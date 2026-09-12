from typing import Literal

from pydantic import BaseModel

from app.llm.client import generate_json


class RouteDecision(BaseModel):
    route: Literal["rag", "tool", "rag_and_tool"]


def classify_question(question: str) -> str:
    prompt = f"""
You are the routing component of an AI Sales Planning Assistant.

Choose exactly ONE route.

rag:
Use when the question requires company policies,
rules, guidelines, or documented knowledge.

tool:
Use when the question requires current structured
business data from the database.

rag_and_tool:
Use when the question requires both company policy
and current database data.

Rules:
- Return JSON only.
- route must be exactly:
  "rag", "tool", or "rag_and_tool".
- Do not answer the user's question.
- Do not execute any tool.
- Do not invent another route.

User question:
{question}
"""

    result = generate_json(prompt)

    decision = RouteDecision.model_validate(result)

    return decision.route