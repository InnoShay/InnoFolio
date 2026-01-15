"""
Resume API endpoints.
Handles file upload, parsing, and AI-powered analysis.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel
from typing import Optional, List
import io
import json
from pypdf import PdfReader
from docx import Document
from core.database.supabase_client import get_supabase
from core.auth import require_auth, User
from core.config import get_settings
import google.generativeai as genai

router = APIRouter()
settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


class ResumeAnalysis(BaseModel):
    """Resume analysis response."""
    id: str
    filename: str
    score: int  # 1-100
    summary: str
    sections: dict
    improvements: List[str]
    strengths: List[str]
    keywords: List[str]


class ResumeListItem(BaseModel):
    """Resume list item."""
    id: str
    filename: str
    score: Optional[int]
    created_at: str


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
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
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse DOCX: {str(e)}"
        )


async def analyze_resume_with_ai(resume_text: str, user: User) -> dict:
    """
    Analyze resume using Gemini AI.
    Returns structured analysis with score, sections, and improvements.
    """
    prompt = f"""You are an expert resume reviewer and career coach. Analyze the following resume and provide a comprehensive evaluation.

Resume Text:
---
{resume_text}
---

User Context:
- Career Stage: {user.career_stage or 'Not specified'}
- Target Role: {user.target_role or 'Not specified'}

Provide your analysis in the following JSON format (respond ONLY with valid JSON, no markdown):
{{
    "score": <number 1-100>,
    "summary": "<2-3 sentence overall assessment>",
    "sections": {{
        "contact_info": {{
            "present": <true/false>,
            "score": <1-10>,
            "feedback": "<specific feedback>"
        }},
        "summary_objective": {{
            "present": <true/false>,
            "score": <1-10>,
            "feedback": "<specific feedback>"
        }},
        "experience": {{
            "present": <true/false>,
            "score": <1-10>,
            "feedback": "<specific feedback>",
            "has_quantified_achievements": <true/false>
        }},
        "education": {{
            "present": <true/false>,
            "score": <1-10>,
            "feedback": "<specific feedback>"
        }},
        "skills": {{
            "present": <true/false>,
            "score": <1-10>,
            "feedback": "<specific feedback>",
            "relevant_skills": ["<skill1>", "<skill2>", ...]
        }},
        "formatting": {{
            "score": <1-10>,
            "feedback": "<feedback on layout, readability, length>"
        }}
    }},
    "strengths": [
        "<strength 1>",
        "<strength 2>",
        "<strength 3>"
    ],
    "improvements": [
        "<specific improvement 1>",
        "<specific improvement 2>",
        "<specific improvement 3>",
        "<specific improvement 4>",
        "<specific improvement 5>"
    ],
    "keywords": ["<keyword1>", "<keyword2>", ...],
    "ats_compatibility": {{
        "score": <1-10>,
        "issues": ["<issue1>", "<issue2>", ...]
    }},
    "grammar_issues": [
        {{
            "original": "<original text>",
            "suggested": "<corrected text>",
            "issue": "<explanation>"
        }}
    ]
}}

Be specific, actionable, and constructive in your feedback. Focus on:
1. Impact metrics and quantified achievements
2. ATS optimization
3. Relevance to target role
4. Professional language and grammar
5. Overall presentation"""

    try:
        model = genai.GenerativeModel(settings.llm_model)
        response = model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        analysis = json.loads(response_text)
        return analysis
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a basic analysis
        return {
            "score": 50,
            "summary": "Unable to fully analyze the resume. Please ensure it contains clear sections.",
            "sections": {},
            "strengths": ["Resume uploaded successfully"],
            "improvements": ["Add more details to your resume for a complete analysis"],
            "keywords": [],
            "ats_compatibility": {"score": 5, "issues": []},
            "grammar_issues": []
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(require_auth)
):
    """
    Upload a resume file (PDF or DOCX).
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024
    content = await file.read()
    
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Extract text based on file type
    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(content)
    else:
        extracted_text = extract_text_from_docx(content)
    
    if not extracted_text or len(extracted_text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract sufficient text from the resume"
        )
    
    try:
        supabase = get_supabase()
        
        # Save resume record (without file storage for now)
        response = supabase.table("resumes").insert({
            "user_id": user.id,
            "filename": file.filename,
            "extracted_text": extracted_text
        }).execute()
        
        resume = response.data[0]
        
        return {
            "id": resume["id"],
            "filename": file.filename,
            "text_length": len(extracted_text),
            "message": "Resume uploaded successfully. Use /resume/analyze to get AI analysis."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save resume: {str(e)}"
        )


@router.post("/resume/{resume_id}/analyze")
async def analyze_resume(
    resume_id: str,
    user: User = Depends(require_auth)
):
    """
    Analyze an uploaded resume with AI.
    """
    try:
        supabase = get_supabase()
        
        # Get resume
        response = supabase.table("resumes").select("*").eq(
            "id", resume_id
        ).eq("user_id", user.id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume = response.data
        
        # Run AI analysis
        analysis = await analyze_resume_with_ai(resume["extracted_text"], user)
        
        # Save analysis results
        supabase.table("resumes").update({
            "analysis": analysis,
            "score": analysis.get("score", 0)
        }).eq("id", resume_id).execute()
        
        return {
            "id": resume_id,
            "filename": resume["filename"],
            **analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/resume/analyze-direct")
async def analyze_resume_direct(
    file: UploadFile = File(...),
    user: User = Depends(require_auth)
):
    """
    Upload and analyze a resume in one step.
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )
    
    # Read and validate file
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Extract text
    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(content)
    else:
        extracted_text = extract_text_from_docx(content)
    
    if not extracted_text or len(extracted_text) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract sufficient text from the resume"
        )
    
    # Analyze with AI
    analysis = await analyze_resume_with_ai(extracted_text, user)
    
    try:
        supabase = get_supabase()
        
        # Save resume with analysis
        response = supabase.table("resumes").insert({
            "user_id": user.id,
            "filename": file.filename,
            "extracted_text": extracted_text,
            "analysis": analysis,
            "score": analysis.get("score", 0)
        }).execute()
        
        resume = response.data[0]
        
        return {
            "id": resume["id"],
            "filename": file.filename,
            **analysis
        }
    except Exception as e:
        # Return analysis even if save fails
        return {
            "id": None,
            "filename": file.filename,
            **analysis,
            "warning": "Analysis complete but failed to save to database"
        }


@router.get("/resumes", response_model=List[ResumeListItem])
async def list_resumes(user: User = Depends(require_auth)):
    """
    List all resumes for the current user.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table("resumes").select(
            "id, filename, score, created_at"
        ).eq("user_id", user.id).order(
            "created_at", desc=True
        ).execute()
        
        return [
            ResumeListItem(
                id=r["id"],
                filename=r["filename"],
                score=r.get("score"),
                created_at=r["created_at"]
            )
            for r in (response.data or [])
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resumes: {str(e)}"
        )


@router.get("/resume/{resume_id}")
async def get_resume(
    resume_id: str,
    user: User = Depends(require_auth)
):
    """
    Get a resume with its analysis.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table("resumes").select("*").eq(
            "id", resume_id
        ).eq("user_id", user.id).single().execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume = response.data
        analysis = resume.get("analysis") or {}
        
        return {
            "id": resume["id"],
            "filename": resume["filename"],
            "score": resume.get("score"),
            "created_at": resume["created_at"],
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )


@router.delete("/resume/{resume_id}")
async def delete_resume(
    resume_id: str,
    user: User = Depends(require_auth)
):
    """
    Delete a resume.
    """
    try:
        supabase = get_supabase()
        
        response = supabase.table("resumes").delete().eq(
            "id", resume_id
        ).eq("user_id", user.id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        return {"message": "Resume deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )
