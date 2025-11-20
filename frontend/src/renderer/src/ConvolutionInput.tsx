import { Component, createEffect, For } from "solid-js";
import { state } from "./convolutionModel";

const ConvolutionInput: Component = () => {
  createEffect(() => {
    if (state.matrixSize > state.matrixValues.length) {
      for (const row of state.matrixValues) {
        row.push(0);
        row.push(0);
      }
      state.matrixValues.push(new Array(state.matrixSize).fill(0));
      state.matrixValues.push(new Array(state.matrixSize).fill(0));
    } else if (state.matrixSize < state.matrixValues.length) {
      state.matrixValues.pop();
      state.matrixValues.pop();
      for (const row of state.matrixValues) {
        row.pop();
        row.pop();
      }
    }
  });

  return (
    <div class="
      text-white text-xl
      place-self-center
      flex flex-col
      w-fit p-2 gap-2
      bg-zinc-800 rounded-lg
      ">
      <div class="
        flex flex-row
        justify-center
        ">
        <div class="flex flex-row rounded-lg bg-zinc-700">
        <button class="
          w-8 rounded-l-lg
          hover:bg-zinc-600
          "
          onClick={() => { if (state.matrixSize > 1) state.matrixSize -= 2; }}
        >
          -
        </button>
        <div class="p-2">
          {state.matrixSize}
        </div>
        <button class="
          w-8 rounded-r-lg
          hover:bg-zinc-600
          "
          onClick={() => { if (state.matrixSize < 9) state.matrixSize += 2; }}
        >
          +
        </button>
      </div>
      </div>
      <For each={state.matrixValues}>
        {(row, i) =>
          <div class="
            flex flex-row
            justify-center gap-2
            ">
            <For each={row}>
              {(it, j) =>
                <input type="number" value={it}
                  class="
                  w-14 text-xl bg-zinc-800 text-center
                  [appearance:textfield]
                  [&::-webkit-inner-spin-button]:appearance-none
                  [&::-webkit-outer-spin-button]:appearance-none
                  [&::-webkit-inner-spin-button]:m-0
                  [&::-webkit-outer-spin-button]:m-0
                  "
                  onChange={(e) => { state.matrixValues[i()][j()] = Number(e.target.value); }}
                />
              }
            </For>
          </div>
        }
      </For>
    </div>
  );
}

export default ConvolutionInput;
