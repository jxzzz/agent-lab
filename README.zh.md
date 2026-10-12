[**简体中文 ← 当前 · switch to English**](./README.md)

# Agent 学习路径

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-1C3C3C?logo=langgraph&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-server%20%2B%20client-000000)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-4D6BFB)

从第一次裸调 LLM API,到一条完整的多 Agent 流水线 —— 一个工作区,五座营地,按真实学习顺序排列。

### 全部秘密,10 行讲完

所有框架都是这个循环的包装。徒手写一遍,之后看什么都通透:

```python
while True:
    resp = llm(messages, tools=tools)
    if not resp.tool_calls:
        break                      # 模型说完了,收工
    for call in resp.tool_calls:
        result = run(call)         # 你的代码动手脚
        messages.append(result)    # 结果回炉,再问模型
```

### 学习路径

| # | 营地 | 目录 | 知识点 |
|---|------|------|--------|
| 01 | 摸清模型 | `fundamentals/` | 裸调 LLM API、多轮上下文、意图解析、function calling、第一个 StateGraph |
| 02 | 跨栈工具调用 | `ai-sdk-lab/` | TypeScript 侧 Vercel AI SDK + zod 工具、多工具编排、语音输入(Deepgram STT) |
| 03 | 单 agent 落地 | `project-1-customer-agent/` | SQLite 工具层、LangGraph 工具循环、会话记忆、人工确认(HITL)、拒绝编造 |
| 04 | 外部知识 · RAG | `project-2-knowledge-agent/` | 切分 → embedding → 向量检索、带来源回答、无答案拒绝、FastAPI、MCP server/client |
| 05 | 多 agent 协作 | `project-3-report-agent/` | planner → data → writer → reviewer 流水线、SQL 只读防护、SSE 流式、评估回归集 |

每一站都在补上一站的短板:

```
裸调 API → 会用工具 → 会编排 → 单 agent 落地 → 外部知识 → 多 agent
```

- **营地 01–02** —— 模型只会说话;function calling 给它手脚,Python 和 TypeScript 各写一遍。
- **营地 03** —— 跑在真实数据库上的客服 agent:危险操作要人工确认(y/n),查不到的订单就回「不存在」,绝不编造。
- **营地 04** —— 五份政策文档变成可问答的知识库;每个回答都带来源,并通过 MCP 暴露成工具。
- **营地 05** —— 自然语言问题变成带数据引用的 Markdown 报告;SQL 只读、每个结论必须引用真实查询、reviewer 不满意可打回重写(上限 2 轮)。

### 快速开始

```bash
# Python 项目——各自带 .venv,进项目目录跑测试
cd project-2-knowledge-agent
.venv/bin/python -m pytest tests -q

# TypeScript
cd ai-sdk-lab && pnpm install && pnpm dev        # task-1 / dev:umbrella / dev:voice

# 运行各 agent 见各项目 README.md
```

### 沼泽 —— 别踩

| 沼泽 | 为什么陷进去 |
|---|---|
| 从框架教程入门 | 框架的抽象会掩盖你该先学的那个循环 |
| 迷信多 agent | 单 agent + 好工具能解决的事,拆成五个只会互相传错话 |
| 无 eval 调提示词 | 没有测试用例,你不是在迭代,是在掷骰子 |
| 追求通用大脑 | 先窄而深,通用是无数个窄步走出来的 |

### 🗺️ 交互式学习地图

[agent-learning-trail.html](./agent-learning-trail.html) —— 地铁图风格的交互式路线:点节点看技能清单,勾选进度存在浏览器本地。

### 🧭 下一步

Structured output(严格 schema 输出)· 长期记忆 · LangSmith tracing · 检索 rerank · 部署生产化

---

<footer>每一段提交历史都是一次真实练习 · 走窄门,进深路</footer>
