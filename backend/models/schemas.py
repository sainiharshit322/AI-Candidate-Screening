from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class CandidateBase(BaseModel):
    s_no: Optional[int] = None
    name: Optional[str] = None
    email: str
    college: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    best_ai_project: Optional[str] = None
    research_work: Optional[str] = None
    github_url: Optional[str] = None
    resume_url: Optional[str] = None
    stage: Optional[str] = "uploaded"

class CandidateCreate(CandidateBase):
    pass

class CandidateResponse(CandidateBase):
    id: str
    created_at: Optional[datetime] = None
    # Joined evaluation fields if present
    evaluation_id: Optional[str] = None
    total_score: Optional[float] = None
    ai_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    ai_strengths: Optional[List[str]] = None
    ai_gaps: Optional[List[str]] = None
    github_score: Optional[float] = None
    github_summary: Optional[str] = None
    test_la: Optional[float] = None
    test_code: Optional[float] = None

    class Config:
        from_attributes = True

class StageUpdate(BaseModel):
    stage: str

class JobDescriptionCreate(BaseModel):
    title: Optional[str] = "Job Description"
    content: str

class JobDescriptionResponse(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    created_at: Optional[datetime] = None

class EvaluateRequest(BaseModel):
    job_description_id: str

class EvaluationResponse(BaseModel):
    id: str
    candidate_id: str
    job_description_id: Optional[str] = None
    resume_text: Optional[str] = None
    ai_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    ai_strengths: Optional[List[str]] = None
    ai_gaps: Optional[List[str]] = None
    github_score: Optional[float] = None
    github_summary: Optional[str] = None
    test_la: Optional[float] = None
    test_code: Optional[float] = None
    total_score: Optional[float] = None
    created_at: Optional[datetime] = None

class UploadResponse(BaseModel):
    inserted: int
    updated: int

class UploadResultsResponse(BaseModel):
    updated: int
    unmatched_emails: List[str]
