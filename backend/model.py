from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset, random_split

@final
class ProjectionUnit(nn.Module):
    def __init__(self, inChannels: int, outChannels: int):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(inChannels, outChannels, kernel_size=3, padding=1),
            nn.PReLU()
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(outChannels, inChannels, kernel_size=3, padding=1),
            nn.PReLU()
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(inChannels, outChannels, kernel_size=3, padding=1),
            nn.PReLU()
        )

    @override
    def forward(self, x):
        h0 = self.conv1(x)
        l0 = self.conv2(h0)
        e = x - l0
        h1 = h0 + self.conv3(e)
        return h1

@final
class RBDN(nn.Module):
    def __init__(self, inChannels: int = 3, outChannels: int = 3, feat: int = 64, numStages: int = 4):
        super().__init__()
        self.feat0 = nn.Conv2d(inChannels, feat, kernel_size=3, padding=1)
        self.feat1 = nn.Conv2d(feat, feat, kernel_size=1, padding=0)
        
        self.stages = nn.ModuleList()
        for _ in range(numStages):
            self.stages.append(ProjectionUnit(feat, feat))
            
        self.bottleneck = nn.Conv2d(feat * numStages, feat, kernel_size=1, padding=0)
        self.output = nn.Conv2d(feat, outChannels, kernel_size=3, padding=1)
        
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    @override
    def forward(self, x):
        f0 = self.feat0(x)
        f = self.feat1(f0)
        
        res = []
        for stage in self.stages:
            f = stage(f)
            res.append(f)
            
        out = torch.cat(res, dim=1)
        out = self.bottleneck(out)
        out = self.output(out)
        
        return out + x


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

def trainRBDN(datasetRoot: Path, usePixelwiseMSE: bool = True):
    # Generate all the images needed for training.
    for fileName in (datasetRoot / "orig").iterdir():
        PngNode().run(datasetRoot, fileName.name)

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = RBDN().to(device)
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
