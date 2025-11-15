import { Component, createResource } from 'solid-js'
import { state, getImage, ImageType } from './model';
import { Zoomer } from './Zoomer';

const Viewer: Component = () => {
  const [origImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Orig)
  );
  const [webpImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Webp)
  );
  const [maskImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Mask)
  );
  const [finalImg] = createResource(
    () => state.selectedImageFileName,
    (path) => getImage(path, ImageType.Final)
  );

  return (
    <div class="
      w-full h-full
      max-w-full max-h-full
      overflow-hidden
      flex flex-col
      gap-2
      "
      style={{
        "--zoom-x": `${state.zoomX()}px`,
        "--zoom-y": `${state.zoomY()}px`,
      }}
    >
      <div class="
        h-full
        max-h-[50%]
        flex flex-row
        justify-center
        gap-2
        ">
        <Zoomer blobSrc={origImg() ?? ""} zoomLabel="zoomOrig" />
        <Zoomer blobSrc={webpImg() ?? ""} zoomLabel="zoomWebp" />
      </div>
      <div class="
        h-full
        max-h-[50%]
        flex flex-row
        justify-center
        gap-2
        ">
        <Zoomer blobSrc={maskImg() ?? ""} zoomLabel="zoomMask" />
        <Zoomer blobSrc={finalImg() ?? ""} zoomLabel="zoomFinal" />
      </div>
    </div>
  )
}

export default Viewer;
