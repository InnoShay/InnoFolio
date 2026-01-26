"""
Chat endpoints for InnoFolio.
Handles user messages and returns AI responses.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from core.rag.pipeline import RAGPipeline
from core.safety.guardrails import check_input_safety, check_topic_boundaries


router = APIRouter()

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request payload."""
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response payload."""
    response: str
    sources: Optional[List[str]] = []
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return AI response.
    Uses RAG to retrieve relevant context and generate response.
    """
    # Safety check on input
    safety_result = await check_input_safety(request.message)
    if not safety_result["safe"]:
        return ChatResponse(
            response="I apologize, but I can't process that request. Let me know if you have questions about resumes, interviews, job search, or career growth!",
            sources=[],
            session_id=request.session_id or "default"
        )
    
    # Check topic boundaries
    boundary_result = await check_topic_boundaries(request.message)
    if not boundary_result["within_bounds"]:
        return ChatResponse(
            response=boundary_result["redirect_message"],
            sources=[],
            session_id=request.session_id or "default"
        )
    
    try:
        # Generate response using RAG pipeline
        result = await rag_pipeline.generate_response(
            query=request.message,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            response=result["response"],
            sources=result.get("sources", []),
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response for real-time typing effect.
    """
    # Safety checks
    safety_result = await check_input_safety(request.message)
    if not safety_result["safe"]:
        async def error_stream():
            yield f"data: {json.dumps({'content': 'I apologize, but I cannot process that request.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")
    
    boundary_result = await check_topic_boundaries(request.message)
    if not boundary_result["within_bounds"]:
        async def boundary_stream():
            yield f"data: {json.dumps({'content': boundary_result['redirect_message']})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(boundary_stream(), media_type="text/event-stream")
    
    # Stream response
    async def response_stream():
        async for chunk in rag_pipeline.generate_response_stream(
            query=request.message,
            conversation_history=request.conversation_history
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(response_stream(), media_type="text/event-stream")


@router.get("/suggestions")
async def get_suggestions():
    """Get starter prompt suggestions for new users."""
    return {
        "suggestions": [
            {
                "icon": "📄",
                "title": "Resume Review",
                "prompt": "How can I improve my resume for a software engineering role?"
            },
            {
                "icon": "🎯",
                "title": "Interview Prep",
                "prompt": "What are the most common interview questions for freshers?"
            },
            {
                "icon": "💼",
                "title": "Job Search",
                "prompt": "What's the best strategy for finding my first job?"
            },
            {
                "icon": "🗺️",
                "title": "Career Path",
                "prompt": "What skills should I learn to become a full-stack developer?"
            }
        ]
    }
