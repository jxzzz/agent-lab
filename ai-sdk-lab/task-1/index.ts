import { deepseek } from "@ai-sdk/deepseek";
import { generateText, Output } from "ai";
import { z } from "zod";

// 1. 用 Zod 定义期望的数据结构 —— model 会把新闻提取成这个格式
const NewsSchema = z.object({
  time: z.string(),
  location: z.string(),
  person: z.string(),
  summary: z.string(),
});

type NewsData = z.infer<typeof NewsSchema>;

// 模拟新闻文本
const newsText = `
本报讯 记者李明报道：2024年5月12日下午3点，位于上海市浦东新区的科技博览中心发生了一件备受瞩目的事件。
知名科技企业"未来引擎"CEO张华在年度发布会上，正式推出了一款名为"QuantumX"的家用量子计算机原型机。
据现场报道，该设备能够在室温下运行，运算速度是目前顶配个人电脑的数千倍。
发布会现场聚集了超过2000名媒体记者和科技爱好者，张华在台上激动地表示，这将彻底改变人类处理信息的方式。
不过，也有行业专家在接受采访时指出，该设备目前仍处于原型阶段，距离真正量产走向千家万户可能还需要5到10年的时间。
`;

async function extractNewsToJson(text: string): Promise<NewsData | null> {
  const systemPrompt = `
  你是一个专业的新闻数据提取专家。
  你的任务是从用户提供的新闻文本中提取关键信息。

  提取规则：
  - time: 事件发生的时间（如果没有明确时间，填 "未知"）
  - location: 事件发生的地点（如果没有明确地点，填 "未知"）
  - person: 事件涉及的主要人物（多个名字用逗号分隔）
  - summary: 将事件浓缩成一句话的摘要（不超过30个字）
  `;

  console.log("正在呼叫 DeepSeek 大模型，请稍候...\n");

  try {
    // 2. 调用 DeepSeek —— Output.object() 自动让模型返回指定结构的数据
    const { output } = await generateText({
      model: deepseek("deepseek-chat"),
      output: Output.object({ schema: NewsSchema }),
      system: systemPrompt,
      prompt: `请提取以下新闻：\n${text}`,
      temperature: 0.1,
    });

    return output;
  } catch (error) {
    console.error("❌ 请求失败：", error);
    return null;
  }
}

// ================= 运行测试 =================
async function main() {
  const result = await extractNewsToJson(newsText);

  if (result) {
    console.log("✅ 成功解析并校验！结果如下：");
    console.log(`时间: ${result.time}`);
    console.log(`地点: ${result.location}`);
    console.log(`人物: ${result.person}`);
    console.log(`摘要: ${result.summary}`);
  }
}

main();
