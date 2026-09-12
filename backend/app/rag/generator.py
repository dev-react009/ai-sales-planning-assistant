from app.llm.client import generate_answer
from app.rag.retriever import search_documents


def answer_with_rag(question: str) -> dict:
    results = search_documents(question, limit=3)

    if not results:
        return {
            "answer": "I could not find relevant information in the available policies.",
            "sources": [],
        }

    context = "\n\n".join(
        f"Source: {result['document']}\n{result['content']}"
        for result in results
    )

    prompt = f"""
You are an AI Sales Planning Assistant.

Answer the user's question using ONLY the provided policy context.

Rules:
- Do not invent information.
- If the context does not contain the answer, say you don't have enough information.
- Keep the answer concise and useful.
- Clearly distinguish policy facts from recommendations.
- Do not make up business data.

Policy Context:
{context}

User Question:
{question}

Answer:
"""

    answer = generate_answer(prompt)

    sources = [
        {
            "document": result["document"],
            "similarity": result["similarity"],
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }