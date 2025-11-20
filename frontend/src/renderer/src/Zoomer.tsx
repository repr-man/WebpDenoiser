type ZoomerProps = {
  blobSrc: string;
  state: any;
};

export function Zoomer(props: ZoomerProps) {
  let img: HTMLImageElement | undefined;
  let overlay: HTMLDivElement | undefined;

  const onOverlayMove = (e: MouseEvent) => {
    if (!img || img.naturalWidth === 0 || !overlay) {
      return;
    }

    props.state.zoom = {
      elementX: e.offsetX,
      elementY: e.offsetY,
      elementWidth: overlay.clientWidth,
      elementHeight: overlay.clientHeight,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
    };
  };

  return (
    <div class="relative w-full h-full">
      <img
        class="object-contain w-full h-full"
        ref={img!}
        src={props.blobSrc}
        style={`image-rendering: pixelated; object-view-box: ${
          props.state.isHovered
            ? `xywh(var(--zoom-x) var(--zoom-y) var(--zoom-width) var(--zoom-height))`
            : 'none'
        }`}
      />
      <div
        class="absolute top-0 left-0 w-full h-full"
        ref={overlay!}
        onMouseMove={onOverlayMove}
      />
    </div>
  );
}
