export type MessageStatus = "USER" | "RESP" | "WARN" | "ERROR";

type FetchResponse = { status: string; message: string };
export async function fetchResponse(message: string) {
  const params = new URLSearchParams();
  params.append("message", message);
  params.append("lang", "czech");

  const base_url = "https://fis-chatbot-v0-atb5ncjzqa-ew.a.run.app";
  const url = new URL(base_url);
  url.search = params.toString();

  try {
    const resp = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      method: "GET",
    });
    console.log(resp);
    return await resp.json();
  } catch {
    return { status: "error", message: "FETCH_NO_SUCCESS" };
  }
}

export const ttypes = {
  SPACE: "SPACE",
  BREAK: "BREAK",
  WORD: "WORD",
  LINK: "LINK",
  MAIL: "MAIL",
  SPECIAL: "SPECIAL",
  // reserved
  ERROR: "ERROR",
  NOMATCH: "NOMATCH",
} as const;

export type Token = {
  type: keyof typeof ttypes;
  content?: string;
};

export function parseMessage(response: FetchResponse): Token[] {
  if (response.message === "FETCH_NO_SUCCESS") {
    return [{ type: ttypes.ERROR }];
  }
  if (response.message === "NO_MATCH") {
    return [{ type: ttypes.NOMATCH }];
  }

  const tokens: Token[] = [];
  let word = "";
  for (let i = 0; i < response.message.length; i++) {
    const char = response.message[i];
    if (char === " ") {
      tokens.push({ type: ttypes.WORD, content: word });
      tokens.push({ type: ttypes.SPACE });
      word = "";
      continue;
    }
    if (char === "\n") {
      tokens.push({ type: ttypes.WORD, content: word });
      tokens.push({ type: ttypes.BREAK });
      word = "";
      continue;
    }
    word += char;
    if (i === response.message.length - 1) {
      tokens.push({ type: ttypes.WORD, content: word });
    }
  }

  const rxLink = /\b(https?:\/\/\S+\/?)/g;
  const rxMail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const rxAlnum = /^[\p{L}\p{N}]+$/iu;
  const special: { idx: number; char: string }[] = [];

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    if (!(token.type === ttypes.WORD)) continue;
    if (token.content!.match(rxLink)) {
      token.type = ttypes.LINK;
    }
    if (token.content!.match(rxMail)) {
      token.type = ttypes.MAIL;
    }
    const lastChar = token.content[token.content.length - 1];
    if (lastChar && !lastChar.match(rxAlnum) && token.type !== ttypes.LINK) {
      special.push({ idx: i, char: lastChar });
      token.content = token.content.slice(0, token.content.length - 1);
    }
  }
  let idx = 1;
  for (let record of special) {
    tokens.splice(record.idx + idx, 0, {
      type: ttypes.SPECIAL,
      content: record.char,
    });
    idx++;
  }
  return tokens;
}
