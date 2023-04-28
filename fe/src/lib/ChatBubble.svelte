<script lang="ts">
  import type { MessageStatus } from "../utils";

  export let status: MessageStatus = "USER";
  export let id: number = 1;
  export let waiting: boolean = true;
  let pos = status == "USER" ? "end" : "start";
</script>

<div class="chat chat-{pos}" id="chat-bubble-{id}">
  <div
    class="chat-bubble {status == 'RESP'
      ? 'response'
      : status == 'ERROR'
      ? 'error'
      : status == 'WARN'
      ? 'warning'
      : ''}"
  >
    <slot />
    {#if waiting === true}
      <div class="waiting" />
    {/if}
  </div>
</div>

<style>
  .chat {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }
  .chat-start {
    place-items: start;
    grid-template-columns: auto 1fr;
  }
  .chat-end {
    place-items: end;
    grid-template-columns: 1fr auto;
  }
  .chat-start .chat-bubble {
    grid-column-start: 2;
    border-bottom-left-radius: 0;
  }
  .chat-end .chat-bubble {
    grid-column-start: 1;
    border-bottom-right-radius: 0;
  }
  .chat-bubble {
    --n: 210 18% 15%;
    position: relative;
    display: block;
    width: -moz-fit-content;
    width: fit-content;
    padding: 0.5rem 1rem;
    max-width: 90%;
    border-radius: var(--rounded-box, 1rem);
    min-height: 2.75rem;
    min-width: 2.75rem;
    --tw-bg-opacity: 1;
    background-color: hsl(var(--n) / var(--tw-bg-opacity));
    --tw-text-opacity: 1;
    color: hsl(var(--nc) / var(--tw-text-opacity));
  }
  .chat-bubble.response {
    background-color: #009982;
  }
  .chat-bubble.error {
    background-color: rgb(244 63 94);
  }
  .chat-bubble.warning {
    background-color: rgb(217 119 6);
  }

  .waiting {
    margin-top: 0.3rem;
    padding-top: 1rem;
    width: 10px;
    height: 10px;
    content: "";
    border-right: 7px solid;
    animation: cursor-blink 1s step-end infinite;
  }

  @keyframes cursor-blink {
    from,
    to {
      border-color: transparent;
    }
    50% {
      border-color: #ddd;
    }
  }
</style>
