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
    question = state["question"].lower()

    results = search_documents(
        state["question"],
        limit=3,
    )

    policy_context = "\n\n".join(
        f"Source: {result['document']}\n{result['content']}"
        for result in results
    )

    tools_used = []
    database_context = ""

    if any(
        keyword in question
        for keyword in [
            "quota",
            "attainment",
            "sales rep",
            "sales reps",
            "representative",
            "representatives",
            "below 70",
            "performance",
        ]
    ):
        quota_data = asyncio.run(
            call_mcp_tool(
                "quota_attainment",
                {"threshold": 70.0},
            )
        )

        tools_used.append("quota_attainment")

        database_context = "\n\n".join(
            f"""
Sales Rep: {rep["name"]}
Quota: {rep["quota"]}
Achieved: {rep["achieved"]}
Attainment: {rep["attainment"]}%
""".strip()
            for rep in quota_data
        )

    elif any(
        keyword in question
        for keyword in [
            "unassigned",
            "enterprise accounts",
            "accounts",
        ]
    ):
        account_data = asyncio.run(
            call_mcp_tool(
                "unassigned_enterprise_accounts"
            )
        )

        tools_used.append(
            "unassigned_enterprise_accounts"
        )

        database_context = "\n\n".join(
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
{database_context}

DATA DEFINITIONS:
- primary_location identifies the primary location of the account.
- territory_id identifies the territory currently associated with the account.
- assignment_status identifies whether a sales representative is assigned.
- UNASSIGNED_TO_SALES_REP means the account currently has no assigned
  sales representative.
- Do not treat territory_id as sales-representative assignment.
- Never claim an official assignment unless it exists in the database.
"""

    return {
        "context": context,
        "sources": [
            result["document"]
            for result in results
        ],
        "tools_used": tools_used,
    }

def generate_final_answer(state: GraphState):
    prompt = f"""
You are an AI Sales Planning Assistant.

Answer the user's question using ONLY the provided policy information
and current database data.

========================
CORE DATA RULES
========================

- Use database data for current business facts.
- Use policy information for rules, policies, and guidelines.
- Never invent facts, numbers, accounts, territories, representatives,
  assignments, or recommendations.
- If required information is missing, clearly say so.
- Do not assume missing geographic or business information.
- Do not confuse territory assignment with sales-representative assignment.
- An account is unassigned only when its assignment status is
  UNASSIGNED_TO_SALES_REP.
- territory_id identifies the territory associated with an account.
- territory_id does NOT mean that a sales representative is assigned.
- Never claim an official assignment unless the database explicitly
  confirms it.
- Recommendations are suggestions only and must be clearly labeled.

========================
POLICY VS DATABASE
========================

When both policy information and database data are available:

- Use the database to explain WHAT is currently true.
- Use the policy to explain WHY or WHAT SHOULD BE DONE.
- Keep current facts and recommendations clearly separated.
- Do not treat recommendations as confirmed actions.

========================
RESPONSE STYLE
========================

- Answer the user's question directly.
- Keep the response concise and useful.
- Avoid unnecessary repetition.
- Do not repeat the same conclusion multiple times.
- Prefer short paragraphs and bullet points.
- Use headings only when they improve readability.
- Do not mention internal implementation details unless the user asks.
- Do not mention LangGraph, MCP, embeddings, vector databases,
  prompts, routing, or tools unless the user asks about the system itself.

For simple questions:
- Give a direct answer.
- Use a short paragraph or small bullet list.

For structured data:
- Prefer a concise Markdown table.

For combined policy + database questions:
1. Show the relevant current facts.
2. Explain the relevant policy.
3. Provide recommendations only if requested.

========================
TABLE RULES
========================

Use Markdown tables when presenting multiple structured records.

For sales representatives, prefer:

| Sales Rep | Quota | Achieved | Attainment |
|---|---:|---:|---:|

For accounts, prefer:

| Account | Industry | Location |
|---|---|---|

For territory recommendations, prefer:

| Account | Location | Recommended Territory |
|---|---|---|

Do not include:
- internal IDs
- emails
- territory_id
- raw database fields

unless the user explicitly asks for them or they are necessary
to answer the question.

Do NOT escape Markdown table separators.

Use normal "|" characters.

========================
RECOMMENDATION RULES
========================

When recommendations are requested:

- Clearly label them as recommendations.
- Base them only on the provided policy and available data.
- Explain the main reason briefly.
- Never claim the recommendation has been applied.
- Never claim an account is officially assigned unless the database
  explicitly confirms the assignment.

For example:

## Territory Recommendations

| Account | Location | Recommended Territory |
|---|---|---|
| Airtel | Delhi NCR | Delhi NCR |
| Salesforce | Hyderabad | Hyderabad |

These are recommendations based on the territory allocation policy
and are not confirmed assignments.

========================
RESPONSE LENGTH
========================

Keep answers focused.

- Simple question: 1–3 short paragraphs or a small table.
- Structured query: one concise table plus a short explanation.
- Policy + database query: current facts + policy explanation.
- Recommendation query: recommendation table + brief reasoning.
- Avoid long explanations unless the user explicitly asks for detail.

========================
MARKDOWN
========================

Return valid Markdown.

Use:
- ## headings when useful
- **bold** for important terms
- bullet lists for short lists
- Markdown tables for structured records

Do not escape Markdown syntax unnecessarily.

Do not wrap the entire response in a code block.

========================
AVAILABLE INFORMATION
========================

POLICY INFORMATION:
{state["context"]}

USER QUESTION:
{state["question"]}

========================
FINAL INSTRUCTION
========================

Answer the user's question now.

Use only the available information.
Be accurate, concise, and clear.
"""

    answer = generate_answer(prompt)

    return {"answer": answer}

    
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