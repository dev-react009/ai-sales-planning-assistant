import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.graph.workflow import graph
from app.services.chat_service import (
    clear_chat_messages,
    create_conversation,
    delete_conversation,
    get_chat_messages,
    get_conversations,
    save_chat_message,
)

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    conversation_id: str | None = None
    user_message_id: str | None = None


class ChatResponse(BaseModel):
    id: str | None = None
    conversation_id: str
    answer: str
    route: str
    sources: list[str]
    tools_used: list[str]


class MessageItem(BaseModel):
    id: str
    conversation_id: str | None = None
    role: str
    content: str
    route: str | None = None
    sources: list[str] = []
    tools_used: list[str] = []
    created_at: str | None = None


class ConversationItem(BaseModel):
    id: str
    title: str
    created_at: str | None = None
    updated_at: str | None = None


@router.get("/conversations", response_model=list[ConversationItem])
def list_conversations():
    try:
        return get_conversations()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve conversations: {str(error)}",
        ) from error


@router.post("/conversations/new")
def new_conversation():
    try:
        conv_id = create_conversation(title="New Chat")
        return {"conversation_id": conv_id, "title": "New Chat"}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to create conversation: {str(error)}",
        ) from error


@router.delete("/conversations/{conversation_id}")
def remove_conversation(conversation_id: str):
    try:
        delete_conversation(conversation_id)
        return {"status": "ok", "message": "Conversation deleted"}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to delete conversation: {str(error)}",
        ) from error


@router.get("/messages", response_model=list[MessageItem])
def list_messages(conversation_id: str | None = None):
    try:
        return get_chat_messages(conversation_id=conversation_id)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve chat messages: {str(error)}",
        ) from error


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # 1. Establish or create conversation thread
        conv_id = request.conversation_id
        if not conv_id:
            title = request.question.strip()[:40]
            if len(request.question.strip()) > 40:
                title += "..."
            conv_id = create_conversation(title=title)

        # 2. Save user question to database
        user_msg_id = request.user_message_id or str(uuid.uuid4())
        save_chat_message(
            role="user",
            content=request.question,
            conversation_id=conv_id,
            message_id=user_msg_id,
        )

        # 3. Invoke LangGraph agent pipeline
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

        # 4. Save assistant response to database
        asst_msg_id = str(uuid.uuid4())
        save_chat_message(
            role="assistant",
            content=result["answer"],
            conversation_id=conv_id,
            route=result["route"],
            sources=result["sources"],
            tools_used=result["tools_used"],
            message_id=asst_msg_id,
        )

        return {
            "id": asst_msg_id,
            "conversation_id": conv_id,
            "answer": result["answer"],
            "route": result["route"],
            "sources": result["sources"],
            "tools_used": result["tools_used"],
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to process the request: {str(error)}",
        ) from error


@router.delete("/messages")
def clear_messages(conversation_id: str | None = None):
    try:
        clear_chat_messages(conversation_id=conversation_id)
        return {"status": "ok", "message": "Chat history cleared successfully"}
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to clear chat history: {str(error)}",
        ) from error
