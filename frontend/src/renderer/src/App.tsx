import { createSignal, Match, Switch, type Component } from 'solid-js'
import SubtractionViewer from './SubtractionViewer'
import ConvolutionViewer from './ConvolutionViewer'
import UNetViewer from './UNetViewer'
import SobelViewer from './SobelViewer'
import SobelRGBViewer from './SobelRGBViewer'

const enum Screen {
  Subtraction,
  Convolution,
  UNet,
  Sobel,
  SobelRGB,
}

const App: Component = () => {
  const [screen, setScreen] = createSignal(Screen.Subtraction)

  const SidebarButton = (props: { screen: Screen, children: any }) => {
    return (
      <button
        class={`
          w-full aspect-square
          text-white
          flex items-center justify-center
          ${props.screen === screen() ? 'bg-zinc-900' : 'bg-zinc-950'}
        `}
        onClick={() => {
          setScreen(props.screen);
        }}
      >
        {props.children}
      </button>
    )
  }

  return (
    <div class="
      w-screen h-screen
      bg-zinc-900
      flex flex-row
      ">
      <div class="
        h-full basis-8
        bg-zinc-950
        flex flex-col
        ">
        <SidebarButton screen={Screen.Subtraction}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
        </SidebarButton>
        <SidebarButton screen={Screen.Convolution}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
          </svg>
        </SidebarButton>
        <SidebarButton screen={Screen.UNet}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3a6 6 0 0 1-6 6h0a6 6 0 0 1-6-6v-3m12 0h-3m-9 0h3" />
          </svg>
        </SidebarButton>
        <SidebarButton screen={Screen.Sobel}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
          </svg>
        </SidebarButton>
        <SidebarButton screen={Screen.SobelRGB}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42" />
          </svg>
        </SidebarButton>
      </div>
      <Switch>
        <Match when={screen() === Screen.Subtraction}>
          <SubtractionViewer />
        </Match>
        <Match when={screen() === Screen.Convolution}>
          <ConvolutionViewer />
        </Match>
        <Match when={screen() === Screen.UNet}>
          <UNetViewer />
        </Match>
        <Match when={screen() === Screen.Sobel}>
          <SobelViewer />
        </Match>
        <Match when={screen() === Screen.SobelRGB}>
          <SobelRGBViewer />
        </Match>
      </Switch>
    </div>
  )
}

export default App
