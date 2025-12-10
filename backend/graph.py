from logging import Logger
import cv2
import numpy as np
from pathlib import Path
from typing import final, override

from PIL import Image
from torch import Tensor
import torch
from torchvision.transforms.functional import to_pil_image, to_tensor

class Node:
    def __init__(self, cacheDirName: str, fileExt: str, parents: list["Node"], log: Logger | None = None):
        self.parents: list[Node] = parents
        self.cacheDirName: str = cacheDirName
        self.fileExt: str = fileExt
        self._log: Logger | None = log

    def log(self, message: str):
        """
        Use this method for debugging.  It has to exist because Flask is stupid
        and doesn't let you `print` things.
        """
        if self._log is not None:
            self._log.warning(message)

    def getPath(self, projectRoot: Path, fileName: str) -> Path:
        return projectRoot / "vali" / self.cacheDirName / fileName.replace(".png", self.fileExt)

    def needsRerun(self, projectRoot: Path, fileName: str) -> bool:
        return not self.getPath(projectRoot, fileName).exists()

    def run(self, projectRoot: Path, fileName: str):
        for parent in self.parents:
            if parent.needsRerun(projectRoot, fileName):
                parent.run(projectRoot, fileName)

    def getImage(self, projectRoot: Path, fileName: str) -> Image.Image:
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        return Image.open(self.getPath(projectRoot, fileName)).convert("RGB")

    def getBytes(self, projectRoot: Path, fileName: str) -> bytes:
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        return self.getPath(projectRoot, fileName).read_bytes()
    
    def getTensor(self, projectRoot: Path, fileName: str) -> Tensor:
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        return to_tensor(Image.open(self.getPath(projectRoot, fileName)).convert("RGB"))


class PngNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("orig", ".png", [], log)

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        return False

    @override
    def run(self, projectRoot: Path, fileName: str):
        pass


@final
class JpegNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("jpeg", ".jpg", [PngNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        path = self.getPath(projectRoot, fileName)
        png = self.parents[0].getImage(projectRoot, fileName)
        _ = png.convert("RGB").save(path, format="jpeg")


@final
class DeltaNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("delta", ".bin", [PngNode(log), JpegNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        png = self.parents[0].getImage(projectRoot, fileName)
        jpeg = self.parents[1].getImage(projectRoot, fileName)
        pngArr = np.array(png, dtype=np.int16)
        jpegArr = np.array(jpeg, dtype=np.int16)
        delta = pngArr - jpegArr
        delta = delta.reshape(png.size[0], png.size[1], 3)
        delta.tofile(self.getPath(projectRoot, fileName))
            
    @override
    def getImage(self, projectRoot: Path, fileName: str) -> Image.Image:
        raise NotImplementedError

    @override
    def getTensor(self, projectRoot: Path, fileName: str) -> Tensor:
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        delta = np.fromfile(self.getPath(projectRoot, fileName), dtype=np.int16)
        image = self.parents[1].getImage(projectRoot, fileName)
        delta = delta.reshape(image.height, image.width, 3)
        return to_tensor(delta)


@final
class MaskNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("mask", ".png", [DeltaNode(log), PngNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        png = self.parents[1].getImage(projectRoot, fileName)
        deltaBytes = self.parents[0].getBytes(projectRoot, fileName)
        deltaArr = np.frombuffer(deltaBytes, dtype=np.int16)
        mask = (deltaArr + 128).astype(np.uint8).tobytes()
        path = self.getPath(projectRoot, fileName)
        Image.frombytes("RGB", png.size, mask).save(path)


@final
class FinalNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("final", ".png", [JpegNode(log), DeltaNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        jpeg = self.parents[0].getImage(projectRoot, fileName)
        deltaBytes = self.parents[1].getBytes(projectRoot, fileName)
        jpegArr = np.frombuffer(jpeg.tobytes(), dtype=np.uint8)
        deltaArr = np.frombuffer(deltaBytes, dtype=np.int16)
        finalArr = jpegArr + deltaArr
        finalBytes = finalArr.astype(np.uint8).tobytes()
        path = self.getPath(projectRoot, fileName)
        Image.frombytes("RGB", jpeg.size, finalBytes).save(path)

@final
class Conv1Node(Node):
    def __init__(self, matrix: np.ndarray, log: Logger | None = None):
        super().__init__("conv1", ".png", [JpegNode(log)], log)
        self.matrix = matrix

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        return True

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        jpegPath = self.parents[0].getPath(projectRoot, fileName)
        conv1Path = self.getPath(projectRoot, fileName)
        imageMat = cv2.imread(str(jpegPath), cv2.IMREAD_UNCHANGED)
        if imageMat is None:
            raise Exception("Failed to read image")
        transformed = cv2.filter2D(imageMat, -1, self.matrix)
        _ = cv2.imwrite(str(conv1Path), transformed)

# This needs to be here to avoid circular imports.
from model import UNet

@final
class UNetComputationNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("unet", ".png", [JpegNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        modelPath = projectRoot / "model.pt"
        outputPath = self.getPath(projectRoot, fileName)
        jpeg = self.parents[0].getTensor(projectRoot, fileName)
        model = UNet().to(device)

        state_dict = torch.load(modelPath, map_location=torch.device(device))
        new_state_dict = {}
        for k, v in state_dict.items():
            # Remove the "_orig_mod." prefix
            new_key = k.replace("_orig_mod.", "")
            new_state_dict[new_key] = v

        _ = model.load_state_dict(new_state_dict)
        #_ = model.load_state_dict(torch.load(modelPath, map_location=torch.device(device)))
        jpeg = jpeg.unsqueeze(0)
        newImgTensor = model(jpeg).squeeze(0)
        pilImg = to_pil_image(newImgTensor)
        pilImg.save(outputPath, format="png")


@final
class ErrorNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("error", ".png", [JpegNode(log), UNetComputationNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        unet = self.parents[1].getTensor(projectRoot, fileName)
        jpeg = self.parents[0].getTensor(projectRoot, fileName)
        for i in range(unet.shape[2]):
            for j in range(unet.shape[1]):
                if i == 0 and j == 0:
                    self.log(unet[:, j, i])
                    self.log(jpeg[:, j, i])
                rSame = unet[0, j, i].item() == jpeg[0, j, i].item()
                gSame = unet[1, j, i].item() == jpeg[1, j, i].item()
                bSame = unet[2, j, i].item() == jpeg[2, j, i].item()
                if (rSame and gSame and bSame):
                    unet[0, j, i] = 0
                    unet[1, j, i] = 0
                    unet[2, j, i] = 0
        pilImg = to_pil_image(unet)
        pilImg.save(outputPath, format="png")


import torch.nn.functional as F

class SobelNode(Node):
    def __init__(self, channel: int, cacheDirName: str, log: Logger | None = None):
        super().__init__(cacheDirName, ".png", [JpegNode(log)], log)
        self.channel = channel

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        jpegPath = self.parents[0].getPath(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        
        # Load image and convert to YCbCr
        img = Image.open(jpegPath).convert("YCbCr")
        # Extract specific channel
        channel_img = img.split()[self.channel]
        # Convert to tensor and add batch/channel dims: [1, 1, H, W]
        tensor = to_tensor(channel_img).unsqueeze(0)
        
        # Define Sobel kernels
        sobel_x = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]).view(1, 1, 3, 3)
        sobel_y = torch.tensor([[-1., -2., -1.], [0., 0., 0.], [1., 2., 1.]]).view(1, 1, 3, 3)
        
        # Apply filters
        grad_x = F.conv2d(tensor, sobel_x, padding=1)
        grad_y = F.conv2d(tensor, sobel_y, padding=1)
        
        # Calculate magnitude
        magnitude = torch.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize to 0-1 range for saving
        magnitude = magnitude / magnitude.max() if magnitude.max() > 0 else magnitude
        
        pilImg = to_pil_image(magnitude.squeeze(0))
        pilImg.save(outputPath, format="png")

@final
class SobelYNode(SobelNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(0, "sobel_y", log)

@final
class SobelCbNode(SobelNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(1, "sobel_cb", log)

@final
class SobelCrNode(SobelNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(2, "sobel_cr", log)

@final
class SobelSumNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("sobel_sum", ".png", [SobelYNode(log), SobelCbNode(log), SobelCrNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        
        y = self.parents[0].getTensor(projectRoot, fileName)
        cb = self.parents[1].getTensor(projectRoot, fileName)
        cr = self.parents[2].getTensor(projectRoot, fileName)
        
        # Sum the tensors
        total = y + cb + cr
        
        # Clamp to valid range [0, 1]
        total = torch.clamp(total, 0, 1)
        
        pilImg = to_pil_image(total)
        pilImg.save(outputPath, format="png")


class SobelRGBNode(Node):
    def __init__(self, channel: int, cacheDirName: str, log: Logger | None = None):
        super().__init__(cacheDirName, ".png", [JpegNode(log)], log)
        self.channel = channel

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        jpegPath = self.parents[0].getPath(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        
        # Load image and keep as RGB
        img = Image.open(jpegPath).convert("RGB")
        # Extract specific channel
        channel_img = img.split()[self.channel]
        # Convert to tensor and add batch/channel dims: [1, 1, H, W]
        tensor = to_tensor(channel_img).unsqueeze(0)
        
        # Define Sobel kernels
        sobel_x = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]).view(1, 1, 3, 3)
        sobel_y = torch.tensor([[-1., -2., -1.], [0., 0., 0.], [1., 2., 1.]]).view(1, 1, 3, 3)
        
        # Apply filters
        grad_x = F.conv2d(tensor, sobel_x, padding=1)
        grad_y = F.conv2d(tensor, sobel_y, padding=1)
        
        # Calculate magnitude
        magnitude = torch.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize to 0-1 range for saving
        magnitude = magnitude / magnitude.max() if magnitude.max() > 0 else magnitude
        
        pilImg = to_pil_image(magnitude.squeeze(0))
        pilImg.save(outputPath, format="png")

@final
class SobelRNode(SobelRGBNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(0, "sobel_r", log)

@final
class SobelGNode(SobelRGBNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(1, "sobel_g", log)

@final
class SobelBNode(SobelRGBNode):
    def __init__(self, log: Logger | None = None):
        super().__init__(2, "sobel_b", log)

@final
class SobelRGBSumNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("sobel_rgb_sum", ".png", [SobelRNode(log), SobelGNode(log), SobelBNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        
        r = self.parents[0].getTensor(projectRoot, fileName)
        g = self.parents[1].getTensor(projectRoot, fileName)
        b = self.parents[2].getTensor(projectRoot, fileName)
        
        # Sum the tensors
        total = r + g + b
        
        # Clamp to valid range [0, 1]
        total = torch.clamp(total, 0, 1)
        
        pilImg = to_pil_image(total)
        pilImg.save(outputPath, format="png")


from torchvision.transforms.functional import gaussian_blur

@final
class WeightedBlurNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("weighted_blur", ".png", [JpegNode(log), SobelSumNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        outputPath = self.getPath(projectRoot, fileName)
        
        jpeg = self.parents[0].getTensor(projectRoot, fileName)
        sobel_sum = self.parents[1].getTensor(projectRoot, fileName)
        
        mask = 1.0 - sobel_sum
        
        blurred = gaussian_blur(jpeg, kernel_size=5)
        
        result = blurred * mask + jpeg * (1.0 - mask)
        
        pilImg = to_pil_image(result)
        pilImg.save(outputPath, format="png")
