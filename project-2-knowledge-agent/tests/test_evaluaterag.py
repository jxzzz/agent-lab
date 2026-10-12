# evaluate_rag.py 这个测试文件写的有问题
import json
import sys
from pathlib import Path

# PROJECT_ROOT = Path(__file__).resolve().parent.parent
# sys.path.insert(0, str(PROJECT_ROOT))


# 如果你 semantic_search.py 里的函数叫 search，就把下面这行改成：
from semantic_search import search as semantic_search
# from semantic_search import semantic_search

QUESTIONS_FILE = "eval_questions.jsonl"

TOP_K = 5


def load_questions(path: str):
    questions = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def best_position(results, expected_sources):
    # 兼容字段名可能叫 source 或 file
    actual_sources = []
    for r in results:
        actual_sources.append(r.get("source") or r.get("file") or "")

    positions = []
    for expected in expected_sources:
        if expected in actual_sources:
            positions.append(actual_sources.index(expected))

    return min(positions) if positions else None


def main():
    questions = load_questions(QUESTIONS_FILE)
    total = len(questions)
    answerable = 0
    hit1 = 0
    hit3 = 0
    no_answer_questions = []

    for q in questions:
        query = q["question"]
        expected_sources = q.get("expected_sources", [])

        # 调用你的真实语义检索
        results = semantic_search(query, top_k=TOP_K)

        if not expected_sources:
            # 这种题暂时无法自动判断，因为检索仍会返回最相近的片段
            no_answer_questions.append(query)
            continue

        answerable += 1
        pos = best_position(results, expected_sources)

        if pos == 0:
            hit1 += 1

        if pos is not None and pos < 3:
            hit3 += 1

        status = f"pos={pos}"
        print(f"[{status}] {query}")
        for i, r in enumerate(results[:3]):
            source = r.get("source") or r.get("file")
            print(f"    #{i + 1} {source} / {r.get('heading', '')}")

    print("\n===== 汇总 =====")
    print(f"总题数：{total}")
    print(f"有答案题目数：{answerable}")
    print(f"hit@1：{hit1}/{answerable} = {hit1 / answerable:.1%}")
    print(f"hit@3：{hit3}/{answerable} = {hit3 / answerable:.1%}")
    print(f"无答案待人工检查：{len(no_answer_questions)} 题")
    for query in no_answer_questions:
        print(f"  - {query}")


if __name__ == "__main__":
    main()