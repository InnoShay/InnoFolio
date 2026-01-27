"""
Safety guardrails for InnoFolio.
Handles input validation, topic boundaries, and content filtering.
"""
import re
from typing import Dict, List

# Topics that InnoFolio should NOT answer
OFF_TOPIC_PATTERNS = [
    # Legal/Immigration
    r'\b(visa|immigration|green\s*card|h1b|h-1b|work\s*permit|citizenship|asylum)\b',
    # Financial
    r'\b(invest|stock|crypto|bitcoin|trading|forex|mutual\s*fund|retirement\s*fund|401k)\b',
    # Medical
    r'\b(diagnos|symptom|medication|prescription|treatment\s+for|mental\s*health\s*disorder)\b',
    # Guarantees
    r'\b(guarantee|promise|definitel?y?\s+get|100%\s+sure|will\s+get\s+hired)\b',
]

# Harmful content patterns
HARMFUL_PATTERNS = [
    r'\b(kill|murder|suicide|self.?harm|hate|racist|sexist)\b',
    r'\b(hack|exploit|steal|fraud|scam)\b',
    r'<script|javascript:|data:text/html',  # XSS attempts
]

# Redirect messages for different off-topic categories
REDIRECT_MESSAGES = {
    "legal": "I appreciate you asking, but legal and immigration questions are outside my expertise. I'd recommend consulting with an immigration attorney. However, I'd love to help you with your resume, interview prep, or job search strategy!",
    "financial": "That's an important question, but financial investment advice is outside my scope. A financial advisor would be the best resource for that. Would you like help with career-related topics like resume building or interview preparation instead?",
    "medical": "I understand that's important to you, but I'm not qualified to give medical or mental health advice. Please reach out to a healthcare professional. Is there anything career-related I can help you with?",
    "general": "I appreciate you asking! That's outside my expertise as a career coach. I focus on resumes, interviews, job search, and career growth. Would you like help with any of those instead?"
}


async def check_input_safety(message: str) -> Dict:
    """
    Check if user input contains harmful content.
    
    Args:
        message: User's input message
    
    Returns:
        Dict with 'safe' boolean and 'reason' if unsafe
    """
    message_lower = message.lower()
    
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return {
                "safe": False,
                "reason": "harmful_content"
            }
    
    # Check for prompt injection attempts
    injection_patterns = [
        r'ignore\s+(previous|all)\s+(instructions|prompts)',
        r'you\s+are\s+now\s+[a-z]+',
        r'pretend\s+(to\s+be|you\'re)',
        r'jailbreak',
        r'system\s*prompt',
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return {
                "safe": False,
                "reason": "prompt_injection"
            }
    
    return {"safe": True}


async def check_topic_boundaries(message: str) -> Dict:
    """
    Check if the message is within InnoFolio's topic boundaries.
    
    Args:
        message: User's input message
    
    Returns:
        Dict with 'within_bounds' boolean and 'redirect_message' if off-topic
    """
    message_lower = message.lower()
    
    # Check for legal/immigration topics
    if re.search(r'\b(visa|immigration|green\s*card|h1b|work\s*permit|citizenship)\b', message_lower):
        return {
            "within_bounds": False,
            "category": "legal",
            "redirect_message": REDIRECT_MESSAGES["legal"]
        }
    
    # Check for financial investment topics
    if re.search(r'\b(invest|stock|crypto|bitcoin|trading|forex|401k)\b', message_lower):
        return {
            "within_bounds": False,
            "category": "financial",
            "redirect_message": REDIRECT_MESSAGES["financial"]
        }
    
    # Check for medical topics
    if re.search(r'\b(diagnos|symptom|medication|prescription|mental\s*health\s*disorder)\b', message_lower):
        return {
            "within_bounds": False,
            "category": "medical",
            "redirect_message": REDIRECT_MESSAGES["medical"]
        }
    
    return {"within_bounds": True}


def sanitize_input(message: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        message: Raw user input
    
    Returns:
        Sanitized message
    """
    # Remove any HTML/script tags
    message = re.sub(r'<[^>]+>', '', message)
    
    # Remove excessive whitespace
    message = ' '.join(message.split())
    
    # Limit length
    max_length = 2000
    if len(message) > max_length:
        message = message[:max_length]
    
    return message
