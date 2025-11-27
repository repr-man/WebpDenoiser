from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset, random_split

@final
class DWT(nn.Module):
    def __init__(self):
        super().__init__()
        self.requires_grad = False

    @override
    def forward(self, x: Tensor) -> Tensor:
        x01 = x[:, :, 0::2, :] / 2
        x02 = x[:, :, 1::2, :] / 2
        x1 = x01[:, :, :, 0::2]
        x2 = x02[:, :, :, 0::2]
        x3 = x01[:, :, :, 1::2]
        x4 = x02[:, :, :, 1::2]
        y1 = x1 + x2 + x3 + x4
        y2 = x1 - x2 + x3 - x4
        y3 = x1 + x2 - x3 - x4
        y4 = x1 - x2 - x3 + x4
        return torch.cat([y1, y2, y3, y4], dim=1)

@final
class IDWT(nn.Module):
    def __init__(self):
        super().__init__()
        self.requires_grad = False

    @override
    def forward(self, x: Tensor) -> Tensor:
        r = 2
        in_batch, in_channel, in_height, in_width = x.size()
        out_batch, out_channel, out_height, out_width = in_batch, int(in_channel / (r ** 2)), r * in_height, r * in_width
        x1 = x[:, 0:out_channel, :, :] / 2
        x2 = x[:, out_channel:out_channel * 2, :, :] / 2
        x3 = x[:, out_channel * 2:out_channel * 3, :, :] / 2
        x4 = x[:, out_channel * 3:out_channel * 4, :, :] / 2
        
        h = torch.zeros([out_batch, out_channel, out_height, out_width]).float().to(x.device)
        
        h[:, :, 0::2, 0::2] = x1 + x2 + x3 + x4
        h[:, :, 1::2, 0::2] = x1 - x2 + x3 - x4
        h[:, :, 0::2, 1::2] = x1 + x2 - x3 - x4
        h[:, :, 1::2, 1::2] = x1 - x2 - x3 + x4
        
        return h

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, 1, 1)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1)
        
    def forward(self, x):
        out = self.conv1(x)
        out = self.relu(out)
        out = self.conv2(out)
        return out + x

@final
class DPW_SDNet(nn.Module):
    def __init__(self, inChannels: int = 3, outChannels: int = 3, feat: int = 64, numStages: int = 4):
        super().__init__()
        
        # Pixel Branch
        self.pixel_unshuffle = nn.PixelUnshuffle(2)
        self.pixel_head = nn.Conv2d(inChannels * 4, feat, 3, 1, 1)
        self.pixel_body = nn.Sequential(*[BasicBlock(feat, feat) for _ in range(numStages)])
        self.pixel_tail = nn.Conv2d(feat, outChannels * 4, 3, 1, 1)
        self.pixel_shuffle = nn.PixelShuffle(2)
        
        # Wavelet Branch
        self.dwt = DWT()
        self.wavelet_head = nn.Conv2d(inChannels * 4, feat, 3, 1, 1)
        self.wavelet_body = nn.Sequential(*[BasicBlock(feat, feat) for _ in range(numStages)])
        self.wavelet_tail = nn.Conv2d(feat, outChannels * 4, 3, 1, 1)
        self.idwt = IDWT()
        
        self.fusion = nn.Conv2d(outChannels * 2, outChannels, 1, 1, 0)

    @override
    def forward(self, x):
        # Pixel Branch
        p = self.pixel_unshuffle(x)
        p = self.pixel_head(p)
        p = self.pixel_body(p)
        p = self.pixel_tail(p)
        p_out = self.pixel_shuffle(p)
        
        # Wavelet Branch
        w = self.dwt(x)
        w = self.wavelet_head(w)
        w = self.wavelet_body(w)
        w = self.wavelet_tail(w)
        w_out = self.idwt(w)
        
        # Fusion
        return self.fusion(torch.cat([p_out, w_out], dim=1)) + x


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

def trainDPWSDNet(datasetRoot: Path, usePixelwiseMSE: bool = True):
    # Generate all the images needed for training.
    for fileName in (datasetRoot / "orig").iterdir():
        PngNode().run(datasetRoot, fileName.name)

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = DPW_SDNet().to(device)
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
