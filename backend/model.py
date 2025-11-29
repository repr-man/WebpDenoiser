from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset, random_split

@final
class LightMUNet(nn.Module):
    def __init__(self):
        super().__init__()
        raise NotImplementedError

    @override
    def forward(self, x: Tensor) -> Tensor:
        """
        The layout of the tensors is:
        [channel, height, width]
        """
        raise NotImplementedError

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

def trainLightMUNet(datasetRoot: Path, usePixelwiseMSE: bool = True):
    # Generate all the images needed for training.
    for fileName in (datasetRoot / "orig").iterdir():
        PngNode().run(datasetRoot, fileName.name)

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = LightMUNet().to(device)
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
