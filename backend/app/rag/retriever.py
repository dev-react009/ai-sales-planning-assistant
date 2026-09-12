from app.database import get_connection
from app.rag.embeddings import create_embedding


def search_documents(
    query: str,
    limit: int = 3,
):
    query_embedding = create_embedding(query)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dc.id,
                    dc.document_id,
                    dc.content,
                    dc.chunk_index,
                    d.title,
                    1 - (dc.embedding <=> %s::vector) AS similarity
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                ORDER BY dc.embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding,
                    query_embedding,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            return [
                {
                    "chunk_id": row[0],
                    "document_id": row[1],
                    "content": row[2],
                    "chunk_index": row[3],
                    "document": row[4],
                    "similarity": round(float(row[5]), 4),
                }
                for row in rows
            ]