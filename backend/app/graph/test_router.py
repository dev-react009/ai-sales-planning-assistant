from app.graph.router import classify_question


questions = [
    "What is the territory allocation policy?",
    "Which sales reps are below 70% quota?",
    "Find unassigned enterprise accounts and recommend potential territories based on the territory allocation policy.",
]


for question in questions:
    route = classify_question(question)

    print("\nQuestion:", question)
    print("Route:", route)