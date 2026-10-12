import { deepseek } from "@ai-sdk/deepseek";
import { generateText, tool, stepCountIs } from "ai";
import { z } from "zod";

// ========= 配置 =========
const CITY = "上海"; // 替换成你的城市

// ========= Tool 1: 查询天气 =========
const getWeather = tool({
  description:
    "查询指定城市的实时天气和未来几小时预报，返回温度、天气状况、降雨量、降雨概率等信息",
  inputSchema: z.object({
    city: z.string().describe("城市名称，中文或英文均可"),
  }),
  execute: async ({ city }) => {
    const url = `https://wttr.in/${encodeURIComponent(city)}?format=j1`;
    console.log(`[tool] 正在查询天气: ${city} → ${url}`);

    const res = await fetch(url);
    if (!res.ok) throw new Error(`天气查询失败: HTTP ${res.status}`);

    const data = await res.json();
    const current = data.current_condition[0];
    const hourly = data.weather?.[0]?.hourly ?? [];

    return {
      city,
      当前温度: `${current.temp_C}°C`,
      体感温度: `${current.FeelsLikeC}°C`,
      天气状况: current.weatherDesc?.[0]?.value ?? "未知",
      湿度: `${current.humidity}%`,
      降雨量_mm: current.precipMM ?? "0.0",
      风速: `${current.winddir16Point} ${current.windspeedKmph} km/h`,
      云量: `${current.cloudcover}%`,
      未来几小时: hourly.slice(0, 8).map((h: any) => ({
        时间: h.time,
        天气: h.weatherDesc?.[0]?.value ?? "未知",
        温度: `${h.tempC}°C`,
        降雨概率: `${h.chanceofrain ?? "0"}%`,
        降雨量_mm: h.precipMM ?? "0.0",
      })),
    };
  },
});

// ========= Tool 2: 发送微信消息 =========
const sendWechat = tool({
  description: "通过 Server 酱向微信发送消息通知",
  inputSchema: z.object({
    title: z.string().describe("消息标题，简洁概括"),
    content: z
      .string()
      .describe("消息正文，支持 Markdown 格式，包含天气详情和带伞建议"),
  }),
  execute: async ({ title, content }) => {
    const sendkey = process.env.SERVERCHAN_SENDKEY;
    if (!sendkey) throw new Error("未配置 SERVERCHAN_SENDKEY 环境变量");

    console.log("[tool] 正在发送微信消息...");
    const res = await fetch(`https://sctapi.ftqq.com/${sendkey}.send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, desp: content }),
    });

    const result = await res.json();
    console.log("[tool] Server酱返回:", JSON.stringify(result, null, 2));
    return result;
  },
});

// ========= 主流程 =========
async function main() {
  console.log("⏰ 启动带伞助手...\n");

  const { text, steps } = await generateText({
    model: deepseek("deepseek-chat"),
    tools: { getWeather, sendWechat },
    system: `你是一个贴心的生活助手，每天早上帮用户决定出门是否需要带伞。

你的工作流程：
1. 调用 getWeather 工具查询用户所在城市的天气
2. 根据天气数据判断是否需要带伞
3. 调用 sendWechat 工具把判断结果发送到用户微信

带伞判断规则：
- 当前降雨量 > 0mm 或降雨概率 > 50% → 建议带伞
- 天气描述包含"雨"、"rain"、"shower" → 建议带伞
- 晴天、多云、阴天但无降雨 → 不需要带伞
- 不确定时，倾向于建议带伞（以防万一）

微信消息要求：
- title: 简洁直接，如"今日天气晴好，无需带伞☀️"或"今日有雨，记得带伞🌂"
- content: Markdown 格式，包含当前天气概况、温度、降雨信息、未来几小时趋势、综合建议`,
    prompt: `帮我查询一下${CITY}今天的天气，判断需不需要带伞，然后发微信告诉我。`,
    stopWhen: stepCountIs(5), // 允许最多 5 步 tool call 循环
  });

  console.log("\n===== Agent 执行完毕 =====");
  console.log(text);
}

main();
