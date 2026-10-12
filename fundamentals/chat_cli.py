import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
URL = "https://api.deepseek.com/chat/completions"


def call_llm(message: list) -> str:
    headers = {
        "authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",

    }

    playload = {
        "model": "deepseek-chat",
        "messages": message,    
    }

    response = requests.post(URL, headers=headers, json=playload, timeout=30)

    if response.status_code == 200:
        data = response.json()
        print("本次消耗 token：", data.get("usage"))
        return data["choices"][0]["message"]["content"]
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        print("Please check your API key and ensure it is set correctly in the .env file.")
        return ""


def main() -> None:
    messages = [
        {"role": "system", "content": "你是一个简洁的助手。"},
        # {"role": "user", "content": user_input},
    ]
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})

        response = call_llm(messages)
        print(f"Assistant: {response}")



if __name__ == "__main__":
    main()
