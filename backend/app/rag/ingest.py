from pathlib import Path

from app.database import get_connection
from app.rag.chunker import chunk_text
from app.rag.embeddings import create_embedding


DOCUMENTS_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "documents"
)


def ingest_document(file_path: Path):
    content = file_path.read_text(encoding="utf-8")

    chunks = chunk_text(content)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            # Store the document
            cursor.execute(
                """
                INSERT INTO documents (title, file_path, content)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    file_path.name,
                    str(file_path),
                    content,
                ),
            )

            document_id = cursor.fetchone()[0]

            # Store chunks + embeddings
            for index, chunk in enumerate(chunks):
                embedding = create_embedding(chunk)

                cursor.execute(
                    """
                    INSERT INTO document_chunks
                    (
                        document_id,
                        content,
                        chunk_index,
                        embedding
                    )
                    VALUES (%s, %s, %s, %s);
                    """,
                    (
                        document_id,
                        chunk,
                        index,
                        embedding,
                    ),
                )

        connection.commit()

    print(
        f"Ingested {file_path.name}: "
        f"{len(chunks)} chunks"
    )


def ingest_all_documents():
    for file_path in DOCUMENTS_PATH.glob("*.md"):
        ingest_document(file_path)


if __name__ == "__main__":
    ingest_all_documents()