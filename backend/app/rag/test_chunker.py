from pathlib import Path

from app.rag.chunker import chunk_text


DOCUMENT_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "documents"
    / "territory-policy.md"
)


if __name__ == "__main__":
    text = DOCUMENT_PATH.read_text(encoding="utf-8")

    chunks = chunk_text(text)

    print("Document:", DOCUMENT_PATH.name)
    print("Total chunks:", len(chunks))

    for index, chunk in enumerate(chunks):
        print(f"\n--- Chunk {index} ---")
        print(chunk)
        