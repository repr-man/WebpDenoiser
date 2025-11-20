# Backend

This is where the magic happens.

## Wow! There aren't as many files as in the frontend!

Nope.  Just these ones:

- `main.py` - Contains the Typer CLI app.  This is the entry point for all of the
              functionality of the project.
- `dataset.py` - Contains all the functions used to download images for the dataset.
- `train.py` or `model.py` - TODO: Will contain the code for training the model.
- `server.py` - Contains the Flask server that serves the image comparison app.
- `graph.py` - Contains the definitions for a graph of processing steps.  See more
               about this below.

## Augh! What is the server doing?

The server needs to take a project full of images, transform them, and present them
to the Electron app.

Currently, there are 5 stages of transformation:

1. `orig` - The original images of the dataset.
2. `webp` - The `orig` images after being converted to Webp using Pillow.
3. `delta` - The raw pixelwise difference between the original and Webp images.
             It is stored as NumPy binary files.
4. `mask` - The `delta`, but each pixel has had the RGB value (128, 128, 128) added
            so that the difference is visually visible.  It is stored as a PNG.
5. `final` - The `webp` plus the `delta`.  This is the final corrected image.
             It is stored as a PNG.

Initially, the app will request all the `orig` images in the dataset so they can be
displayed in the carousel.  This happens in the `requestGetCarouselPngs()` function.

When the user clicks on an image, the app will request the visual forms of the image
at each stage of the pipeline.  This happens in the `requestGet*()` functions.

## Wait!  I don't see any image transformations happening in the code.  And what's with all the `Node` stuff?

A problem with using a web-based technology for the frontend is that it makes a lot
of asynchronous requests with no ordering.  This means that the app could ask for
the `mask` image before the `webp` has been converted.  When this happens, the app
breaks.  To solve this, we use a graph of processing steps.  The result of each
step gets cached in a separate directory.  When a step is requested, it checks
if the result is already cached.  If not, it runs its dependencies recursively
before returning the result.  This ensures that regardless of the order of requests,
the server will always perform all the needed steps in order.

If you want to add a new visualization, start in `main.py`.  You will see a block
that looks like this:
```python
    (root / "orig").mkdir(parents=True, exist_ok=True)
    (root / "webp").mkdir(parents=True, exist_ok=True)
    (root / "delta").mkdir(parents=True, exist_ok=True)
    (root / "mask").mkdir(parents=True, exist_ok=True)
    (root / "final").mkdir(parents=True, exist_ok=True)
```
Add a new line with the name of your step.  Next, go to `server.py` and add a request
handler, like the following, replacing `mystep` and `MyStepNode` with the name of your
step:
```python
@flaskServer.route("/get-image-mystep", methods=["POST"])
def requestGetFinal():
    root, fileName = getProjectParts(request)
    return MyStepNode().getBytes(root, fileName)
```
Now, you can implement your step node.

`Node`s have 5 methods that you must implement / override:
1. `__init__()` - This function *must* start with `super().__init__()`.  If your
   `Node` requires any other steps to be run before it, you must initialize the
   `parents` field with a list of `Node`s, calling their constructors:
   `self.parents = [PngNode()]`.
2. `needsRerun` - This function usually just needs to check if the file is in the
   cache directory.
3. `run` - This function runs the step. It *must* start with the line
   `super().run(projectRoot, fileName)`.  Everything else is up to you.
4. `getImage` - This function should return an `Image` object.  It is usually
   used by subsequent steps to access the computed image.  It should usually
   check if the node needs to be rerun just in case, and if so, run it.  If
   the node does not need to compute an image (e.g. `delta`), a
   `NotImplementedError` should be raised.
5. `getBytes` - This function should return the bytes of the image.  It is usually
   the method called by the server's request handler to get the image that is sent
   to the frontend.
