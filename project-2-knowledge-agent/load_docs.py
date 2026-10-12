from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"

def load_documents() -> list[dict]:
    documents = []
    for file_path in sorted(DOCS_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        documents.append({
            "file": file_path.name,
            "text": text,
            "length": len(text),
        })
    return documents

if __name__ == "__main__":
    docs = load_documents()
    for doc in docs:
        print(f"Loaded {doc['file']} ({doc['length']} characters)") 