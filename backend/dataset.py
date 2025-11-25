from typing import final, override
from huggingface_hub import snapshot_download
import numpy as np
from pathlib import Path
import requests
import zipfile
from os import rename, remove
import shutil
from torch import Tensor
from torch.utils.data import Dataset
from torchvision.io.image import decode_image

from graph import DeltaNode, WebpNode
from tqdm import tqdm

def loadDataset_GooglePng(root: Path):
    orig = root / "orig"
    _ = snapshot_download(
        repo_id="niabalaji123/google_png",
        repo_type="dataset",
        revision="main",
        allow_patterns=["*.png"],
        local_dir=f"{orig}"
    )

    # This dataset has duplicates, so we need to remove them.
    # 3d pie chart
    (orig / "downloaded_image_png1109.png").unlink()
    (orig / "downloaded_image_png1113.png").unlink()
    (orig / "downloaded_image_png1171.png").unlink()
    (orig / "downloaded_image_png1195.png").unlink()
    # Byju's
    (orig / "downloaded_image_png1148.png").unlink()
    # Triangular prism
    (orig / "downloaded_image_png1262.png").unlink()
    # Billiards
    (orig / "downloaded_image_png143.png").unlink()
    (orig / "downloaded_image_png1193.png").unlink()
    # Tangent and Normal Line
    (orig / "downloaded_image_png1196.png").unlink()
    # Red Light Reflected
    (orig / "downloaded_image_png1151.png").unlink()
    (orig / "downloaded_image_png1165.png").unlink()
    (orig / "downloaded_image_png1166.png").unlink()
    (orig / "downloaded_image_png1242.png").unlink()
    # Flowery dots
    (orig / "downloaded_image_png1128.png").unlink()
    (orig / "downloaded_image_png1261.png").unlink()
    # In-Center Inscribed Circle
    (orig / "downloaded_image_png1288.png").unlink()
    (orig / "downloaded_image_png1291.png").unlink()
    # Radius cx, cy
    (orig / "downloaded_image_png1271.png").unlink()
    # Yoga Mats
    (orig / "downloaded_image_png1230.png").unlink()
    # daa
    (orig / "downloaded_image_png125.png").unlink()
    # Ruler
    (orig / "downloaded_image_png1188.png").unlink()
    # Measuring Leaf
    (orig / "downloaded_image_png1208.png").unlink()
    (orig / "downloaded_image_png1280.png").unlink()
    # Colorful things with faces
    (orig / "downloaded_image_png1134.png").unlink()
    # DOt
    (orig / "downloaded_image_png1217.png").unlink()
    # Cloth thing
    (orig / "downloaded_image_png1198.png").unlink()
    # Many charts
    (orig / "downloaded_image_png1269.png").unlink()
    # Consistent Voters
    (orig / "downloaded_image_png1235.png").unlink()
    # AF AB and BF
    (orig / "downloaded_image_png197.png").unlink()
    (orig / "downloaded_image_png1160.png").unlink()
    (orig / "downloaded_image_png1206.png").unlink()
    # Green Triangle
    (orig / "downloaded_image_png1169.png").unlink()
    # Equidistant
    (orig / "downloaded_image_png1133.png").unlink()
    # Triangle Comparison
    (orig / "downloaded_image_png164.png").unlink()



def loadDataset_CID22(root: Path):
    orig = root / "orig"
    tmpzip = orig / "CID22.zip"
    with open(tmpzip, "wb") as f:
        print("Downloading CID22 dataset... (will take a while)")
        res = requests.get(
            "https://cloudinary-marketing-res.cloudinary.com/raw/upload/v1682032119/CID22.zip",
            stream=True,
        )
        for chunk in tqdm(res.iter_content(chunk_size=1024)):
            _ = f.write(chunk)
    with zipfile.ZipFile(tmpzip, "r") as zipObj:
        print("Extracting CID22 dataset...")
        zipObj.extractall(path=orig)
    for file in tqdm((orig / "CID22" / "original").iterdir()):
        rename(file, orig / file.name)
    remove(tmpzip)
    remove(orig / "LICENSE")
    shutil.rmtree(orig / "CID22")

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
            or next(orig.iterdir(), None) is None
            or next(webp.iterdir(), None) is None
            or next(delta.iterdir(), None) is None
        ):
            assert False, "CID22 dataset not downloaded."
        self.filenames = [f.name for f in (root / "orig").iterdir()]

    @override
    def __getitem__(self, index: int):
        webp = WebpNode().getTensor(self.root, self.filenames[index])
        delta = DeltaNode().getTensor(self.root, self.filenames[index])
        return webp, delta

    def __len__(self):
        return len(self.filenames)
