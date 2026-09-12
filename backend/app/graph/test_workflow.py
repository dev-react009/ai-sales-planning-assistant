from app.graph.workflow import graph




question = (
    "Find unassigned enterprise accounts and recommend "
    "potential territories based on the territory allocation policy."
)

print("\n" + "=" * 60)
print("QUESTION:", question)

result = graph.invoke(
    {
        "question": question,
        "route": "",
        "context": "",
        "answer": "",
        "sources": [],
        "tools_used": [],
    }
)

print("\nROUTE:", result["route"])
print("CONTEXT:", result["context"])
print("\nANSWER:")
print(result["answer"])


print("ROUTE:", result["route"])
print("\nSOURCES:")
print(result["sources"])

print("\nTOOLS USED:")
print(result["tools_used"])

print("\nANSWER:")
print(result["answer"])