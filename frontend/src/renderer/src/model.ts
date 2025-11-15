import { Accessor } from "solid-js";
import { createMutable } from "solid-js/store"

export const enum ImageType {
  Orig = 'orig',
  Webp = 'webp',
  Mask = 'mask',
  Final = 'final',
}

/** @returns a blob url to the image in the current project that is fetched from the server */
export async function getImage(fileName: string | undefined, imgType: ImageType) {
  if (!fileName) return "";
  const res = await fetch(`http://localhost:5000/get-image-${imgType}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      projectRoot: state.projectRoot,
      fileName
    }),
  })
  const file = await res.bytes()
  const blob = new Blob([file])
  const url = URL.createObjectURL(blob)
  return url
}

type ZoomerState = {
  elementX: number;
  elementY: number;
  isOutside: boolean;
  elementWidth: number;
  elementHeight: number;
  naturalWidth: number;
  naturalHeight: number;
}

type State = {
  projectRoot: string | undefined;
  selectedImageFileName: string | undefined;
  zoomOrig: ZoomerState;
  zoomWebp: ZoomerState;
  zoomMask: ZoomerState;
  zoomFinal: ZoomerState;
  isHovered: Accessor<boolean>;
  zoomX: Accessor<number>;
  zoomY: Accessor<number>;
  imgRatio: number;
}

export let state: State = createMutable({
  projectRoot: undefined,
  selectedImageFileName: undefined,
  zoomOrig: {
    isOutside: false,
    elementX: 0,
    elementY: 0,
    elementWidth: 0,
    elementHeight: 0,
    naturalWidth: 0,
    naturalHeight: 0,
  },
  zoomWebp: {
    isOutside: false,
    elementX: 0,
    elementY: 0,
    elementWidth: 0,
    elementHeight: 0,
    naturalWidth: 0,
    naturalHeight: 0,
  },
  zoomMask: {
    isOutside: false,
    elementX: 0,
    elementY: 0,
    elementWidth: 0,
    elementHeight: 0,
    naturalWidth: 0,
    naturalHeight: 0,
  },
  zoomFinal: {
    isOutside: false,
    elementX: 0,
    elementY: 0,
    elementWidth: 0,
    elementHeight: 0,
    naturalWidth: 0,
    naturalHeight: 0,
  },
  isHovered: () => false,
  zoomX: () => 0,
  zoomY: () => 0,
  imgRatio: 0,
});

state.isHovered = () => !state.zoomOrig.isOutside || !state.zoomWebp.isOutside || !state.zoomMask.isOutside || !state.zoomFinal.isOutside;

state.zoomX = () => {
  const z = !state.zoomOrig.isOutside ? state.zoomOrig
    : !state.zoomWebp.isOutside ? state.zoomWebp
      : !state.zoomMask.isOutside ? state.zoomMask
        : state.zoomFinal;
  const xEltPct = z.elementX / z.elementWidth;
  const xImgPos = xEltPct * z.naturalWidth - state.imgRatio * 16;
  return xImgPos;
};

state.zoomY = () => {
  const z = !state.zoomOrig.isOutside ? state.zoomOrig
    : !state.zoomWebp.isOutside ? state.zoomWebp
      : !state.zoomMask.isOutside ? state.zoomMask
        : state.zoomFinal;
  const yEltPct = z.elementY / z.elementHeight;
  const yImgPos = yEltPct * z.naturalHeight - 16;
  return yImgPos;
};
