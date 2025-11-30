from pathlib import Path
from typing import final, override
import torch
from torch import Tensor, nn
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset, random_split

### RCAN Implementation
#
#class ChannelAttention(nn.Module):
#    def __init__(self, num_feat, squeeze_factor=16):
#        super(ChannelAttention, self).__init__()
#        self.avg_pool = nn.AdaptiveAvgPool2d(1)
#        self.conv_down = nn.Conv2d(num_feat, num_feat // squeeze_factor, 1, padding=0, bias=True)
#        self.relu = nn.ReLU(inplace=True)
#        self.conv_up = nn.Conv2d(num_feat // squeeze_factor, num_feat, 1, padding=0, bias=True)
#        self.sigmoid = nn.Sigmoid()
#
#    def forward(self, x):
#        y = self.avg_pool(x)
#        y = self.conv_down(y)
#        y = self.relu(y)
#        y = self.conv_up(y)
#        y = self.sigmoid(y)
#        return x * y
#
#class RCAB(nn.Module):
#    def __init__(self, num_feat, squeeze_factor=16):
#        super(RCAB, self).__init__()
#        self.body = nn.Sequential(
#            nn.Conv2d(num_feat, num_feat, 3, 1, 1),
#            nn.ReLU(inplace=True),
#            nn.Conv2d(num_feat, num_feat, 3, 1, 1),
#            ChannelAttention(num_feat, squeeze_factor)
#        )
#
#    def forward(self, x):
#        res = self.body(x)
#        res += x
#        return res
#
#class ResidualGroup(nn.Module):
#    def __init__(self, num_feat, num_rcab, squeeze_factor=16):
#        super(ResidualGroup, self).__init__()
#        modules_body = [
#            RCAB(num_feat, squeeze_factor) \
#            for _ in range(num_rcab)]
#        modules_body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
#        self.body = nn.Sequential(*modules_body)
#
#    def forward(self, x):
#        res = self.body(x)
#        res += x
#        return res
#
#@final
#class RCAN(nn.Module):
#    def __init__(self, num_feat=64, num_rg=4, num_rcab=4, squeeze_factor=16):
#        super(RCAN, self).__init__()
#        self.head = nn.Conv2d(3, num_feat, 3, 1, 1)
#        
#        modules_body = [
#            ResidualGroup(num_feat, num_rcab, squeeze_factor) \
#            for _ in range(num_rg)]
#        modules_body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
#        self.body = nn.Sequential(*modules_body)
#        
#        self.tail = nn.Conv2d(num_feat, 3, 3, 1, 1)
#
#    @override
#    def forward(self, x):
#        x = self.head(x)
#        res = self.body(x)
#        res += x
#        x = self.tail(res)
#        return x
#
#
#@final
#class OurDataset(Dataset[tuple[Tensor, Tensor]]):
#    def __init__(self, root: Path):
#        super().__init__()
#        self.root = root
#        orig = root / "orig"
#        webp = root / "webp"
#        delta = root / "delta"
#        if (
#            not orig.exists()
#            or not webp.exists()
#            or not delta.exists()
#            #or next(orig.iterdir(), None) is None
#            #or next(webp.iterdir(), None) is None
#            #or next(delta.iterdir(), None) is None
#        ):
#            assert False, "CID22 dataset not downloaded."
#        self.filenames = [f.name for f in (root / "orig").iterdir()]
#
#    @override
#    def __getitem__(self, index: int):
#        webp = WebpNode().getTensor(self.root, self.filenames[index])
#
#        png = PngNode().getTensor(self.root, self.filenames[index])
#        return webp, png
#
#        #delta = DeltaNode().getTensor(self.root, self.filenames[index])
#        #return webp, delta
#
#    def __len__(self):
#        return len(self.filenames)
#
#
#class PixelwiseMSE(nn.Module):
#    def __init__(self):
#        super().__init__()
#
#    @override
#    def forward(self, x: Tensor, y: Tensor) -> Tensor:
#        """
#        The layout of the tensors is:
#        [channel, height, width]
#        """
#        return torch.mean(torch.mean((x.squeeze(0) - y.squeeze(0)) ** 2, dim=0))
#
#
#from graph import DeltaNode, PngNode, WebpNode
#
#def trainRCAN(datasetRoot: Path, usePixelwiseMSE: bool = True):
#    # Generate all the images needed for training.
#    for fileName in (datasetRoot / "orig").iterdir():
#        #DeltaNode().run(datasetRoot, fileName.name)
#        PngNode().run(datasetRoot, fileName.name)
#
#    dataset = OurDataset(datasetRoot)
#    gen = torch.Generator().manual_seed(42)
#    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
#    trainLoader = DataLoader(trainData, shuffle=True)
#    valiLoader = DataLoader(valiData, shuffle=True)
#    
#    device = "cuda" if torch.cuda.is_available() else "cpu"
#    model = RCAN().to(device)
#    model = torch.compile(model, fullgraph=True)
#    criterion = PixelwiseMSE() if usePixelwiseMSE else nn.MSELoss()
#    optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001)
#
#    EPOCHS = 5
#    for epoch in tqdm(range(EPOCHS)):
#        _ = model.train()
#        trainRunningLoss = 0
#        for img in tqdm(trainLoader):
#            webp: Tensor = img[0].float().to(device)
#            
#            #delta: Tensor = img[1].float().to(device)
#            png: Tensor = img[1].float().to(device)
#            
#            prediction = model(webp)
#            optimizer.zero_grad()
#
#            #loss = criterion(prediction, delta)
#            loss = criterion(prediction, png)
#
#            trainRunningLoss += loss.item()
#            loss.backward()
#            optimizer.step()
#        trainLoss = trainRunningLoss / (len(trainLoader) + 1)
#
#        model.eval()
#        valiRunningLoss = 0
#        with torch.no_grad():
#            for img in tqdm(valiLoader):
#                webp: Tensor = img[0].float().to(device)
#
#                #delta: Tensor = img[1].float().to(device)
#                png: Tensor = img[1].float().to(device)
#
#                prediction = model(webp)
#
#                #loss = criterion(prediction, delta)
#                loss = criterion(prediction, png)
#
#                valiRunningLoss += loss.item()
#            valiLoss = valiRunningLoss / (len(valiLoader) + 1)
#        print(f"\nEpoch {epoch + 1} || loss: {trainLoss:.4f} :: validation loss: {valiLoss:.4f}\n")
#
#    torch.save(model.state_dict(), datasetRoot / "model.pt")






class ChannelAttention(nn.Module):
    """
    Implements the Channel Attention mechanism (Squeeze-and-Excitation).
    """
    def __init__(self, num_feat, squeeze_factor=16):
        super().__init__()
        # Squeeze operation: Global Average Pooling (GAP)
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        # Excitation operation: Two fully connected layers (implemented as 1x1 convolutions)
        self.conv_down = nn.Conv2d(num_feat, num_feat // squeeze_factor, 1, padding=0, bias=True)
        self.relu = nn.ReLU(inplace=True)
        self.conv_up = nn.Conv2d(num_feat // squeeze_factor, num_feat, 1, padding=0, bias=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        y = self.avg_pool(x)
        y = self.conv_down(y)
        y = self.relu(y)
        y = self.conv_up(y)
        y = self.sigmoid(y)
        # Scale operation: Element-wise multiplication of the input features by the learned weights
        return x * y

class RCAB(nn.Module):
    """
    Residual Channel Attention Block.
    """
    def __init__(self, num_feat, squeeze_factor=16):
        super().__init__()
        self.body = nn.Sequential(
            # Conv 1
            nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True),
            # ReLU after the first convolution (standard practice for EDSR/RCAN style)
            nn.ReLU(inplace=True),
            # Conv 2
            nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True),
            # Channel Attention Block
            ChannelAttention(num_feat, squeeze_factor)
        )
        # Initialize the last convolution layer of the body to zero-out the residual
        # This helps stabilize training initially. (Optional, but recommended)
        # nn.init.constant_(self.body[-2].weight, 0)
        # nn.init.constant_(self.body[-2].bias, 0)

    def forward(self, x):
        # Local Residual Learning: Output = Input + Body(Input)
        return self.body(x) + x

class ResidualGroup(nn.Module):
    """
    Residual Group containing multiple RCABs and a final skip connection.
    """
    def __init__(self, num_feat, num_rcab, squeeze_factor=16):
        super().__init__()
        modules_body = [
            RCAB(num_feat, squeeze_factor) for _ in range(num_rcab)
        ]
        # Final convolution within the Residual Group (Global Residual Learning within the Group)
        modules_body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True))
        self.body = nn.Sequential(*modules_body)

    def forward(self, x):
        # Global Residual Learning for the Group: Output = Input + Body(Input)
        return self.body(x) + x

class RCAN_Deblocking(nn.Module):
    """
    RCAN architecture modified for 1x Image Deblocking (Residual Learning).
    """
    def __init__(self, num_feat=64, num_rg=4, num_rcab=4, squeeze_factor=16):
        super().__init__()
        
        # 1. Shallow Feature Extraction (Head)
        # Input: 3 channels (RGB); Output: num_feat channels
        self.head = nn.Conv2d(3, num_feat, 3, 1, 1, bias=True)
        
        # 2. Deep Feature Extraction (Body - RIR)
        modules_body = [
            ResidualGroup(num_feat, num_rcab, squeeze_factor) for _ in range(num_rg)
        ]
        # Final convolution of the main body
        modules_body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1, bias=True))
        self.body = nn.Sequential(*modules_body)
        
        # 3. Reconstruction (Tail)
        # Output: 3 channels (The predicted residual R)
        self.tail = nn.Conv2d(num_feat, 3, 3, 1, 1, bias=True)
        
        # Optional: Initialize final layers to zero for stable residual training (DnCNN/EDSR practice)
        # nn.init.constant_(self.body[-1].weight, 0)
        # nn.init.constant_(self.body[-1].bias, 0)
        # nn.init.constant_(self.tail.weight, 0)
        # nn.init.constant_(self.tail.bias, 0)

    def forward(self, x_compressed):
        # Store initial compressed input for the final skip connection
        x_input = x_compressed
        
        # 1. Shallow Feature Extraction
        x = self.head(x_compressed)
        
        # 2. Deep Feature Extraction
        res_body = self.body(x)
        
        # Global Residual Learning across the RGs: x_shallow + res_body
        res_body += x
        
        # 3. Reconstruction (Predict the Residual R)
        # The output of the tail is the predicted artifact pattern (R)
        residual_r = self.tail(res_body)
        
        # Final Reconstruction (Global Skip Connection): Y_hat = X + R
        y_restored = x_input + residual_r
        
        return y_restored


@final
class OurDataset(Dataset[tuple[Tensor, Tensor]]):
    def __init__(self, root: Path):
        super().__init__()
        self.root = root
        orig = root / "orig"
        webp = root / "webp"
        if (
            not orig.exists()
            or not webp.exists()
        ):
            assert False, "CID22 dataset not downloaded."
        self.filenames = [f.name for f in (root / "orig").iterdir()]

    @override
    def __getitem__(self, index: int):
        webpPath = Path('/') / 'content' / 'sample_data' / 'webp' / self.filenames[index].replace('.png', '.webp')
        pngPath = Path('/') / 'content' / 'sample_data' / 'orig' / self.filenames[index]
        webp = to_tensor(Image.open(webpPath).convert("RGB"))
        png = to_tensor(Image.open(pngPath).convert("RGB"))
        return webp, png

    def __len__(self):
        return len(self.filenames)


class PixelwiseMAE(nn.Module):
    def __init__(self):
        super().__init__()

    @override
    def forward(self, x: Tensor, y: Tensor) -> Tensor:
        """
        The layout of the tensors is:
        [channel, height, width]
        """
        return torch.mean(torch.abs(x.squeeze(0) - y.squeeze(0)), dim=0)
        #return torch.mean(torch.mean((x.squeeze(0) - y.squeeze(0)) ** 2, dim=0))


def trainRCAN(datasetRoot: Path, usePixelwiseMAE: bool = True):

    dataset = OurDataset(datasetRoot)
    gen = torch.Generator().manual_seed(42)
    trainData, valiData = random_split(dataset, [0.8, 0.2], generator=gen)
    trainLoader = DataLoader(trainData, shuffle=True)
    valiLoader = DataLoader(valiData, shuffle=True)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = RCAN_Deblocking().to(device)
    model = torch.compile(model, fullgraph=True)
    criterion = PixelwiseMAE() if usePixelwiseMAE else nn.L1Loss()
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
