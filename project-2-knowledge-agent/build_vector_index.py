import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("EMBEDDING_BASE_URL")
API_KEY = os.getenv("EMBEDDING_API_KEY")
MODEL = os.getenv("EMBEDDING_MODEL")


CHUNKS_FILE = Path(__file__).parent / "chunks.jsonl"
OUTPUT_FILE = Path(__file__).parent / "vector_index.json"

# chunk - > embed - > save to vector_index.json
def embed_text(text: str) -> list[float]:
    response = requests.post(
        f"{BASE_URL}/embeddings",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "input": text,
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise RuntimeError(f"Embedding 请求失败：{response.status_code} {response.text}")

    return response.json()["data"][0]["embedding"]


def load_chunks() -> list[dict]:
    chunks = []
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def main() -> None:
    chunks = load_chunks()
    records = []

    for index, chunk in enumerate(chunks):
        print(f"处理第 {index + 1}/{len(chunks)} 条：{chunk['source']} / {chunk['heading']}")

        vector = embed_text(chunk["text"])

        records.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "heading": chunk["heading"],
            "text": chunk["text"],
            "embedding": vector,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"完成，共 {len(records)} 条向量")
    print(f"向量维度：{len(records[0]['embedding'])}")




if __name__ == "__main__":
    main()