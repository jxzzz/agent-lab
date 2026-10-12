import json
import operator
import os
from typing import Annotated, TypedDict
import requests

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

import agent_tools

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """
你是电商客服数据助手。
只能根据数据库工具返回的信息回答，查不到就明确说查不到，禁止编造。
发提醒、提交退款这类操作要调用工具，工具会要求用户确认。
如果工具返回 blocked，说明用户没有批准，不要反复尝试。
回答使用简洁中文。
"""


def call_model(messages: list) -> dict:
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "tools": agent_tools.TOOLS,
        "tool_choice": "auto",
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"API 请求失败：{response.status_code} {response.text}")

    data = response.json()
    print("本轮 tokens：", data.get("usage", {}).get("total_tokens"))
    return data["choices"][0]["message"]


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


def agent_node(state: AgentState) -> dict:
    message = call_model(state["messages"])
    return {"messages": [message]}


def tools_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message["tool_calls"]:
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        print(f"调用工具：{name}，参数：{args}")

        result = agent_tools.execute_tool(name, args)

        tool_results.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result, ensure_ascii=False),
        })

    return {"messages": tool_results}


def route_after_agent(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls"):
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
config = {"configurable": {"thread_id": "customer-support-demo"}}

if __name__ == "__main__":
    print("客服 Agent 已启动，输入 /quit 退出")

    while True:
        user_input = input("用户：")
        if user_input == "/quit":
            break

        result = app.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config,
        )

        print("助手：", result["messages"][-1]["content"])
        print()