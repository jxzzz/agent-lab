# Agent 开发学习路径

从调 API 到多 Agent 系统的完整学习记录，每个目录是一个学习阶段，提交历史按学习顺序排列。

## 学习路径 × 知识点

| # | 阶段 | 目录 | 知识点 |
|---|---|---|---|
| 1 | LLM API 基础 | `fundamentals/` | API 调用、messages 结构、多轮对话上下文、命令行交互 |
| 2 | Function Calling | `fundamentals/` | tool schema 定义、模型决策调用、工具结果回传、意图解析 |
| 3 | LangGraph 入门 | `fundamentals/langgraph_agent.py` | StateGraph 状态机、节点与条件路由、agent↔tools 循环 |
| 4 | TypeScript 侧 AI SDK | `ai-sdk-lab/` | Vercel AI SDK、zod 工具定义、多工具编排、语音输入（Deepgram STT）、Web 前端 |
| 5 | 工具型客服 Agent | `project-1-customer-agent/` | SQLite 数据层、LangGraph 工具循环、会话记忆、人工确认（HITL）、拒绝编造 |
| 6 | RAG 知识库 Agent | `project-2-knowledge-agent/` | 文档切分、embedding、向量检索、带来源回答、MCP server/client、FastAPI |
| 7 | 多 Agent 报告系统 | `project-3-report-agent/` | 多角色协作（planner→data→writer→reviewer）、SQL 只读防护、SSE 流式、评估回归、Web 控制台 |

## 递进逻辑

```
调 API → 会用工具 → 会编排 → 单 agent 落地 → 外部知识(RAG) → 多 agent 协作
```

每一步解决上一步的一个不足：function calling 解决「只会说话」，LangGraph 解决「工具循环难写」，project-1 解决「接真实数据 + 安全」，project-2 解决「模型不知道的知识」，project-3 解决「单 agent 干不了复杂任务」。

## 环境与运行

Python 项目统一使用各自的 `.venv/`，TypeScript 用 pnpm：

```bash
# Python 项目（在各项目目录下）
.venv/bin/python -m pytest tests -q

# TypeScript（ai-sdk-lab/）
pnpm install && pnpm dev

# 运行各 Agent 见各项目 README.md
```

## 下一步计划

- 长期记忆 / 跨会话持久化
- Structured Output（严格 JSON schema 输出）
- LangSmith 可观测性 / tracing
- 评估规模化与部署生产化
