import { Component, createResource } from "solid-js";
import { ConvolutionType, getImageConv, state } from "./convolutionModel";
import ConvolutionInput from "./ConvolutionInput";
import { Zoomer } from "./Zoomer";
import Carousel from "./Carousel";
import { getImage, ImageType } from "./subtractionModel";

const ConvolutionViewer: Component = () => {
  const [webpImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Webp, state)
  );
  const [maskImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Mask, state)
  );

  const [conv1Img] = createResource(
    () => ({
      path: state.selectedImageFileName,
      matrix: JSON.stringify(state.matrixValues),
    }),
    ({ path }) => {
      if (!path) return;
      return getImageConv(path, ConvolutionType.Conv1, state);
    }
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
        grid grid-cols-2 grid-rows-2
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
        <Zoomer state={state} blobSrc={webpImg() ?? ""} />
        <Zoomer state={state} blobSrc={maskImg() ?? ""} />
        <ConvolutionInput />
        <Zoomer state={state} blobSrc={conv1Img() ?? ""} />
      </div>
    </div>
  );
}

export default ConvolutionViewer;
