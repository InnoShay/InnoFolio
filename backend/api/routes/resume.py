"""
Resume API endpoints.
Handles file upload, text extraction, and AI-powered analysis chat.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel
import io
from pypdf import PdfReader
from docx import Document
from core.config import get_settings
import google.generativeai as genai

router = APIRouter()
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


class ResumeChatRequest(BaseModel):
    """Resume chat request."""
    message: str
    resume_text: str


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse PDF: {str(e)}"
        )


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file."""
    try:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse DOCX: {str(e)}"
        )


@router.post("/resume/extract")
async def extract_resume_text(file: UploadFile = File(...)):
    """
    Upload a resume and extract its text content.
    Returns the extracted text for further analysis.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Also check by extension for files without proper MIME type
    is_pdf = file.content_type == "application/pdf" or file.filename.lower().endswith(".pdf")
    is_docx = file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or file.filename.lower().endswith(".docx")
    
    if not (is_pdf or is_docx):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size (max 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Extract text based on file type
    if is_pdf:
        extracted_text = extract_text_from_pdf(content)
    else:
        extracted_text = extract_text_from_docx(content)
    
    if not extracted_text or len(extracted_text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract sufficient text from the resume. Please ensure the file is not empty or image-based."
        )
    
    return {
        "filename": file.filename,
        "text": extracted_text,
        "text_length": len(extracted_text)
    }


@router.post("/resume/chat")
async def chat_about_resume(request: ResumeChatRequest):
    """
    Chat with AI about the uploaded resume.
    Provides analysis, scoring, and feedback based on the resume content.
    """
    if not request.resume_text or len(request.resume_text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text is required"
        )
    
    system_prompt = """You are an expert resume reviewer and career coach with 15+ years of experience in HR and recruiting. 
You are analyzing a candidate's resume and providing helpful, actionable feedback.

Guidelines:
- Be specific and reference actual content from the resume
- Use markdown formatting for clarity (bold headers, bullet points, numbered lists)
- Be encouraging but honest about areas for improvement
- Provide actionable, specific suggestions
- Use professional language
- When scoring, be fair but rigorous (most resumes score 50-75)

Resume Content:
---
{resume}
---

Respond to the user's question about this resume."""

    try:
        model = genai.GenerativeModel(settings.llm_model)
        
        full_prompt = system_prompt.format(resume=request.resume_text) + f"\n\nUser Question: {request.message}"
        
        response = model.generate_content(full_prompt)
        
        return {
            "response": response.text
        }
    except Exception as e:
        print(f"Resume chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze resume. Please try again."
        )
