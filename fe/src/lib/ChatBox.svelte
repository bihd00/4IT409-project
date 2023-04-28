<script lang="ts">
  import Arrow from "../assets/arrow.svelte";
  export let message = "";
  export let height = 24;
  export let handleKeyDown = (e: KeyboardEvent) => {};
  export let handleClick = (e: Event) => {};
  export let isDisabled = false;

  let element: HTMLTextAreaElement;

  export function reset() {
    element.style.height = height + "px";
  }
  export function focus() {
    element.focus();
    element.click();
  }

  function autoResize({ target: textarea }) {
    textarea.style.height = height + "px";
    textarea.style.height = textarea.scrollHeight + "px";
  }
</script>

<textarea
  tabindex="0"
  data-id="root"
  style="max-height: 200px; height: {height}px; overflow-y: auto;"
  rows="1"
  placeholder="Send a message."
  class="
    m-0 w-full resize-none border-0 bg-transparent p-0 pr-7
    focus:ring-0 focus-visible:ring-0 dark:bg-transparent pl-2
    md:pl-0 focus:outline-none focus:border-none no-scrollbar
    disabled:text-gray-700
  "
  on:input={autoResize}
  on:keydown={handleKeyDown}
  bind:value={message}
  bind:this={element}
  autofocus
/>
<button
  on:click={handleClick}
  disabled={isDisabled}
  class="
    absolute p-1.5 pt-2 rounded-md text-gray-500 bottom-1.5
    md:bottom-2.5 hover:bg-gray-100 enabled:hover:text-gray-400
    hover:bg-gray-900 disabled:hover:bg-transparent
    disabled:hover:bg-transparent right-1 md:right-2 disabled:opacity-40"
>
  <Arrow />
</button>
