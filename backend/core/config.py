"""
Application settings using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    google_api_key: str = ""
    
    # Supabase (optional for MVP)
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Vector Store
    chroma_persist_directory: str = "./data/chroma"
    
    # LLM Settings
    llm_model: str = "gemini-2.5-flash"
    embedding_model: str = "models/text-embedding-004"
    
    # RAG Settings
    chunk_size: int = 500
    chunk_overlap: int = 100
    retrieval_k: int = 5
    
    # Safety
    enable_content_filter: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
