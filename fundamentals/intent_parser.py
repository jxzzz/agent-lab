import os
import requests
from dotenv import load_dotenv  
import json

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

url = "https://api.deepseek.com/chat/completions"

def call_llm(message: list) -> str:
    
    headers = {
        "authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": message,
        "response_format": {"type": "json_object"},
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print("本次消耗 token：", data.get("usage"))
        return data["choices"][0]["message"]["content"]
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        print("Please check your API key and ensure it is set correctly in the .env file.")
        return ""


def main() -> None:
    SYSTEM_PROMPT = """
你是意图解析器。根据用户输入判断意图，只输出 JSON，不要解释。

JSON 格式必须严格为：
{"intent": "意图名", "args": {"参数名": "参数值"}}

可用意图：query_weather, book_ticket, play_music, search_info
无法判断时输出：{"intent": "unknown", "args": {}}
"""
    # messages = [
    #     {"role": "system", "content": SYSTEM_PROMPT},
    # ]
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
          ]

        try:
            # 尝试解析为 JSON
            response = call_llm(messages)
            parsed_response = json.loads(response)
            print(f"Assistant: {parsed_response}")
        except json.JSONDecodeError:
            print("Assistant: 无法解析为 JSON，请检查输出格式。")
            print(f"Raw response: {response}")



if __name__ == "__main__":
    main()