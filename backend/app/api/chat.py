from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph.workflow import graph

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    route: str
    sources: list[str]
    tools_used: list[str]


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = graph.invoke(
            {
                "question": request.question,
                "route": "",
                "context": "",
                "answer": "",
                "sources": [],
                "tools_used": [],
            }
        )

        return {
            "answer": result["answer"],
            "route": result["route"],
            "sources": result["sources"],
            "tools_used": result["tools_used"],
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to process the request.",
        ) from error