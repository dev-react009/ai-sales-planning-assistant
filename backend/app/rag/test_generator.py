from app.rag.generator import answer_with_rag


question = "What is the territory allocation policy?"

result = answer_with_rag(question)

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")
for source in result["sources"]:
    print(source)