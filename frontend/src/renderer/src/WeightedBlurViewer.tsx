import { Component, createResource } from 'solid-js'
import Carousel from './Carousel'
import { state, getWeightedBlurImage, WeightedBlurType } from './weightedBlurModel';
import { Zoomer } from './Zoomer';

const WeightedBlurViewer: Component = () => {
    const [jpegImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.Jpeg, state)
    );
    const [maskImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.Mask, state)
    );
    const [sumImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.Sum, state)
    );
    const [blurImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.WeightedBlur, state)
    );
    const [sobelMaskImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.SobelMask, state)
    );
    const [weightedMaskImg] = createResource(
        () => state.selectedImageFileName,
        (path) => getWeightedBlurImage(path, WeightedBlurType.WeightedMask, state)
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
                <Zoomer state={state} blobSrc={blurImg() ?? ""} />
                <Zoomer state={state} blobSrc={sobelMaskImg() ?? ""} />
                <Zoomer state={state} blobSrc={maskImg() ?? ""} />
                <Zoomer state={state} blobSrc={sumImg() ?? ""} />
                <Zoomer state={state} blobSrc={weightedMaskImg() ?? ""} />
            </div>
        </div>
    )
}

export default WeightedBlurViewer;
