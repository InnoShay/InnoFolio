"""
InnoFolio Backend - FastAPI Application
AI-powered career coaching chatbot
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import chat, health, auth, conversations, resume
from core.rag.vector_store import initialize_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    # Initialize vector store
    await initialize_vector_store()
    yield
    # Cleanup on shutdown


app = FastAPI(
    title="InnoFolio API",
    description="AI-powered career coaching chatbot API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "*",  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
app.include_router(resume.router, prefix="/api", tags=["Resume"])
