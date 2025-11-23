from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, random_split

from dataset import OurDataset
from graph import DeltaNode

@final
class DoubleConv(nn.Module):
    def __init__(self, inChannels: int, outChannels: int):
        super().__init__()
        self.op = nn.Sequential(
            nn.Conv2d(inChannels, outChannels, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(outChannels, outChannels, 3, padding=1),
            nn.ReLU(inplace=True)
        )

    @override
    def forward(self, x):
        return self.op(x)

@final
class DownSample(nn.Module):
    def __init__(self, inChannels: int, outChannels: int):
        super().__init__()
        self.op = DoubleConv(inChannels, outChannels)
        self.pool = nn.MaxPool2d(2, 2)
        
    @override
    def forward(self, x):
        downSampled = self.op(x)
        pooled = self.pool(downSampled)
        return downSampled, pooled
        
@final
class UpSample(nn.Module):
    def __init__(self, inChannels: int, outChannels: int):
        super().__init__()
        self.transposed = nn.ConvTranspose2d(inChannels, outChannels, 2, 2)
        self.op = DoubleConv(inChannels, outChannels)

    @override
    def forward(self, x1, x2):
        x1 = self.transposed(x1)
        x1 = torch.cat([x1, x2], 1)
        return self.op(x1)

@final
class UNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.down1 = DownSample(3, 64)
        self.down2 = DownSample(64, 128)
        self.down3 = DownSample(128, 256)
        self.down4 = DownSample(256, 512)
        self.bottleneck = DoubleConv(512, 1024)
        self.up1 = UpSample(1024, 512)
        self.up2 = UpSample(512, 256)
        self.up3 = UpSample(256, 128)
        self.up4 = UpSample(128, 64)
        self.final = nn.Conv2d(64, 3, 1)

    @override
    def forward(self, x):
        down1, pool1 = self.down1(x)
        down2, pool2 = self.down2(pool1)
        down3, pool3 = self.down3(pool2)
        down4, pool4 = self.down4(pool3)
        bottleneck = self.bottleneck(pool4)
        up1 = self.up1(bottleneck, down4)
        up2 = self.up2(up1, down3)
        up3 = self.up3(up2, down2)
        up4 = self.up4(up3, down1)
        final = self.final(up4)
        return final

def trainUNet(datasetRoot: Path):
    # Generate all the images needed for training.
    for fileName in (datasetRoot / "orig").iterdir():
        DeltaNode().run(datasetRoot, fileName.name)

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = UNet().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001)

    EPOCHS = 2
    for epoch in tqdm(range(EPOCHS)):
        _ = model.train()
        trainRunningLoss = 0
        for img in tqdm(trainLoader):
            webp: Tensor = img[0].float().to(device)
            delta: Tensor = img[1].float().to(device)
            prediction = model(webp)
            optimizer.zero_grad()
            loss = criterion(prediction, delta)
            trainRunningLoss += loss.item()
            loss.backward()
            optimizer.step()
        trainLoss = trainRunningLoss / (len(trainLoader) + 1)

        model.eval()
        valiRunningLoss = 0
        with torch.no_grad():
            for img in tqdm(valiLoader):
                webp: Tensor = img[0].float().to(device)
                delta: Tensor = img[1].float().to(device)
                prediction = model(webp)
                loss = criterion(prediction, delta)
                valiRunningLoss += loss.item()
            valiLoss = valiRunningLoss / (len(valiLoader) + 1)
        print(f"\nEpoch {epoch + 1} || loss: {trainLoss:.4f} :: validation loss: {valiLoss:.4f}\n")

    torch.save(model.state_dict(), datasetRoot / "model.pt")
