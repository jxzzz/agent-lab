import json
import math
from pathlib import Path

from build_vector_index import embed_text

INDEX_FILE = Path(__file__).parent / "vector_index.json"


def load_index() -> list[dict]:
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def search(query: str, top_k: int = 3) -> list[dict]:
    records = load_index()
    query_vector = embed_text(query)
  

    scored = []
    for record in records:
        score = cosine_similarity(query_vector, record["embedding"])
        scored.append({
            "score": score,
            "source": record["source"],
            "heading": record["heading"],
            "text": record["text"],
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    queries = [
        "钱什么时候退回来？",
        "退款多久能到账？",
        "什么情况下可以七天无理由退货？",
    ]

    for query in queries:
        print(f"问题：{query}")
        for rank, result in enumerate(search(query, top_k=3), start=1):
            print(f"  #{rank} 相似度 {result['score']:.4f}")
            print(f"    来源：{result['source']} / {result['heading']}")
            print(f"    内容：{result['text'][:50]}")
        print()