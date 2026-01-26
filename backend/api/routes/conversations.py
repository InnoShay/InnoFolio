"""
Conversation API endpoints.
Handles chat history storage and retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from core.database.supabase_client import get_supabase
from core.auth import require_auth, User, get_current_user

router = APIRouter()


class ConversationCreate(BaseModel):
    """Create conversation request."""
    title: Optional[str] = "New Chat"


class MessageCreate(BaseModel):
    """Create message request."""
    role: str  # 'user' or 'assistant'
    content: str


class ConversationResponse(BaseModel):
    """Conversation response."""
    id: str
    title: str
    is_pinned: bool
    created_at: str
    updated_at: str
    message_count: Optional[int] = 0


class MessageResponse(BaseModel):
    """Message response."""
    id: str
    role: str
    content: str
    is_saved: bool
    created_at: str


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(user: User = Depends(require_auth)):
    """
    List all conversations for the current user.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table("conversations").select(
            "*, messages(count)"
        ).eq("user_id", user.id).order(
            "updated_at", desc=True
        ).execute()
        
        conversations = []
        for conv in response.data or []:
            conversations.append(ConversationResponse(
                id=conv["id"],
                title=conv["title"] or "New Chat",
                is_pinned=conv.get("is_pinned", False),
                created_at=conv["created_at"],
                updated_at=conv["updated_at"],
                message_count=conv.get("messages", [{}])[0].get("count", 0) if conv.get("messages") else 0
            ))
        
        return conversations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversations: {str(e)}"
        )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    user: User = Depends(require_auth)
):
    """
    Create a new conversation.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table("conversations").insert({
            "user_id": user.id,
            "title": request.title
        }).execute()
        
        conv = response.data[0]
        
        return ConversationResponse(
            id=conv["id"],
            title=conv["title"],
            is_pinned=conv.get("is_pinned", False),
            created_at=conv["created_at"],
            updated_at=conv["updated_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: User = Depends(require_auth)
):
    """
    Get a conversation with all its messages.
    """
    try:
        supabase = get_supabase()
        
        # Get conversation
        conv_response = supabase.table("conversations").select("*").eq(
            "id", conversation_id
        ).eq("user_id", user.id).single().execute()
        
        if not conv_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        msg_response = supabase.table("messages").select("*").eq(
            "conversation_id", conversation_id
        ).order("created_at", desc=False).execute()
        
        messages = [
            MessageResponse(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                is_saved=msg.get("is_saved", False),
                created_at=msg["created_at"]
            )
            for msg in (msg_response.data or [])
        ]
        
        conv = conv_response.data
        return {
            "id": conv["id"],
            "title": conv["title"],
            "is_pinned": conv.get("is_pinned", False),
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages")
async def add_message(
    conversation_id: str,
    request: MessageCreate,
    user: User = Depends(require_auth)
):
    """
    Add a message to a conversation.
    """
    try:
        supabase = get_supabase()
        
        # Verify conversation belongs to user
        conv_check = supabase.table("conversations").select("id").eq(
            "id", conversation_id
        ).eq("user_id", user.id).execute()
        
        if not conv_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Add message
        response = supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "role": request.role,
            "content": request.content
        }).execute()
        
        # Update conversation timestamp and title if first message
        if request.role == "user":
            # Auto-generate title from first user message
            title = request.content[:50] + "..." if len(request.content) > 50 else request.content
            supabase.table("conversations").update({
                "updated_at": datetime.utcnow().isoformat(),
                "title": title
            }).eq("id", conversation_id).execute()
        
        msg = response.data[0]
        return MessageResponse(
            id=msg["id"],
            role=msg["role"],
            content=msg["content"],
            is_saved=msg.get("is_saved", False),
            created_at=msg["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(require_auth)
):
    """
    Delete a conversation and all its messages.
    """
    try:
        supabase = get_supabase()
        
        # Verify ownership and delete
        response = supabase.table("conversations").delete().eq(
            "id", conversation_id
        ).eq("user_id", user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"message": "Conversation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.patch("/conversations/{conversation_id}/pin")
async def toggle_pin(
    conversation_id: str,
    user: User = Depends(require_auth)
):
    """
    Toggle pin status of a conversation.
    """
    try:
        supabase = get_supabase()
        
        # Get current pin status
        conv = supabase.table("conversations").select("is_pinned").eq(
            "id", conversation_id
        ).eq("user_id", user.id).single().execute()
        
        if not conv.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        new_status = not conv.data.get("is_pinned", False)
        
        supabase.table("conversations").update({
            "is_pinned": new_status
        }).eq("id", conversation_id).execute()
        
        return {"is_pinned": new_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle pin: {str(e)}"
        )


@router.patch("/messages/{message_id}/save")
async def toggle_save_message(
    message_id: str,
    user: User = Depends(require_auth)
):
    """
    Toggle save status of a message.
    """
    try:
        supabase = get_supabase()
        
        # Get message and verify ownership through conversation
        msg = supabase.table("messages").select(
            "*, conversations!inner(user_id)"
        ).eq("id", message_id).single().execute()
        
        if not msg.data or msg.data["conversations"]["user_id"] != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        new_status = not msg.data.get("is_saved", False)
        
        supabase.table("messages").update({
            "is_saved": new_status
        }).eq("id", message_id).execute()
        
        return {"is_saved": new_status}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save message: {str(e)}"
        )
