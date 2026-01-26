"""Health check endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "InnoFolio API",
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to InnoFolio API",
        "docs": "/docs"
    }
