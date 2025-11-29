import { Component, createResource } from 'solid-js'
import Carousel from './Carousel'
import { state, getImage, ImageType } from './unetModel';
import { Zoomer } from './Zoomer';

const LightMUNetViewer: Component = () => {
  const [webpImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Webp, state)
  );
  const [maskImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Mask, state)
  );
  const [lightmImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.LightM, state)
  );
  const [errorImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Error, state)
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
        <Zoomer state={state} blobSrc={lightmImg() ?? ""} />
        <Zoomer state={state} blobSrc={errorImg() ?? ""} />
      </div>
    </div>
  )
}

export default LightMUNetViewer;

        //<Zoomer state={state} blobSrc={reconstructedImg() ?? ""} />
