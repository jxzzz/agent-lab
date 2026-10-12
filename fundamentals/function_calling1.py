
import json
import os
import requests
from dotenv import load_dotenv
import datetime
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

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

def get_weather(city: str) -> str:
    # 这里可以调用实际的天气 API 获取天气信息
    # 例如使用 OpenWeatherMap API 或其他天气服务
    # 下面是一个示例返回值
    return {"city": city, "weather": "晴", "temperature": 28}

def get_current_time() -> dict:
    return {"now": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

def execute_tool(name: str, args: dict) -> dict:

    func = TOOL_FUNCTIONS.get(name)

    if not func:
        raise ValueError(f"Unknown tool: {name}")
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

SYSTEM_PROMPT = """
你是订单助手。
需要数据时先调用工具，拿到结果后再决定下一步。
如果工具返回 error，请根据错误修正参数后重试。
最终用简洁中文向用户总结结果。
"""

def run_agent(user_text) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    for step in range(8):
        print(f"--- 第 {step + 1} 轮模型调用 ---")
        try:
            #  1. 调用 LLM 
            response = call_llm(messages)

            tool_calls = response.get("tool_calls")

            # print("tool_calls:", response.get("tool_calls"))

            # 2. 如果没有工具调用，说明 LLM 已经给出了最终回答
            if not tool_calls:
                print("最终回答：", response.get("content"))
                return
        
            # 3. 如果有工具调用，执行工具，并把结果放回历史
            messages.append(response)
    
            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])

                print(f"执行工具：{name}，参数：{args}")

                result = execute_tool(name, args)
                
                # 3. 把工具执行结果放回历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })
        except Exception as e:
            print(f"Error during agent execution: {e}")
        


if __name__ == "__main__":
    run_agent("查询订单 9999 的人民币金额，换算成美元，然后提醒经理")
   