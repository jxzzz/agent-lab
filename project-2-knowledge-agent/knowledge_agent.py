import json
import operator
import os
from typing import Annotated, TypedDict

import requests
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, add_messages

from semantic_search import search as retrieve_chunks

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """
你是客服知识库问答助手。
每个新的用户问题必须先调用且只能调用一次 search_knowledge。
只有检索结果中确实包含你正在引用的内容时，才能输出“参考来源：[文件名] / [标题]”。
如果检索结果为空或没有足够相关内容：
只回答“知识库中没有相关内容。”
禁止输出任何参考来源，禁止沿用上一轮回答中的来源。
回答使用简洁中文。
"""


def search_knowledge(query: str) -> dict:
    results = retrieve_chunks(query, top_k=3)
    relevant = [item for item in results if item["score"] >= 0.5]

    if not relevant:
        return {
            "results": [],
            "message": "知识库中没有足够相关的内容",
        }

    return {
        "results": relevant,
        "citations": [
            {"source": item["source"], "heading": item["heading"]}
            for item in relevant
        ],
    }

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在客服知识库中检索与用户问题相关的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要检索的问题或关键词"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "search_knowledge": search_knowledge,
}


def execute_tool(name: str, args: dict) -> dict:
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return {"error": f"未知工具：{name}"}

    try:
        return func(**args)
    except Exception as exc:
        return {"error": f"{name} 执行失败：{exc}"}

def to_openai_dict(message):
    if isinstance(message, dict):
        return message

    role_map = {
    "system": "system",
    "human": "user",
    "ai": "assistant",
    "tool": "tool",
}
    
    out = {
        "role": role_map.get(message.type, message.type),
        "content": message.content,
    }

    if message.type == "tool":
        out["tool_call_id"] = message.tool_call_id

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.get("id"),
                "type": "function",
                "function": {
                    "name": tc.get("name"),
                    "arguments": json.dumps(
                        tc.get("args", {}), ensure_ascii=False
                    ),
                },
            }
            for tc in tool_calls
        ]

    return out

def call_model(messages: list) -> dict:
    messages = [to_openai_dict(m) for m in messages]
    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"API 请求失败：{response.status_code} {response.text}")
    return response.json()["choices"][0]["message"]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: AgentState) -> dict:
    return {"messages": [call_model(state["messages"])]}


def tools_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = []

    if isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls", [])
    else:
        tool_calls = getattr(last_message, "tool_calls", [])

    for tool_call in tool_calls:
        # LangGraph 内部格式：name / args / id
        name = tool_call["name"]
        args = tool_call["args"]
        tool_call_id = tool_call["id"]

        result = execute_tool(name, args)

        results.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(result, ensure_ascii=False),
        })

    return {"messages": results}


def has_tool_calls(message) -> bool:
    if isinstance(message, dict):
        return bool(message.get("tool_calls"))
    
    return bool(getattr(message, "tool_calls", None))

def route_after_agent(state: AgentState) -> str:
    last_message = state["messages"][-1]

    if has_tool_calls(last_message):
        return "tools"

    return "end"


graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)
graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent",
    route_after_agent,
    {"tools": "tools", "end": END},
)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "knowledge-agent-demo"}}


def ask(user_input: str, thread_id: str = "knowledge-agent-demo") -> str:
    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(
        {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ]
        },
        config,
    )

    last = result["messages"][-1]

    if isinstance(last, dict):
        return last["content"]

    return last.content

if __name__ == "__main__":
    print("知识库 Agent 已启动，输入 /quit 退出")

    while True:
        user_input = input("用户：")
        if user_input == "/quit":
            break

        answer = ask(user_input)

        print("助手：", answer["messages"][-1]["content"])
        print()