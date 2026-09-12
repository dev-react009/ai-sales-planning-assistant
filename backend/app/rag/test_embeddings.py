from app.rag.embeddings import create_embedding


if __name__ == "__main__":
    text = "Territories are primarily allocated based on geography."

    embedding = create_embedding(text)

    print("Embedding created successfully")
    print("Dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])