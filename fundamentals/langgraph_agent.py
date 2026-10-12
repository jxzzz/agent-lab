import json
import os
import operator
from typing import Annotated, TypedDict
import requests
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from dotenv import load_dotenv
import datetime
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_amount",
            "description": "按订单号查询订单金额和状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "订单号，例如 1001"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "把人民币金额换算成其他货币",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount_cny": {"type": "number", "description": "人民币金额"},
                    "target": {"type": "string", "description": "目标货币，USD 或 JPY"}
                },
                "required": ["amount_cny", "target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_reminder",
            "description": "给用户发送一条提醒",
            "parameters": {
                "type": "object",
                "properties": {
                    "user": {"type": "string", "description": "接收人"},
                    "message": {"type": "string", "description": "提醒内容"}
                },
                "required": ["user", "message"]
            }
        }
    }
]

ORDERS = {
    "1001": {"amount_cny": 880.0, "status": "已支付"},
    "1002": {"amount_cny": 2600.0, "status": "已发货"},
}

def get_order_amount(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if not order:
        return {"error": f"订单 {order_id} 不存在"}
    return order

def convert_currency(amount_cny: float, target: str) -> dict:
    rates = {"USD": 0.14, "JPY": 20.5}
    if target not in rates:
        return {"error": f"不支持货币：{target}"}
    return {
        "amount": round(amount_cny * rates[target], 2),
        "currency": target,
    }

def send_reminder(user: str, message: str) -> dict:
    with open("reminders.log", "a", encoding="utf-8") as f:
        f.write(f"{user}: {message}\n")
    return {"status": "sent", "to": user, "message": message}

TOOL_FUNCTIONS = {
    "get_order_amount": get_order_amount,
    "convert_currency": convert_currency,
    "send_reminder": send_reminder,
}

def execute_tool(name: str, args: dict) -> dict:

    func = TOOL_FUNCTIONS.get(name)

    if not func:
        raise ValueError(f"Unknown tool: {name}")

    if name == "send_reminder":
        answer = input(f"请确认是否发送提醒给 {args.get('user')}，内容：{args.get('message')} (y/n): ")
        if answer.lower() != "y":
            return {"error": "用户取消了提醒发送"}  
    
    try:
        return func(**args)
    except Exception as e:
        return {"error": f"工具参数错误：{e}"}


def call_llm(message: list) -> str:
    headers = {
        "authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": message,        
        # "response_format": {"type": "json_object"},
        "tools": TOOLS,
    }

    response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        # print("本次消耗 token：", data.get("usage"))
        return data["choices"][0]["message"]
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        print("Please check your API key and ensure it is set correctly in the .env file.")
        return ""

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def agent_node(state: AgentState) -> dict:
    # call_llm 就是你现在那个函数，会带 TOOLS 调用模型
    message = call_llm(state["messages"])
    return {"messages": [message]}

def tools_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message["tool_calls"]:
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        result = execute_tool(name, args)

        results.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result, ensure_ascii=False),
        })

    return {"messages": results}

def route_after_agent(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls"):
        return "tools"
    return "end"


graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)

graph.add_edge(START, "agent")
graph.add_edge("tools", "agent")

graph.add_conditional_edges(
    "agent",
    route_after_agent,
    {"tools": "tools", "end": END},
)


app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "order-session-1"}}


SYSTEM_PROMPT = """
你是订单助手。
需要数据时先调用工具，拿到结果后再决定下一步。
如果工具返回 error，请根据错误修正参数后重试。
最终用简洁中文向用户总结结果。
"""

initial_messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "查询订单 1001 的人民币金额，换算成美元，然后提醒经理"},
]

result = app.invoke({"messages": initial_messages}, config)
print(result["messages"][-1]["content"])

# state = app.get_state(config)
# print(len(state.values["messages"]))