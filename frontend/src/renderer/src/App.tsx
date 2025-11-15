import type { Component } from 'solid-js'
import Carousel from './Carousel'
import Viewer from './Viewer'

const App: Component = () => {
  return (
    <div class="
      w-screen h-screen
      p-2
      bg-zinc-900
      flex flex-col gap-2
      ">
      <Carousel />
      <Viewer />
    </div>
  )
}

export default App
