from app.llm.client import generate_answer


prompt = """
You are an AI sales planning assistant.

Explain in one sentence why territory allocation
is important for sales planning.
"""

answer = generate_answer(prompt)

print("LLM RESPONSE:")
print(answer)
