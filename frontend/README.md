# Frontend

If you don't like web dev stuff, you should probably find your way back to the `backend` directory.

## What tools are you using?

- Electron
- Typescript
- SolidJS
- TailwindCSS
- Vite

## Why use Electron instead of localhost in a browser?

Believe me, I tried.  It comes down to file handling.  Browsers are very restrictive with how much
they let you work with the filesystem.  Electron is *slightly* less restrictive.

## I'm lost in the filesystem again.

The only directory you need to care about is `src/renderer/src/`.  The rest of it is Electron and
Vite boilerplate.

- main.tsx - Mounts the app to the DOM.
- App.tsx - Holds the root component of the app.
- Carousel.tsx - Holds the top bar image carousel component.
- SubtractionViewer.tsx - Holds the grid of images and manages some of the CSS needed for zooming
                          in the default view.
- ConvolutionViewer.tsx - Holds the grid of images and manages some of the CSS needed for zooming
                          in the convolution view.
- subtractionModel.ts - Holds the state and functions needed for the subtraction view.
- convolutionModel.ts - Holds the state and functions needed for the convolution view.
- Zoomer.tsx - Holds the zoomable image component.

## How does the data flow between the app and the server?

Maybe later...

## How does the zooming work?

Would you look at the time?!...
