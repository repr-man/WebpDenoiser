import { createSignal, Match, Switch, type Component } from 'solid-js'
import SubtractionViewer from './SubtractionViewer'
import ConvolutionViewer from './ConvolutionViewer'

const enum Screen {
  Subtraction,
  Convolution,
}

const App: Component = () => {
  const [screen, setScreen] = createSignal(Screen.Subtraction)

  const SidebarButton = (props: { screen: Screen }) => {
    return (
      <button
        class={`
          w-full aspect-square
          text-white
          ${props.screen === screen() ? 'bg-zinc-900' : 'bg-zinc-950'}
        `}
        onClick={() => {
          setScreen(props.screen);
        }}
        >
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
        <SidebarButton screen={Screen.Subtraction} />
        <SidebarButton screen={Screen.Convolution} />
      </div>
      <Switch>
        <Match when={screen() === Screen.Subtraction}>
          <SubtractionViewer />
        </Match>
        <Match when={screen() === Screen.Convolution}>
          <ConvolutionViewer />
        </Match>
      </Switch>
    </div>
  )
}

export default App
