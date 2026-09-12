# AI Sales Planning & Decision Assistant

An AI-powered sales planning assistant that combines **LLM reasoning, RAG, semantic search, PostgreSQL/pgvector, LangGraph, MCP, and business tools** to help sales teams analyze accounts, territories, and sales performance.

The project is designed as a production-style AI application with a simple architecture and clear separation between business data, company policies, and AI reasoning.

---

## Problem

Sales planning often requires combining information from different sources:

- Company policies and guidelines
- Sales account information
- Territory information
- Sales representative performance
- Quota attainment
- Account assignment status

A traditional application can query the database, but it cannot easily understand policy documents and combine them with live business data.

This project solves that problem by combining:

**RAG + Business Tools + MCP + LangGraph + LLM**

---

## Features

- LLM-powered question answering
- Retrieval-Augmented Generation (RAG)
- Semantic search using embeddings
- PostgreSQL with pgvector
- BGE embeddings (`BAAI/bge-base-en-v1.5`)
- LangGraph workflow orchestration
- Dynamic question routing
- MCP-based business tools
- FastAPI backend
- Next.js frontend
- Read-only business tools
- Source tracking
- Tool usage tracking
- Basic AI guardrails
- Human-in-the-loop recommendations

---

## Example Questions

### Policy question

> What is the territory allocation policy?

The system routes the question to **RAG** and retrieves the relevant policy documents.

### Business data question

> Which sales reps are below 70% quota?

The system routes the question to a **business tool** that retrieves current data from PostgreSQL.

### Account question

> Show me unassigned enterprise accounts.

The system uses an MCP business tool to retrieve the current account data.

### Combined AI planning question

> Find unassigned enterprise accounts and recommend potential territories based on the territory allocation policy.

This is the main showcase workflow.

The system combines:

- RAG for territory policy
- MCP tool for account data
- LangGraph for orchestration
- LLM for generating the recommendation

---

## Architecture

```text
                    ┌─────────────────┐
                    │    Next.js UI   │
                    └────────┬────────┘
                             │
                             │ HTTP
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    LangGraph    │
                    │     Router      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
            RAG          MCP Tools       RAG + Tool
              │              │              │
              ▼              ▼              ▼
        pgvector DB     MCP Server      Combined Context
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                           LLM
                             │
                             ▼
                         Answer





AI Workflow

The system first analyzes the user's question and selects one of three routes:

RAG
Tool
RAG + Tool



RAG

Used when the question requires company policies, rules, or documented knowledge.
Question
   ↓
Embedding
   ↓
pgvector semantic search
   ↓
Relevant document chunks
   ↓
LLM
   ↓
Answer



Tool

Used when the question requires current structured business data.


Question
   ↓
LangGraph
   ↓
MCP Client
   ↓
MCP Server
   ↓
Business Tool
   ↓
PostgreSQL
   ↓
LLM
   ↓
Answer






RAG + Tool

Used when the question requires both policy knowledge and current database information.


                 Question
                    ↓
                LangGraph
                    ↓
          ┌─────────┴─────────┐
          ↓                   ↓
         RAG              MCP Tool
          ↓                   ↓
      Policy Docs         PostgreSQL
          │                   │
          └─────────┬─────────┘
                    ↓
               Combined Context
                    ↓
                   LLM
                    ↓
                 Answer




RAG Pipeline

The project uses: BAAI/bge-base-en-v1.5

The embedding model converts document text into a 768-dimensional vector.

Document
   ↓
Chunking
   ↓
Embedding Model
   ↓
768-dimensional vector
   ↓
PostgreSQL + pgvector


During retrieval:

User Question
   ↓
Question Embedding
   ↓
Cosine Similarity Search
   ↓
Top Relevant Chunks
   ↓
LLM Context




Database

The project uses PostgreSQL with pgvector.

Main tables:

territories
sales_reps
accounts
documents
document_chunks



Structured business data

PostgreSQL is the source of truth for:

Sales representatives
Accounts
Territories
Quotas
Achievements
Assignments
Policy knowledge

Policy documents are stored and embedded for semantic retrieval.

Example documents:

territory-policy.md
quota-policy.md
account-management-policy.md
sales-planning-guide.md



Business Tools

The application exposes read-only business tools through MCP.

Quota attainment


Finds sales representatives below a specified quota threshold.

Example:

Which sales reps are below 70% quota?
Unassigned enterprise accounts
unassigned_enterprise_accounts

Returns enterprise accounts that currently have no assigned sales representative.

Accounts by territory
accounts_by_territory

Retrieves accounts associated with a specific territory.

MCP

Model Context Protocol (MCP) provides a standardized interface for exposing the application's business tools.

Architecture:

LangGraph
    ↓
MCP Client
    ↓
MCP Server
    ↓
Business Tools
    ↓
PostgreSQL

MCP is not required for LangGraph itself.

It is used here to make the business tools standardized and reusable by compatible AI clients.

LangGraph

LangGraph is used to orchestrate the AI workflow.

The current graph contains:

START
  ↓
Analyze Question
  ↓
Route
 ┌───────────────┬───────────────┐
 ↓               ↓               ↓
RAG            Tool          RAG + Tool
 └───────────────┴───────────────┘
                 ↓
          Generate Answer
                 ↓
                END

The router determines whether the question requires:

rag
tool
rag_and_tool
API
Health Check
GET /api/health

Example response:

{
  "status": "ok"
}
Chat
POST /api/chat

Request:

{
  "question": "Show me unassigned enterprise accounts."
}

Response:

{
  "answer": "...",
  "route": "tool",
  "sources": [],
  "tools_used": [
    "unassigned_enterprise_accounts"
  ]
}

For a combined question:

{
  "answer": "...",
  "route": "rag_and_tool",
  "sources": [
    "territory-policy.md",
    "account-management-policy.md",
    "sales-planning-guide.md"
  ],
  "tools_used": [
    "unassigned_enterprise_accounts"
  ]
}
Guardrails

The assistant follows several basic safety and reliability rules:

Business facts come from the database.
Policies come from approved documents.
Tools are read-only.
No arbitrary SQL is exposed to the LLM.
Tool inputs are validated.
API keys and secrets are never exposed.
Internal stack traces are not returned to users.
The assistant should not invent missing information.
Recommendations are clearly presented as recommendations.
The system does not automatically modify account assignments.
Territory assignment is not confused with sales representative assignment.
Human approval is required before changing assignments.
Project Structure
ai-sales-planning-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── graph/
│   │   ├── rag/
│   │   ├── services/
│   │   ├── tools/
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── mcp_client.py
│   │   └── mcp_server.py
│   │
│   └── requirements.txt
│
├── frontend/
│
├── data/
│   └── documents/
│       ├── territory-policy.md
│       ├── quota-policy.md
│       ├── account-management-policy.md
│       └── sales-planning-guide.md
│
├── .env.example
├── .gitignore
└── README.md
Environment Variables

Create a .env file in the backend directory.

Example:

DATABASE_URL=your_database_connection_string
GROQ_API_KEY=your_groq_api_key

Never commit .env or API keys to Git.

Local Development
Backend
cd backend

Create a virtual environment:

python -m venv .venv

Activate it on Windows:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Start FastAPI:

uvicorn app.main:app --reload

API:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Frontend
cd frontend

Install dependencies:

pnpm install

Start the development server:

pnpm dev

The Next.js application will run locally using the development server.

Testing

Current workflow testing can be run with:

python -m app.graph.test_workflow

The main showcase question is:

Find unassigned enterprise accounts and recommend potential territories based on the territory allocation policy.

Expected route:

rag_and_tool

Expected tool:

unassigned_enterprise_accounts

Expected sources include:

territory-policy.md
account-management-policy.md
sales-planning-guide.md
Deployment

Planned deployment architecture:

Next.js
   ↓
Vercel

FastAPI
   ↓
Render

PostgreSQL + pgvector
   ↓
Supabase
Why This Architecture?

The application separates three different responsibilities:

PostgreSQL

Source of truth for structured business data.

RAG

Source of truth for company policies and documented knowledge.

MCP Tools

Controlled interface for accessing business operations/data.

LangGraph

Orchestrates the overall AI workflow.

LLM

Understands the user's question and generates the final response.

This separation makes the system easier to reason about, test, and extend.

Future Improvements

Possible future improvements include:

Better evaluation of RAG retrieval quality
Automated evaluation datasets
More business tools
Improved prompt injection protection
Authentication and authorization
Role-based access control
Streaming responses
Conversation history
Better observability
Production monitoring
More advanced territory recommendations
Human approval workflows
Automated deployment pipelines
Tech Stack
Frontend
Next.js
React
TypeScript
Backend
Python
FastAPI
LangGraph
AI
Groq
LLM
Sentence Transformers
BAAI BGE embeddings
RAG
Semantic Search
Data
PostgreSQL
pgvector
Supabase
AI Tooling
Model Context Protocol (MCP)
Deployment
Vercel
Render
Supabase
Project Goal

This project demonstrates how a modern full-stack application can integrate AI capabilities without turning the system into an overly complex multi-agent architecture.

The focus is on:

Practical AI engineering → reliable data access → controlled tools → useful business decisions.


For the **first commit**, this README is good enough even though the frontend isn't finished yet. We can update the README after the frontend and deployment are completed.

One thing I'd change later: the README currently says deployment is “planned,” which is correct right now. After we deploy, we'll update that section with the live links.

Now save it as:

```text
D:\App\ai-sales-planning-assistant\README.md

