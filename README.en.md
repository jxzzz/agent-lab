[**English ← current · 切换 简体中文**](./README.md)

[![简体中文](https://img.shields.io/badge/🌐-简体中文-blue)](./README.md)

# Agent Learning Trail

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.x-1C3C3C?logo=langgraph&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-server%20%2B%20client-000000)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-4D6BFB)

From the first raw LLM API call to a full multi-agent pipeline — one workspace, five camps, in real learning order.

### The whole secret, in 10 lines

Every framework is a wrapper around this loop. Write it by hand once, and everything after becomes transparent:

```python
while True:
    resp = llm(messages, tools=tools)
    if not resp.tool_calls:
        break                      # model is done talking
    for call in resp.tool_calls:
        result = run(call)         # your code does the work
        messages.append(result)    # feed it back, ask again
```

### The trail

| # | Camp | Directory | What you learn |
|---|------|-----------|----------------|
| 01 | Know the model | `fundamentals/` | Raw LLM API, multi-turn context, intent parsing, function calling, first StateGraph |
| 02 | Tool calling across stacks | `ai-sdk-lab/` | Vercel AI SDK + zod tools in TypeScript, multi-tool orchestration, voice input (Deepgram STT) |
| 03 | A real single agent | `project-1-customer-agent/` | SQLite tool layer, LangGraph tool loop, session memory, human-in-the-loop confirmation, refusing to hallucinate |
| 04 | External knowledge · RAG | `project-2-knowledge-agent/` | Chunking → embedding → vector search, answers with sources, refusal when unsure, FastAPI, MCP server & client |
| 05 | Multi-agent collaboration | `project-3-report-agent/` | planner → data → writer → reviewer pipeline, read-only SQL guards, SSE streaming, eval regression suite |

Each camp solves what the previous one cannot:

```
raw API → tool calling → orchestration → one grounded agent → external knowledge → many agents
```

- **Camps 01–02** — the model can only talk; function calling gives it hands, in both Python and TypeScript.
- **Camp 03** — a customer-service agent over a real database: dangerous actions need human confirmation (y/n), missing orders get "not found", never invented.
- **Camp 04** — five policy documents become a Q&A knowledge base; every answer carries its source, and MCP exposes it as tools.
- **Camp 05** — a natural-language question becomes a Markdown report with data citations; SQL is read-only, every claim must reference a real query, and the reviewer can force a rewrite (max 2 rounds).

### Quick start

```bash
# Python projects — each has its own .venv, tests from inside the project
cd project-3-report-agent
.venv/bin/python -m pytest tests -q

# TypeScript
cd ai-sdk-lab && pnpm install && pnpm dev        # task-1 / dev:umbrella / dev:voice

# Running the agents — see each project's README.md
```

### Swamps — don't step in

| Swamp | Why it eats you |
|---|---|
| Starting from a framework tutorial | Framework abstractions hide the loop you should learn first |
| Believing in multi-agent | If one agent with good tools can do it, five agents will just misquote each other |
| Tuning prompts without evals | Without test cases you're rolling dice, not iterating |
| Chasing a universal brain | Narrow-and-deep first; generality is walked out one narrow step at a time |

### 🗺️ Interactive map

[agent-learning-trail.html](./agent-learning-trail.html) — a metro-map style interactive trail: click nodes for skill checklists; progress is stored in your browser.

### 🧭 What's next

Structured output · Long-term memory · LangSmith tracing · Retrieval rerank · Production deployment

---

<footer>Every commit is a real exercise · walk the narrow gate, take the deep road</footer>
