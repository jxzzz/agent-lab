import { createServer, type IncomingMessage } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { DeepgramClient } from "@deepgram/sdk";
import { deepseek } from "@ai-sdk/deepseek";
import { generateText } from "ai";

const PORT = 3001;
const HTML_PATH = join(import.meta.dirname, "index.html");

type Lang = "en" | "zh";

const SYSTEMS: Record<Lang, string> = {
  en: "You are a friendly English conversation partner. Keep responses short (2-3 sentences), conversational, and natural — as if talking out loud. Use everyday vocabulary. Occasionally ask follow-up questions to keep the conversation going.",
  zh: "你是一个友好的中文语音助手。回答简洁（2-3 句）、口语化、适合被朗读出来。用日常词汇，偶尔追问让对话自然延续。",
};

const TTS_MODELS: Record<Lang, string> = {
  en: "aura-asteria-en",
  zh: "aura-xiao-zh",
};

const DG_LANGUAGES: Record<Lang, string> = {
  en: "en",
  zh: "zh-CN",
};

// ========= 路由 =========
const server = createServer(async (req, res) => {
  const url = req.url ?? "/";
  const urlObj = new URL(url, `http://localhost:${PORT}`);
  const pathname = urlObj.pathname;

  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  // 首页
  if (pathname === "/" && req.method === "GET") {
    if (!existsSync(HTML_PATH)) {
      res.writeHead(404);
      return res.end("index.html not found");
    }
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.writeHead(200);
    return res.end(readFileSync(HTML_PATH, "utf-8"));
  }

  // STT: 音频 → 文字
  if (pathname === "/api/stt" && req.method === "POST") {
    try {
      const lang = (urlObj.searchParams.get("lang") ?? "en") as Lang;
      const buffers = await readBody(req);
      const audio = Buffer.concat(buffers);
      console.log(`[stt] ${audio.length} bytes, lang=${lang}`);

      const dg = new DeepgramClient();
      const result = await dg.listen.v1.media.transcribeFile(audio, {
        model: "nova-3",
        language: DG_LANGUAGES[lang],
        smart_format: true,
        punctuate: true,
      });

      const text =
        (result as any)?.results?.channels?.[0]?.alternatives?.[0]
          ?.transcript ?? "";
      console.log(`[stt] → "${text}"`);

      res.setHeader("Content-Type", "application/json");
      res.writeHead(200);
      return res.end(JSON.stringify({ text }));
    } catch (err: any) {
      console.error("[stt] 失败:", err.message);
      res.setHeader("Content-Type", "application/json");
      res.writeHead(500);
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  // Chat: 文字 → LLM
  if (pathname === "/api/chat" && req.method === "POST") {
    try {
      const { text, lang = "en" } = JSON.parse(
        Buffer.concat(await readBody(req)).toString()
      ) as { text: string; lang: Lang };
      console.log(`[chat] ${lang}: "${text.slice(0, 60)}"`);

      const { text: reply } = await generateText({
        model: deepseek("deepseek-chat"),
        system: SYSTEMS[lang] ?? SYSTEMS.en,
        prompt: text,
        temperature: 0.7,
      });

      console.log(`[chat] → "${reply.slice(0, 60)}"`);

      res.setHeader("Content-Type", "application/json");
      res.writeHead(200);
      return res.end(JSON.stringify({ text: reply }));
    } catch (err: any) {
      console.error("[chat] 失败:", err.message);
      res.setHeader("Content-Type", "application/json");
      res.writeHead(500);
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  // TTS: 文字 → 语音 (Deepgram Aura)
  if (pathname === "/api/tts" && req.method === "POST") {
    try {
      const { text, lang = "en" } = JSON.parse(
        Buffer.concat(await readBody(req)).toString()
      ) as { text: string; lang: Lang };
      console.log(`[tts] ${lang}: "${text.slice(0, 50)}..."`);

      const dg = new DeepgramClient();
      const response = await dg.speak.v1.audio.generate({
        text,
        model: TTS_MODELS[lang] ?? TTS_MODELS.en,
        encoding: "mp3",
      });

      const audioBuffer = Buffer.from(await response.arrayBuffer());

      res.setHeader("Content-Type", "audio/mpeg");
      res.setHeader("Content-Length", audioBuffer.length);
      res.writeHead(200);
      return res.end(audioBuffer);
    } catch (err: any) {
      console.error("[tts] 失败:", err.message);
      res.setHeader("Content-Type", "application/json");
      res.writeHead(500);
      return res.end(JSON.stringify({ error: err.message }));
    }
  }

  res.writeHead(404);
  return res.end("404");
});

function readBody(req: IncomingMessage): Promise<Buffer[]> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (ch) => chunks.push(ch as Buffer));
    req.on("end", () => resolve(chunks));
    req.on("error", reject);
  });
}

server.listen(PORT, () => {
  console.log(`🎤 语音助手已启动: http://localhost:${PORT}`);
  console.log(`   打开浏览器，授权麦克风后即可对话\n`);
});
