from app.rag.retriever import search_documents


if __name__ == "__main__":
    query = "How are territories allocated?"

    results = search_documents(query, limit=3)

    print(f"\nQuery: {query}")
    print(f"Retrieved {len(results)} results\n")

    for index, result in enumerate(results, start=1):
        print(f"--- Result {index} ---")
        print(f"Document: {result['document']}")
        print(f"Similarity: {result['similarity']}")
        print(f"Content: {result['content']}\n")