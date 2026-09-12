import asyncio
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.llm.client import generate_answer
from app.graph.router import classify_question
from app.mcp_client import call_mcp_tool
from app.rag.retriever import search_documents


class GraphState(TypedDict):
    question: str
    route: str
    context: str
    answer: str
    sources: list[str]
    tools_used: list[str]

def analyze_question(state: GraphState):
    route = classify_question(state["question"])

    return {
        "route": route
    }


def route_question(
    state: GraphState,
) -> Literal["rag", "tool", "rag_and_tool"]:
    return state["route"]


def run_rag(state: GraphState):
    results = search_documents(
        state["question"],
        limit=3,
    )

    context = "\n\n".join(
        f"Source: {result['document']}\n{result['content']}"
        for result in results
    )

    sources = [
        result["document"]
        for result in results
    ]

    return {
        "context": context,
        "sources": sources,
    }


def run_tool(state: GraphState):
    question = state["question"].lower()

    if "quota" in question:
        data = asyncio.run(
            call_mcp_tool(
                "quota_attainment",
                {"threshold": 70.0},
            )
        )
        tool_name = "quota_attainment"

    elif "unassigned" in question:
        data = asyncio.run(
            call_mcp_tool(
                "unassigned_enterprise_accounts"
            )
        )
        tool_name = "unassigned_enterprise_accounts"

    else:
        data = []
        tool_name = ""

    return {
        "context": str(data),
        "tools_used": [tool_name] if tool_name else [],
    }


def run_rag_and_tool(state: GraphState):
    results = search_documents(
        state["question"],
        limit=3,
    )

    policy_context = "\n\n".join(
        f"Source: {result['document']}\n{result['content']}"
        for result in results
    )

    account_data = asyncio.run(
        call_mcp_tool(
            "unassigned_enterprise_accounts"
        )
    )

    account_context = "\n\n".join(
        f"""
Account: {account["name"]}
Industry: {account["industry"]}
Segment: {account["segment"]}
Primary Location: {account["primary_location"]}
Territory ID: {account["territory_id"]}
Assignment Status: {account["assignment_status"]}
""".strip()
        for account in account_data
    )

    context = f"""
POLICY INFORMATION:
{policy_context}

CURRENT DATABASE DATA:
{account_context}

DATA DEFINITIONS:
- primary_location identifies the primary location of the account.
- territory_id identifies the territory currently associated with the account.
- assignment_status identifies whether a sales representative is assigned.
- UNASSIGNED_TO_SALES_REP means the account currently has no assigned sales representative.
- Do not treat territory_id as sales-representative assignment.
- Never claim an official assignment unless it exists in the database.
"""

    return {
        "context": context,
        "sources": [
            result["document"]
            for result in results
        ],
        "tools_used": [
            "unassigned_enterprise_accounts"
        ],
    }


def generate_final_answer(state: GraphState):
    prompt = f"""
You are an AI Sales Planning Assistant.

Answer the user's question using the provided policy information
and database data.

Rules:
- Use database data for current business facts.
- Use policy information for business rules and guidelines.
- Do not invent facts.
- Do not assume missing geographic information.
- Do not confuse territory assignment with sales-representative assignment.
- An account is unassigned when its assignment status is
  UNASSIGNED_TO_SALES_REP.
- Recommendations are suggestions, not confirmed assignments.
- Never claim an account is officially assigned unless the database says so.
- If required information is missing, clearly say so.

POLICY INFORMATION:
{state["context"]}

USER QUESTION:
{state["question"]}

Provide a concise, useful answer.
"""

    answer = generate_answer(prompt)

    return {
        "answer": answer
    }


graph_builder = StateGraph(GraphState)

graph_builder.add_node(
    "analyze_question",
    analyze_question,
)

graph_builder.add_node(
    "rag",
    run_rag,
)

graph_builder.add_node(
    "tool",
    run_tool,
)

graph_builder.add_node(
    "rag_and_tool",
    run_rag_and_tool,
)

graph_builder.add_node(
    "generate_answer",
    generate_final_answer,
)

graph_builder.add_edge(
    START,
    "analyze_question",
)

graph_builder.add_conditional_edges(
    "analyze_question",
    route_question,
    {
        "rag": "rag",
        "tool": "tool",
        "rag_and_tool": "rag_and_tool",
    },
)

graph_builder.add_edge(
    "rag",
    "generate_answer",
)

graph_builder.add_edge(
    "tool",
    "generate_answer",
)

graph_builder.add_edge(
    "rag_and_tool",
    "generate_answer",
)

graph_builder.add_edge(
    "generate_answer",
    END,
)

graph = graph_builder.compile()