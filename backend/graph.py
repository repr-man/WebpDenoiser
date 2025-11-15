import numpy as np
from pathlib import Path
from typing import final, override

from PIL import Image

class Node:
    def __init__(self):
        self.parents: list[Node] = []

    def needsRerun(self, projectRoot: Path, fileName: str) -> bool:
        ...

    def run(self, projectRoot: Path, fileName: str):
        for parent in self.parents:
            if parent.needsRerun(projectRoot, fileName):
                parent.run(projectRoot, fileName)

    def getImage(self, projectRoot: Path, fileName: str) -> Image.Image:
        ...

    def getBytes(self, projectRoot: Path, fileName: str) -> bytes:
        ...


class PngNode(Node):
    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        return False

    @override
    def run(self, projectRoot: Path, fileName: str):
        pass

    @override
    def getImage(self, projectRoot: Path, fileName: str):
        path = projectRoot / "orig" / fileName
        return Image.open(path).convert("RGB")

    @override
    def getBytes(self, projectRoot: Path, fileName: str):
        path = projectRoot / "orig" / fileName
        return path.read_bytes()


@final
class WebpNode(Node):
    def __init__(self):
        super().__init__()
        self.parents = [PngNode()]

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        path = projectRoot / "webp" / fileName.replace(".png", ".webp")
        return not path.exists()

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        path = projectRoot / "webp" / fileName.replace(".png", ".webp")
        png = self.parents[0].getImage(projectRoot, fileName)
        _ = png.convert("RGB").save(path, format="webp")
        
    @override
    def getImage(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "webp" / fileName.replace(".png", ".webp")
        return Image.open(path).convert("RGB")

    @override
    def getBytes(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "webp" / fileName.replace(".png", ".webp")
        return path.read_bytes()


@final
class DeltaNode(Node):
    def __init__(self):
        super().__init__()
        self.parents = [PngNode(), WebpNode()]

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        path = projectRoot / "delta" / fileName.replace(".png", ".bin")
        return not path.exists()
            
    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        png = self.parents[0].getImage(projectRoot, fileName)
        webp = self.parents[1].getImage(projectRoot, fileName)
        pngArr = np.array(png, dtype=np.int16)
        webpArr = np.array(webp, dtype=np.int16)
        delta = pngArr - webpArr
        delta.tofile(projectRoot / "delta" / fileName.replace(".png", ".bin"))
            
    @override
    def getImage(self, projectRoot: Path, fileName: str) -> Image.Image:
        raise NotImplementedError

    @override
    def getBytes(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "delta" / fileName.replace(".png", ".bin")
        return np.fromfile(path, dtype=np.int16).tobytes()


@final
class MaskNode(Node):
    def __init__(self):
        super().__init__()
        self.parents = [DeltaNode(), PngNode()]

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        path = projectRoot / "mask" / fileName
        return not path.exists()

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        png = self.parents[1].getImage(projectRoot, fileName)
        deltaBytes = self.parents[0].getBytes(projectRoot, fileName)
        deltaArr = np.frombuffer(deltaBytes, dtype=np.int16)
        mask = (deltaArr + 128).astype(np.uint8).tobytes()
        path = projectRoot / "mask" / fileName
        Image.frombytes("RGB", png.size, mask).save(path)

    @override
    def getImage(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "mask" / fileName
        return Image.open(path).convert("RGB")

    @override
    def getBytes(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "mask" / fileName
        return path.read_bytes()


@final
class FinalNode(Node):
    def __init__(self):
        super().__init__()
        self.parents = [WebpNode(), DeltaNode()]

    @override
    def needsRerun(self, projectRoot: Path, fileName: str):
        path = projectRoot / "final" / fileName
        return not path.exists()

    @override
    def run(self, projectRoot: Path, fileName: str):
        super().run(projectRoot, fileName)
        webp = self.parents[0].getImage(projectRoot, fileName)
        deltaBytes = self.parents[1].getBytes(projectRoot, fileName)
        webpArr = np.frombuffer(webp.tobytes(), dtype=np.uint8)
        deltaArr = np.frombuffer(deltaBytes, dtype=np.int16)
        finalArr = webpArr + deltaArr
        finalBytes = finalArr.astype(np.uint8).tobytes()
        path = projectRoot / "final" / fileName
        Image.frombytes("RGB", webp.size, finalBytes).save(path)

    @override
    def getImage(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "final" / fileName
        return Image.open(path).convert("RGB")

    @override
    def getBytes(self, projectRoot: Path, fileName: str):
        if self.needsRerun(projectRoot, fileName):
            self.run(projectRoot, fileName)
        path = projectRoot / "final" / fileName
        return path.read_bytes()
