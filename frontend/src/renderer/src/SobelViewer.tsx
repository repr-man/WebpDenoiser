import { Component, createResource } from 'solid-js'
import Carousel from './Carousel'
import { state, getSobelImage, SobelType } from './sobelModel';
import { Zoomer } from './Zoomer';

const SobelViewer: Component = () => {
    const [yImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Y, state)
    );
    const [cbImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Cb, state)
    );
    const [crImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Cr, state)
    );

    const [jpegImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Jpeg, state)
    );
    const [sumImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Sum, state)
    );
    const [maskImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Mask, state)
    );

    return (
        <div class="
      basis-full w-full h-full
      p-2
      flex flex-col gap-2
      items-center
      ">
            <Carousel state={state} />
            <div class="
        h-full
        grid grid-cols-3 grid-rows-2
        gap-2 justify-center content-center
        overflow-hidden
        "
                style={{
                    "--zoom-x": `${state.zoomX()}px`,
                    "--zoom-y": `${state.zoomY()}px`,
                    "--zoom-width": `${state.zoomWidth()}px`,
                    "--zoom-height": `${state.zoomHeight()}px`,
                }}
                onMouseEnter={() => { state.isHovered = true; }}
                onMouseLeave={() => { state.isHovered = false; }}
            >
                <Zoomer state={state} blobSrc={jpegImg() ?? ""} />
                <Zoomer state={state} blobSrc={yImg() ?? ""} />
                <Zoomer state={state} blobSrc={sumImg() ?? ""} />
                <Zoomer state={state} blobSrc={cbImg() ?? ""} />
                <Zoomer state={state} blobSrc={crImg() ?? ""} />
                <Zoomer state={state} blobSrc={maskImg() ?? ""} />
            </div>
        </div>
    )
}

export default SobelViewer;
