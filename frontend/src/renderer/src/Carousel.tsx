import { Component, createResource, For, Suspense } from 'solid-js'
import { createStore } from 'solid-js/store'
import { getImage, ImageType, state } from './model'

const AsyncImage: Component<{ fileName: string }> = (props) => {
  const [imageBlobUrl] = createResource(props.fileName, (fileName) => getImage(fileName, ImageType.Orig));
  return (
    <img class="
      w-full h-full
      object-contain
      "
      src={imageBlobUrl()}
      onClick={() => {state.selectedImageFileName = props.fileName}}
    />
  )
}

const Carousel: Component = () => {
  const [images, setImages] = createStore<string[]>([])

  async function onAddClicked() {
    try {
      const dir = await window.electron.selectDirectory()
      if (!dir) return
      state.projectRoot = dir
      const pngs = await fetch('http://localhost:5000/get-carousel-pngs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectRoot: state.projectRoot,
        }),
      })
      setImages(await pngs.json())
    } catch (err) {
      console.log(err)
    }
  }

  function onDelClicked() {
    setImages([])
    state.projectRoot = undefined
    state.selectedImageFileName = undefined
  }

  return (
    <div class="
      w-full min-h-32 max-h-32
      rounded-lg
      bg-zinc-800
      flex flex-row
      ">
      <button class="
        h-full aspect-square rounded-lg
        bg-zinc-700 hover:bg-zinc-800
        duration-150
        text-white select-none
        "
        onClick={onAddClicked}
      >
        Add
      </button>
      <div class="
        w-full h-full
        px-2
        overflow-x-auto
        flex flex-row
        ">
        <For each={images}>
          {(it) =>
            <Suspense>
              <AsyncImage fileName={it} />
            </Suspense>
          }
        </For>
      </div>
      <button class="
        h-full aspect-square rounded-lg
        bg-zinc-700 hover:bg-zinc-800
        duration-150
        text-white select-none
        "
        onClick={onDelClicked}
      >
        Del
      </button>
    </div>
  )
}

export default Carousel;
