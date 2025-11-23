from logging import Logger
import cv2
import numpy as np
from pathlib import Path
from typing import final, override

from PIL import Image
from torch import Tensor
from torchvision.transforms.functional import to_tensor

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
        return projectRoot / self.cacheDirName / fileName.replace(".png", self.fileExt)

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
class WebpNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("webp", ".webp", [PngNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        path = self.getPath(projectRoot, fileName)
        png = self.parents[0].getImage(projectRoot, fileName)
        _ = png.convert("RGB").save(path, format="webp")


@final
class DeltaNode(Node):
    def __init__(self, log: Logger | None = None):
        super().__init__("delta", ".bin", [PngNode(log), WebpNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        png = self.parents[0].getImage(projectRoot, fileName)
        webp = self.parents[1].getImage(projectRoot, fileName)
        pngArr = np.array(png, dtype=np.int16)
        webpArr = np.array(webp, dtype=np.int16)
        delta = pngArr - webpArr
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
        super().__init__("final", ".png", [WebpNode(log), DeltaNode(log)], log)

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        webp = self.parents[0].getImage(projectRoot, fileName)
        deltaBytes = self.parents[1].getBytes(projectRoot, fileName)
        webpArr = np.frombuffer(webp.tobytes(), dtype=np.uint8)
        deltaArr = np.frombuffer(deltaBytes, dtype=np.int16)
        finalArr = webpArr + deltaArr
        finalBytes = finalArr.astype(np.uint8).tobytes()
        path = self.getPath(projectRoot, fileName)
        Image.frombytes("RGB", webp.size, finalBytes).save(path)

@final
class Conv1Node(Node):
    def __init__(self, matrix: np.ndarray, log: Logger | None = None):
        super().__init__("conv1", ".png", [WebpNode(log)], log)
        self.matrix = matrix

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        return True

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        webpPath = self.parents[0].getPath(projectRoot, fileName)
        conv1Path = self.getPath(projectRoot, fileName)
        imageMat = cv2.imread(str(webpPath), cv2.IMREAD_UNCHANGED)
        if imageMat is None:
            raise Exception("Failed to read image")
        transformed = cv2.filter2D(imageMat, -1, self.matrix)
        _ = cv2.imwrite(str(conv1Path), transformed)
