"""
Authentication middleware and dependencies.
Handles JWT verification and user session management.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from core.config import get_settings
from core.database.supabase_client import get_supabase

settings = get_settings()
security = HTTPBearer(auto_error=False)


class User(BaseModel):
    """User model for authenticated requests."""
    id: str
    email: str
    full_name: Optional[str] = None
    career_stage: Optional[str] = None
    target_role: Optional[str] = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token.
    Returns None if no valid token is provided.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    try:
        # Verify the JWT with Supabase
        supabase = get_supabase()
        response = supabase.auth.get_user(token)
        
        if response.user is None:
            return None
        
        user_data = response.user
        
        # Get additional profile data
        profile = supabase.table("profiles").select("*").eq(
            "id", user_data.id
        ).single().execute()
        
        profile_data = profile.data if profile.data else {}
        
        return User(
            id=user_data.id,
            email=user_data.email,
            full_name=profile_data.get("full_name"),
            career_stage=profile_data.get("career_stage"),
            target_role=profile_data.get("target_role")
        )
    except Exception as e:
        print(f"Auth error: {e}")
        return None


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Require authenticated user. Raises 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_current_user(credentials)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
