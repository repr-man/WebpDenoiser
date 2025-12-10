import numpy as np
from pathlib import Path
from flask import Flask, Request, request, jsonify
from flask_cors import CORS

from graph import FinalNode, MaskNode, PngNode, UNetComputationNode, ErrorNode, JpegNode, Conv1Node, SobelYNode, SobelCbNode, SobelCrNode, SobelSumNode, SobelRNode, SobelGNode, SobelBNode, SobelRGBSumNode, WeightedBlurNode, SobelMaskNode, WeightedMaskNode

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
    origPngPath = Path(projectRoot) / "vali" / "orig"
    
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


@flaskServer.route("/get-image-jpeg", methods=["POST"])
def requestGetJpeg():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/jpeg/filename.jpg'.
    """
    root, fileName = getProjectParts(request)
    return JpegNode().getBytes(root, fileName)


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

@flaskServer.route("/get-image-unet", methods=["POST"])
def requestGetUnet():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/unet/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return UNetComputationNode().getBytes(root, fileName)

@flaskServer.route("/get-image-error", methods=["POST"])
def requestGetError():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/error/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return ErrorNode(log).getBytes(root, fileName)
    
@flaskServer.route("/get-image-sobel-y", methods=["POST"])
def requestGetSobelY():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_y/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelYNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-cb", methods=["POST"])
def requestGetSobelCb():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_cb/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelCbNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-cr", methods=["POST"])
def requestGetSobelCr():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_cr/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelCrNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-sum", methods=["POST"])
def requestGetSobelSum():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_sum/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelSumNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-r", methods=["POST"])
def requestGetSobelR():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_r/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelRNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-g", methods=["POST"])
def requestGetSobelG():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_g/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelGNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-b", methods=["POST"])
def requestGetSobelB():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_b/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelBNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-rgb-sum", methods=["POST"])
def requestGetSobelRGBSum():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_rgb_sum/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelRGBSumNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-weighted-blur", methods=["POST"])
def requestGetWeightedBlur():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/weighted_blur/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return WeightedBlurNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-sobel-mask", methods=["POST"])
def requestGetSobelMask():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/sobel_mask/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return SobelMaskNode(log).getBytes(root, fileName)

@flaskServer.route("/get-image-weighted-mask", methods=["POST"])
def requestGetWeightedMask():
    """
    Receives a JSON payload of the form:
    {
        "projectRoot": "/path/to/root/dir",
        "fileName": "filename.png"
    }
    Returns the contents of the file at
    '/path/to/root/dir/weighted_mask/filename.png'.
    """
    root, fileName = getProjectParts(request)
    return WeightedMaskNode(log).getBytes(root, fileName)
