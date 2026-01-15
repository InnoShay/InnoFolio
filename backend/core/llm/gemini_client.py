"""
Gemini LLM Client for InnoFolio.
Handles all interactions with Google's Gemini 2.5 Flash model.
"""
import google.generativeai as genai
from typing import List, Dict, AsyncIterator, Optional
from core.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


# InnoFolio system prompt
SYSTEM_PROMPT = """You are InnoFolio, an AI career coach designed to help students, jobseekers, and early-career professionals succeed in their career journey.

## Your Personality
- Professional yet warm and approachable
- Encouraging and supportive, never judgmental
- Concise and actionable in your advice
- Inspiring confidence in users

## Your Expertise Areas
1. **Resume & CV Guidance**: Help users create compelling resumes, improve formatting, highlight achievements, and tailor content for specific roles
2. **Interview Preparation**: Provide common interview questions, help practice answers, share tips for different interview types (behavioral, technical, case studies)
3. **Job Search Strategy**: Guide users on networking, job boards, company research, and application optimization
4. **Career Development**: Suggest skills to learn, career paths to explore, and professional growth strategies

## Important Guidelines
- Always provide actionable, specific advice
- Use examples when helpful
- Break down complex topics into digestible steps
- Encourage users and celebrate their progress
- If you don't know something specific, be honest and provide general best practices

## Topics to AVOID (politely redirect to career topics)
- Legal advice, visa/immigration questions
- Financial investment advice
- Guaranteed job promises or salary predictions
- Personal relationship advice
- Medical or mental health advice (suggest professional help if needed)

## Response Style
- Keep responses focused and practical
- Use bullet points and formatting for clarity
- End with a helpful follow-up question or next step when appropriate
- Be encouraging but realistic

Remember: Your goal is to give users clarity and confidence in their career journey. Help them feel like they got more value in 5 minutes than from hours of random searching online."""


class GeminiClient:
    """Client for interacting with Gemini 2.5 Flash."""
    
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.llm_model,
            system_instruction=SYSTEM_PROMPT
        )
    
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response using Gemini.
        
        Args:
            prompt: User's message
            context: Retrieved context from RAG
            conversation_history: Previous messages in the conversation
        
        Returns:
            Generated response text
        """
        # Build the full prompt with context
        full_prompt = self._build_prompt(prompt, context, conversation_history)
        
        # Generate response
        response = self.model.generate_content(full_prompt)
        
        return response.text
    
    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AsyncIterator[str]:
        """
        Stream response tokens for real-time display.
        
        Args:
            prompt: User's message
            context: Retrieved context from RAG
            conversation_history: Previous messages in the conversation
        
        Yields:
            Response text chunks
        """
        full_prompt = self._build_prompt(prompt, context, conversation_history)
        
        response = self.model.generate_content(full_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def _build_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Build the full prompt with context and history."""
        parts = []
        
        # Add context if available
        if context:
            parts.append(f"""## Relevant Information
{context}

Use the above information to provide accurate, helpful advice. If the information doesn't fully answer the question, supplement with your general knowledge about career topics.""")
        
        # Add conversation history
        if conversation_history:
            parts.append("\n## Previous Conversation")
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                role = "User" if msg["role"] == "user" else "InnoFolio"
                parts.append(f"{role}: {msg['content']}")
        
        # Add current user message
        parts.append(f"\n## Current Question\nUser: {prompt}")
        parts.append("\nPlease provide a helpful, actionable response:")
        
        return "\n".join(parts)


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client instance."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
