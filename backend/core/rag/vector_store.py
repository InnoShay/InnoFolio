"""
Vector Store initialization and management.
Uses ChromaDB for local development, with easy migration path to pgvector.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import google.generativeai as genai
from typing import List, Dict, Optional
import os

from core.config import get_settings

settings = get_settings()

# Global vector store instance
_collection = None


async def initialize_vector_store():
    """Initialize the ChromaDB vector store."""
    global _collection
    
    # Ensure directory exists
    os.makedirs(settings.chroma_persist_directory, exist_ok=True)
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_directory,
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    _collection = client.get_or_create_collection(
        name="innofolio_knowledge",
        metadata={"description": "InnoFolio career knowledge base"}
    )
    
    print(f"✅ Vector store initialized with {_collection.count()} documents")
    
    return _collection


def get_collection():
    """Get the current collection instance."""
    if _collection is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vector_store() first.")
    return _collection


class GeminiEmbeddings:
    """Wrapper for Gemini embeddings."""
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        self.model = settings.embedding_model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']


async def add_documents(
    documents: List[str],
    metadatas: Optional[List[Dict]] = None,
    ids: Optional[List[str]] = None
):
    """
    Add documents to the vector store.
    
    Args:
        documents: List of text documents
        metadatas: Optional metadata for each document
        ids: Optional unique IDs for each document
    """
    collection = get_collection()
    embeddings = GeminiEmbeddings()
    
    # Generate embeddings
    doc_embeddings = embeddings.embed_documents(documents)
    
    # Generate IDs if not provided
    if ids is None:
        ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]
    
    # Add to collection
    collection.add(
        embeddings=doc_embeddings,
        documents=documents,
        metadatas=metadatas or [{} for _ in documents],
        ids=ids
    )
    
    print(f"✅ Added {len(documents)} documents to vector store")


async def search_documents(
    query: str,
    n_results: int = 5,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """
    Search for relevant documents.
    
    Args:
        query: Search query
        n_results: Number of results to return
        filter_metadata: Optional metadata filter
    
    Returns:
        List of documents with scores and metadata
    """
    collection = get_collection()
    embeddings = GeminiEmbeddings()
    
    # Embed query
    query_embedding = embeddings.embed_query(query)
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata
    )
    
    # Format results
    documents = []
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            documents.append({
                "content": doc,
                "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                "distance": results['distances'][0][i] if results['distances'] else 0
            })
    
    return documents
