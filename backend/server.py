import numpy as np
from pathlib import Path
from flask import Flask, Request, request, jsonify
from flask_cors import CORS

from graph import FinalNode, MaskNode, PngNode, DPWSDNetComputationNode, DPWSDNetErrorNode, WebpNode, Conv1Node

flaskServer = Flask(__name__)
_ = CORS(flaskServer)
log = flaskServer.logger

def getProjectParts(request: Request):
    """
    A helper function that extracts the project root and file name from a
    JSON request.

    The app only identifies an image by its project root and file name.  This
    makes some of the abstractions simpler because the app doesn't need to
    manipulate paths; it only needs send requests for the type of image it needs.
    """
    body = request.get_json()
    projectRoot: str = body["projectRoot"]
    fileName: str = body["fileName"]
    return Path(projectRoot), fileName

@flaskServer.route("/get-carousel-pngs", methods=["POST"])
def requestGetCarouselPngs():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir"
    }
    Returns a JSON array of the form:
    [
        "filename.png", "other.png", ...
    ]
    where each filename corresponds to the path
    '/path/to/root/dir/orig/filename.png'.
    """
    body = request.get_json()
    projectRoot: str = body["projectRoot"]
    origPngPath = Path(projectRoot) / "orig"
    
    pngs = [p.name
        for p in origPngPath.iterdir()
        if p.is_file() and p.suffix.lower() == ".png"
    ]
    return jsonify(pngs)


@flaskServer.route("/get-image-orig", methods=["POST"])
def requestGetImage():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/orig/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return PngNode().getBytes(root, fileName)


@flaskServer.route("/get-image-webp", methods=["POST"])
def requestGetWebp():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/webp/filename.webp'.
    """
    root, fileName = getProjectParts(request)
    return WebpNode().getBytes(root, fileName)


@flaskServer.route("/get-image-mask", methods=["POST"])
def requestGetMask():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/mask/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return MaskNode().getBytes(root, fileName)


@flaskServer.route("/get-image-final", methods=["POST"])
def requestGetFinal():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/final/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return FinalNode().getBytes(root, fileName)

@flaskServer.route("/get-image-conv1", methods=["POST"])
def requestGetConv1():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/conv1/filename.png'.
    """
    root, fileName = getProjectParts(request)
    matrix = np.array(request.get_json()["matrixValues"])
    return Conv1Node(matrix).getBytes(root, fileName)

@flaskServer.route("/get-image-dpw_sdnet", methods=["POST"])
def requestGetDPWSDNet():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/dpwsdnet/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return DPWSDNetComputationNode().getBytes(root, fileName)

@flaskServer.route("/get-image-dpw_sdnet_err", methods=["POST"])
def requestGetDPWSDNetErr():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/dpwsdnet_err/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return DPWSDNetErrorNode().getBytes(root, fileName)
