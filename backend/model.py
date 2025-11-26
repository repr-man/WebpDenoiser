from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset, random_split

@final
class ResBlock(nn.Module):
    def __init__(self, inChannels: int, outChannels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(inChannels, outChannels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(outChannels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(outChannels, outChannels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(outChannels)
        
        self.downsample = None
        if stride != 1 or inChannels != outChannels:
            self.downsample = nn.Sequential(
                nn.Conv2d(inChannels, outChannels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(outChannels)
            )

    @override
    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
            
        out += identity
        out = self.relu(out)
        return out

@final
class ResNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.inChannels = 64
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        self.layer1 = self._make_layer(64, 2, stride=1)
        self.layer2 = self._make_layer(128, 2, stride=2)
        self.layer3 = self._make_layer(256, 2, stride=2)
        self.layer4 = self._make_layer(512, 2, stride=2)
        
        self.up1 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.up2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.up3 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.up4 = nn.ConvTranspose2d(64, 64, 2, stride=2)
        self.up5 = nn.ConvTranspose2d(64, 3, 2, stride=2)
        self.final = nn.Conv2d(3, 3, kernel_size=1)

    def _make_layer(self, outChannels: int, blocks: int, stride: int = 1):
        layers = []
        layers.append(ResBlock(self.inChannels, outChannels, stride))
        self.inChannels = outChannels
        for _ in range(1, blocks):
            layers.append(ResBlock(outChannels, outChannels))
        return nn.Sequential(*layers)

    @override
    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.up1(x)
        x = self.up2(x)
        x = self.up3(x)
        x = self.up4(x)
        x = self.up5(x)
        
        x = self.final(x)
        return x


@final
class OurDataset(Dataset[tuple[Tensor, Tensor]]):
    def __init__(self, root: Path):
        super().__init__()
        self.root = root
        orig = root / "orig"
        webp = root / "webp"
        delta = root / "delta"
        if (
            not orig.exists()
            or not webp.exists()
            or not delta.exists()
        ):
            assert False, "CID22 dataset not downloaded."
        self.filenames = [f.name for f in (root / "orig").iterdir()]

    @override
    def __getitem__(self, index: int):
        webp = WebpNode().getTensor(self.root, self.filenames[index])
        png = PngNode().getTensor(self.root, self.filenames[index])
        return webp, png

    def __len__(self):
        return len(self.filenames)


class PixelwiseMSE(nn.Module):
    def __init__(self):
        super().__init__()

    @override
    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        """
        The layout of the tensors is:
        [channel, height, width]
        """
        return torch.mean(torch.mean((x.squeeze(0) - y.squeeze(0)) ** 2, dim=0))


from graph import DeltaNode, PngNode, WebpNode

def trainResNet(datasetRoot: Path, usePixelwiseMSE: bool = True):
    # Generate all the images needed for training.
    for fileName in (datasetRoot / "orig").iterdir():
        PngNode().run(datasetRoot, fileName.name)

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ResNet().to(device)
    model = torch.compile(model, fullgraph=True)
    criterion = PixelwiseMSE() if usePixelwiseMSE else nn.MSELoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001)

    EPOCHS = 5
    for epoch in tqdm(range(EPOCHS)):
        _ = model.train()
        trainRunningLoss = 0
        for img in tqdm(trainLoader):
            webp: Tensor = img[0].float().to(device)
            png: Tensor = img[1].float().to(device)
            prediction = model(webp)
            optimizer.zero_grad()
            loss = criterion(prediction, png)
            trainRunningLoss += loss.item()
            loss.backward()
            optimizer.step()
        trainLoss = trainRunningLoss / (len(trainLoader) + 1)

        model.eval()
        valiRunningLoss = 0
        with torch.no_grad():
            for img in tqdm(valiLoader):
                webp: Tensor = img[0].float().to(device)
                png: Tensor = img[1].float().to(device)
                prediction = model(webp)
                loss = criterion(prediction, png)
                valiRunningLoss += loss.item()
            valiLoss = valiRunningLoss / (len(valiLoader) + 1)
        print(f"\nEpoch {epoch + 1} || loss: {trainLoss:.4f} :: validation loss: {valiLoss:.4f}\n")

    torch.save(model.state_dict(), datasetRoot / "model.pt")
