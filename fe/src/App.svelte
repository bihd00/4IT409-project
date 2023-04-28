<script lang="ts">
  import "./app.css";
  import ChatBox from "./lib/ChatBox.svelte";
  import FisLogoEN from "./assets/FIS_logo_en.png";
  import ChatBubble from "./lib/ChatBubble.svelte";
  import {
    fetchResponse,
    parseMessage,
    ttypes,
    type Token,
    type MessageStatus,
  } from "./utils";

  let shiftPressed = false;
  let chatRecords: {
    tokens: Token[];
    status: MessageStatus;
    waiting?: boolean;
  }[] = [];
  let message = "";
  let chatInput: ChatBox;
  let chatInputDisabled: boolean = false;
  let chatHistory: HTMLElement;

  function isValidInput(message: string) {
    if (message === "") return false;
    if (message.split("\n").every((x) => x === "")) return false;
    return true;
  }
  function handleShiftDown(e: KeyboardEvent) {
    if (e.key === "Shift") shiftPressed = true;
  }
  function handleShiftUp(e: KeyboardEvent) {
    if (e.key === "Shift") shiftPressed = false;
  }
  function handleClick() {
    if (!isValidInput(message)) return;
    sendMessage(message);
    message = "";
    chatInput.reset();
  }
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === "Enter" && !shiftPressed) {
      e.preventDefault();
      if (chatInputDisabled) return;
      if (!isValidInput(message)) return;
      sendMessage(message);
      message = "";
      chatInput.reset();
    }
  }

  async function sendMessage(message: string) {
    const pMessage = parseMessage({ status: "success", message });
    const pWaiting = parseMessage({ status: "success", message: " " });

    chatRecords = [
      ...chatRecords,
      { tokens: pMessage, status: "USER" },
      { tokens: pWaiting, status: "RESP", waiting: true },
    ];

    chatHistory.scrollTo(0, chatHistory.scrollHeight);
    setTimeout(() => chatHistory.scrollTo(0, chatHistory.scrollHeight), 10);
    chatInputDisabled = true;

    const resp = await fetchResponse(message);
    const pResp = parseMessage(resp);
    const newMessage = {
      tokens: pResp,
      status: "RESP" as MessageStatus,
      waiting: false,
    };
    if (resp.message == "FETCH_NO_SUCCESS") newMessage.status = "ERROR";
    if (resp.message == "NO_MATCH") newMessage.status = "WARN";
    chatRecords[chatRecords.length - 1] = newMessage;

    chatInputDisabled = false;
    setTimeout(() => chatInput.focus(), 10);
  }

  const initialMessage = {
    tokens: parseMessage({ status: "success", message: " " }),
    status: "RESP" as MessageStatus,
    waiting: true,
  };
  chatRecords = [...chatRecords, initialMessage];

  setTimeout(() => {
    chatRecords[chatRecords.length - 1].waiting = false;
    chatRecords[chatRecords.length - 1].tokens = parseMessage({
      status: "success",
      message: "Ahoj! Zeptej se mě!",
    });
  }, Math.floor(Math.random() * 2 * 1000) + 2000);
</script>

<svelte:window on:keydown={handleShiftDown} on:keyup={handleShiftUp} />

<main class="h-screen max-h-screen text-white flex bg-[#090a11]">
  <div class="container mx-auto max-w-3xl h-full flex flex-col overflow-hidden">
    <!--  -->
    <div class="w-full h-32 px-2 md:px-0 bg-[#090a11]">
      <div class="flex h-full justify-between items-center">
        <h1 class="text-4xl md:text-7xl font-bold">
          <span class="text-[#009982] mr-1">FIS</span><span class="">Bot</span>
        </h1>
        <img src={FisLogoEN} alt="" class="h-[90%] me-[-0.75rem]" />
      </div>
    </div>
    <!--  -->
    <div class="flex flex-col items-center grow max-h-full overflow-hidden">
      <div class="h-full max-h-full flex flex-col w-full overflow-hidden">
        <!--  -->
        <div
          class="w-full overflow-auto no-scrollbar px-2 h-auto mt-auto"
          bind:this={chatHistory}
        >
          {#each chatRecords as record, i}
            <ChatBubble
              status={record.status}
              waiting={record.waiting || false}
              id={i}
            >
              <div
                class="break-words max-w-xs md:max-w-sm lg:max-w-md xl:max-w-lg"
              >
                {#each record.tokens as { type, content }, i}
                  {#if type === ttypes.ERROR}
                    <span>Došlo k chybě</span>
                  {/if}
                  {#if type === ttypes.NOMATCH}
                    <span>Promiň, nerozumím</span>
                  {/if}
                  {#if type === ttypes.WORD}
                    <span>{content}</span>
                  {/if}
                  {#if type === ttypes.SPECIAL}
                    <span>{content}</span>
                  {/if}
                  {#if type === ttypes.BREAK}
                    <br />
                  {/if}
                  {#if type === ttypes.MAIL}
                    <a
                      href="mailto:{content}"
                      target="_blank"
                      class="border-b-2 border-transparent {record.status ===
                      'USER'
                        ? 'text-[#009982] hover:border-[#009982]'
                        : 'text-[#252525] hover:border-[#252525]'}">{content}</a
                    >
                  {/if}
                  {#if type === ttypes.LINK}
                    <a
                      href={content}
                      target="_blank"
                      class="border-b-2 border-transparent {record.status ===
                      'USER'
                        ? 'text-[#009982] hover:border-[#009982]'
                        : 'text-[#252525] hover:border-[#252525]'}">{content}</a
                    >
                  {/if}
                {/each}
              </div>
            </ChatBubble>
          {/each}
        </div>
        <!--  -->
        <div
          class="w-full py-2 md:py-3 md:pl-4 border-gray-900/50 text-white rounded-md relative sm:mb-auto
            {chatInputDisabled ? 'bg-gray-900' : 'bg-gray-800'}
            "
        >
          <ChatBox
            {handleKeyDown}
            {handleClick}
            bind:message
            bind:this={chatInput}
            bind:isDisabled={chatInputDisabled}
          />
        </div>
      </div>
    </div>
  </div>
</main>
