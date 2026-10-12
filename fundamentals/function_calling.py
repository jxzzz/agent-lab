
import json
import os
import requests
from dotenv import load_dotenv
import datetime
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，例如 北京"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}}
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


def execute_tool(tool_name: str, args: dict) -> dict:
    if tool_name == "get_weather":
        return get_weather(**args)
    elif tool_name == "get_current_time":
        return get_current_time()
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

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
        print("本次消耗 token：", data.get("usage"))
        return data["choices"][0]["message"]
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        print("Please check your API key and ensure it is set correctly in the .env file.")
        return ""


def run_agent(user_text) -> None:
    messages = [
        {"role": "user", "content": user_text},
    ]

    for step in range(5):
        print(f"--- 第 {step + 1} 轮模型调用 ---")
        try:
            #  1. 调用 LLM 
            response = call_llm(messages)
            tool_calls = response.get("tool_calls")

            print("tool_calls:", response.get("tool_calls"))

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
            print(f"Error during agent execution: {response}")
        


if __name__ == "__main__":
    run_agent("北京现在天气怎么样？现在几点？")
   