"""
Authentication API endpoints.
Handles user signup, login, logout, and profile management.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from core.database.supabase_client import get_supabase
from core.auth import require_auth, User, get_current_user

router = APIRouter()


class SignUpRequest(BaseModel):
    """Sign up request payload."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    """Profile update request payload."""
    full_name: Optional[str] = None
    career_stage: Optional[str] = None  # 'student', 'fresher', 'experienced', 'career_changer'
    target_role: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Register a new user account.
    """
    try:
        supabase = get_supabase()
        
        # Sign up the user
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name
                }
            }
        })
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create account"
            )
        
        # Create profile entry
        if response.session:
            supabase.table("profiles").upsert({
                "id": response.user.id,
                "full_name": request.full_name
            }).execute()
        
        return AuthResponse(
            access_token=response.session.access_token if response.session else "",
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": request.full_name
            }
        )
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user is None or response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get profile data
        profile = supabase.table("profiles").select("*").eq(
            "id", response.user.id
        ).single().execute()
        
        profile_data = profile.data if profile.data else {}
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": profile_data.get("full_name"),
                "career_stage": profile_data.get("career_stage"),
                "target_role": profile_data.get("target_role")
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/auth/logout")
async def logout(user: User = Depends(require_auth)):
    """
    Logout the current user.
    """
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.get("/auth/me")
async def get_me(user: User = Depends(require_auth)):
    """
    Get current authenticated user.
    """
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "career_stage": user.career_stage,
        "target_role": user.target_role
    }


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    user: User = Depends(require_auth)
):
    """
    Update user profile.
    """
    try:
        supabase = get_supabase()
        
        update_data = {}
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.career_stage is not None:
            update_data["career_stage"] = request.career_stage
        if request.target_role is not None:
            update_data["target_role"] = request.target_role
        
        if update_data:
            response = supabase.table("profiles").upsert({
                "id": user.id,
                **update_data
            }).execute()
        
        return {
            "message": "Profile updated successfully",
            "profile": {
                "id": user.id,
                "email": user.email,
                **update_data
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
