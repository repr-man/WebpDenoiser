import { state } from "./model";

type ZoomerProps = {
  blobSrc: string;
  zoomLabel: string;
};

export function Zoomer(props: ZoomerProps) {
  let img: HTMLImageElement | undefined;

  return (
    <img
      class="block object-contain"
      ref={img!}
      src={props.blobSrc}
      style={`image-rendering: pixelated; object-view-box: ${state.isHovered() ? `xywh(var(--zoom-x) var(--zoom-y) ${state.imgRatio * 32}px 32px)` : 'none'}`}
      onMouseEnter={() => {
        state[props.zoomLabel].isOutside = false;
        state[props.zoomLabel].elementWidth = img!.clientWidth;
        state[props.zoomLabel].elementHeight = img!.clientHeight;
        state[props.zoomLabel].naturalWidth = img!.naturalWidth;
        state[props.zoomLabel].naturalHeight = img!.naturalHeight;
        state.imgRatio = img!.clientWidth / img!.clientHeight;
      }}
      onMouseLeave={() => {
        state[props.zoomLabel].isOutside = true;
      }}
      onMouseMove={(e) => {
        state[props.zoomLabel].elementX = e.offsetX;
        state[props.zoomLabel].elementY = e.offsetY;
      }}
    />
  );
}

