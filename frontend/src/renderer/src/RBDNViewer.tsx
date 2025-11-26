import { Component, createResource } from 'solid-js'
import Carousel from './Carousel'
import { state, getImage, ImageType } from './rbdnModel';
import { Zoomer } from './Zoomer';

const RBDNViewer: Component = () => {
  const [webpImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Webp, state)
  );
  const [maskImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Mask, state)
  );
  const [rbdnImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.RBDN, state)
  );
  const [rbdnErrImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.RBDNErr, state)
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
        <Zoomer state={state} blobSrc={rbdnImg() ?? ""} />
        <Zoomer state={state} blobSrc={rbdnErrImg() ?? ""} />
      </div>
    </div>
  )
}

export default RBDNViewer;

//<Zoomer state={state} blobSrc={reconstructedImg() ?? ""} />
