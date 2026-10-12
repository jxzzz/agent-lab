import json
from pathlib import Path

from load_docs import load_documents

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
OUTPUT_FILE = Path(__file__).parent / "chunks.jsonl"


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = text.strip()
    if len(text) <= size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + size

        if end < len(text):
            cut = text.rfind("\n", start, end)
            if cut > start + size // 2:
                end = cut

        chunks.append(text[start:end].strip())
        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return [chunk for chunk in chunks if chunk]


def chunk_documents() -> list[dict]:
    documents = load_documents()
    all_chunks = []
    chunk_id = 0
    # 获取所有文档的块
    for doc in documents:
        # print(f"正在处理文档：{doc['file']}，长度：{doc['length']}，标题：{doc.get('heading', '无')}")

        print(f"{doc}")
        current_heading = "概述"
        section_lines = []

        def flush_section() -> None:
            nonlocal chunk_id
            text = "\n".join(section_lines).strip()
            if not text:
                return

            for piece in chunk_text(text):
                all_chunks.append({
                    "id": chunk_id,
                    "source": doc["file"],
                    "heading": current_heading,
                    "text": piece,
                    "length": len(piece),
                })
                chunk_id += 1
                
        # 按行处理文档内容，遇到标题时刷新当前块
        for line in doc["text"].splitlines():
            # 如果遇到标题行（以 # 开头），则刷新当前块，并更新当前标题
            if line.startswith("#"):
                # 刷新当前块是什么意思
                flush_section()
                current_heading = line.lstrip("#").strip()
                section_lines = []
            else:
                section_lines.append(line)

        flush_section()

    return all_chunks


if __name__ == "__main__":    
    chunks = chunk_documents()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"文档块总数：{len(chunks)}")
    print(f"平均长度：{sum(c['length'] for c in chunks) / len(chunks):.1f}")
    print(f"来源文件数：{len({c['source'] for c in chunks})}")

    for chunk in chunks[:5]:
        print("-", chunk["source"], "|", chunk["heading"], "|", chunk["length"])