import { Component, createResource } from 'solid-js'
import Carousel from './Carousel'
import { state, getSobelImage, SobelType } from './sobelModel';
import { Zoomer } from './Zoomer';

const SobelRGBViewer: Component = () => {
    const [rImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.R, state)
    );
    const [gImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.G, state)
    );
    const [bImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.B, state)
    );

    const [jpegImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.Jpeg, state)
    );
    const [sumImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getSobelImage(path, SobelType.RGBSum, state)
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
                <Zoomer state={state} blobSrc={maskImg() ?? ""} />
                <Zoomer state={state} blobSrc={sumImg() ?? ""} />
                <Zoomer state={state} blobSrc={rImg() ?? ""} />
                <Zoomer state={state} blobSrc={gImg() ?? ""} />
                <Zoomer state={state} blobSrc={bImg() ?? ""} />
            </div>
        </div>
    )
}

export default SobelRGBViewer;
