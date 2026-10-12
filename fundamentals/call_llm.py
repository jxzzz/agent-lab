import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")


url = "https://api.deepseek.com/chat/completions"

headers ={
     "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "system", "content": "你是一个简洁的助手。"},
        {"role": "user", "content": "用一句话介绍你自己"},
    ],
    "stream": False,
}


response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    print(data["choices"][0]["message"]["content"])
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")       
    print("Please check your API key and ensure it is set correctly in the .env file.")