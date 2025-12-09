import { Accessor } from "solid-js";
import { createMutable } from "solid-js/store";

export const enum SobelType {
    Y = 'sobel-y',
    Cb = 'sobel-cb',
    Cr = 'sobel-cr',
    Jpeg = 'jpeg',
    Sum = 'sobel-sum',
    Mask = 'mask',
    R = 'sobel-r',
    G = 'sobel-g',
    B = 'sobel-b',
    RGBSum = 'sobel-rgb-sum',
}

/** @returns a blob url to the image in the current project that is fetched from the server */
export async function getSobelImage(fileName: string | undefined, imgType: SobelType, state: { projectRoot: string | undefined }) {
    if (!fileName) return "";
    const res = await fetch(`http://localhost:5000/get-image-${imgType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            projectRoot: state.projectRoot!,
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
    elementWidth: number;
    elementHeight: number;
    naturalWidth: number;
    naturalHeight: number;
}

type State = {
    projectRoot: string | undefined;
    selectedImageFileName: string | undefined;
    zoom: ZoomerState;
    isHovered: boolean;
    zoomX: Accessor<number>;
    zoomY: Accessor<number>;
    zoomWidth: Accessor<number>;
    zoomHeight: Accessor<number>;
}

const ZOOM_WINDOW_HEIGHT_NATURAL_PX = 32;

export let state: State = createMutable({
    projectRoot: undefined,
    selectedImageFileName: undefined,
    zoom: {
        elementX: 0,
        elementY: 0,
        elementWidth: 0,
        elementHeight: 0,
        naturalWidth: 0,
        naturalHeight: 0,
    },
    isHovered: false,
    zoomX: () => 0,
    zoomY: () => 0,
    zoomWidth: () => 0,
    zoomHeight: () => 0,
});

const naturalRatio = () => {
    const z = state.zoom;
    if (z.naturalHeight === 0 || z.naturalWidth === 0) {
        return 1;
    }
    return z.naturalWidth / z.naturalHeight;
};

state.zoomWidth = () => {
    return ZOOM_WINDOW_HEIGHT_NATURAL_PX * naturalRatio();
};

state.zoomHeight = () => {
    return ZOOM_WINDOW_HEIGHT_NATURAL_PX;
};

state.zoomX = () => {
    const z = state.zoom;
    if (z.elementWidth === 0 || z.naturalWidth === 0) return 0;
    const xEltPct = z.elementX / z.elementWidth;
    const xImgPos = xEltPct * z.naturalWidth - (state.zoomWidth() / 2);
    return xImgPos;
};

state.zoomY = () => {
    const z = state.zoom;
    if (z.elementHeight === 0 || z.naturalHeight === 0) return 0;
    const yEltPct = z.elementY / z.elementHeight;
    const yImgPos = yEltPct * z.naturalHeight - (state.zoomHeight() / 2);
    return yImgPos;
};
