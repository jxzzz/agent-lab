import json
import re
from pathlib import Path

CHUNKS_FILE = Path(__file__).parent / "chunks.jsonl"


def load_chunks() -> list[dict]:
    chunks = []
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def clean_text(text: str) -> str:
    return re.sub(r"\s+", "", text)


def char_bigrams(text: str) -> list[str]:
    return [text[i:i + 2] for i in range(len(text) - 1)]


def score_chunk(query: str, chunk: dict) -> float:
    query = clean_text(query)
    text = clean_text(chunk["text"])
    heading = clean_text(chunk.get("heading", ""))

    score = 0.0

    # 完整问句直接出现在正文里，优先
    if query in text:
        score += 100

    # 与正文的字符二元组重叠越多越相关
    query_grams = set(char_bigrams(query))
    text_grams = set(char_bigrams(text))
    overlap = len(query_grams & text_grams)
    score += overlap * 2

    # 标题命中加一点权重
    if any(bigram in heading for bigram in query_grams):
        score += 10

    return score


def search(query: str, top_k: int = 3) -> list[dict]:
    chunks = load_chunks()

    scored = []
    for chunk in chunks:
        score = score_chunk(query, chunk)
        scored.append({
            "score": score,
            "source": chunk["source"],
            "heading": chunk["heading"],
            "text": chunk["text"],
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    query = "退款多久能到账？"
    results = search(query, top_k=3)

    print(f"问题：{query}\n")
    for rank, result in enumerate(results, start=1):
        print(f"第 {rank} 名，得分 {result['score']:.1f}")
        print(f"来源：{result['source']} / {result['heading']}")
        print(f"内容：{result['text']}")
        print()