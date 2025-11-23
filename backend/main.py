from pathlib import Path
from typing_extensions import Annotated
import typer
from dataset import loadDataset_CID22, loadDataset_GooglePng
from model import trainUNet
from server import flaskServer

app = typer.Typer()

@app.command()
def dataset(datasetroot: Annotated[str | None, typer.Argument()] = None):
    if datasetroot is None:
        print("Where do you want to store the dataset?")
        print("Enter path > ", end="")
        root = Path(input()).resolve()
    else:
        root = Path(datasetroot).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "orig").mkdir(parents=True, exist_ok=True)
    (root / "webp").mkdir(parents=True, exist_ok=True)
    (root / "delta").mkdir(parents=True, exist_ok=True)
    (root / "mask").mkdir(parents=True, exist_ok=True)
    (root / "final").mkdir(parents=True, exist_ok=True)
    (root / "conv1").mkdir(parents=True, exist_ok=True)
    (root / "unet").mkdir(parents=True, exist_ok=True)
    (root / "unet_vis").mkdir(parents=True, exist_ok=True)
    (root / "reconstructed").mkdir(parents=True, exist_ok=True)

    # Download the dataset.
    #loadDataset_GooglePng(root)
    loadDataset_CID22(root)


@app.command()
def server():
    flaskServer.run(debug=True, threaded=False, processes=1)

@app.command()
def train(datasetroot: Annotated[Path | None, typer.Argument()] = None):
    if datasetroot is None:
        print("Where is the dataset?")
        print("Enter path > ", end="")
        root = Path(input()).resolve()
    else:
        root = Path(datasetroot).resolve()

    # TODO: Train the model.  When we get to this part, we will want to put the
    # code in a file called `train.py` or `model.py` or something like that.
    trainUNet(root)

if __name__ == "__main__":
    app()
