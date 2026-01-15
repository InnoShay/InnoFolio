"""
RAG Pipeline for InnoFolio.
Combines retrieval and generation for accurate, grounded responses.
"""
from typing import List, Dict, Optional, AsyncIterator

from core.rag.vector_store import search_documents
from core.llm.gemini_client import get_gemini_client


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.
    Retrieves relevant context and generates responses.
    """
    
    def __init__(self):
        self.llm = get_gemini_client()
        self.retrieval_k = 5
        self.min_relevance_score = 0.7
    
    async def generate_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate a response using RAG.
        
        Args:
            query: User's question
            conversation_history: Previous messages
        
        Returns:
            Dict with response and sources
        """
        # Retrieve relevant documents
        documents = await search_documents(query, n_results=self.retrieval_k)
        
        # Filter by relevance (lower distance = more relevant)
        relevant_docs = [
            doc for doc in documents 
            if doc.get("distance", 1) < (1 - self.min_relevance_score)
        ]
        
        # Build context from retrieved documents
        context = None
        sources = []
        
        if relevant_docs:
            context_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                context_parts.append(f"[Source {i}]: {doc['content']}")
                if doc.get('metadata', {}).get('title'):
                    sources.append(doc['metadata']['title'])
            context = "\n\n".join(context_parts)
        
        # Generate response
        response = await self.llm.generate(
            prompt=query,
            context=context,
            conversation_history=conversation_history
        )
        
        return {
            "response": response,
            "sources": sources,
            "context_used": bool(context)
        }
    
    async def generate_response_stream(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> AsyncIterator[str]:
        """
        Stream a response using RAG.
        
        Args:
            query: User's question
            conversation_history: Previous messages
        
        Yields:
            Response text chunks
        """
        # Retrieve relevant documents
        documents = await search_documents(query, n_results=self.retrieval_k)
        
        # Filter by relevance
        relevant_docs = [
            doc for doc in documents 
            if doc.get("distance", 1) < (1 - self.min_relevance_score)
        ]
        
        # Build context
        context = None
        if relevant_docs:
            context_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                context_parts.append(f"[Source {i}]: {doc['content']}")
            context = "\n\n".join(context_parts)
        
        # Stream response
        async for chunk in self.llm.generate_stream(
            prompt=query,
            context=context,
            conversation_history=conversation_history
        ):
            yield chunk
