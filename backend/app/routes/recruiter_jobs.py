from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.data.seed_data import (
    add_job_with_recruiter,
    get_all_students,
    get_job_by_id,
    get_all_jobs,
    update_job_by_id,
    delete_job_by_id,
)
from app.services.recruiter_matching_agent import match_candidates_for_job, parse_skills
from app.data.database import SessionLocal, StudentModel

router = APIRouter(prefix="/api/recruiter", tags=["recruiter"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RecruiterJobPostRequest(BaseModel):
    job_title: str
    company_name: str
    location: str
    required_skills: List[str]
    min_cgpa: float
    experience_level: str
    job_type: str
    employment_type: str

class RecruiterJobUpdateRequest(BaseModel):
    job_title: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[List[str]] = None
    min_cgpa: Optional[float] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    employment_type: Optional[str] = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _job_to_dict(j):
    """Convert job object to dictionary"""
    return {
        "id": j.id,
        "job_title": j.title,
        "company_name": j.company_name,
        "location": j.location,
        "required_skills": parse_skills(j.required_skills),
        "preferred_skills": parse_skills(j.preferred_skills),
        "min_cgpa": j.min_cgpa,
        "experience_level": j.experience_level,
        "employment_type": j.employment_type,
        "is_active": j.is_active,
        "posted_date": j.created_at.isoformat() if j.created_at else None,
    }

# ============================================================================
# ROUTES
# ============================================================================

@router.post("/jobs")
def post_job(req: RecruiterJobPostRequest):
    """Post a new job opportunity"""
    try:
        new_job = add_job_with_recruiter(
            job_title=req.job_title,
            company_name=req.company_name,
            location=req.location,
            required_skills=req.required_skills,
            min_cgpa=req.min_cgpa,
            experience_level=req.experience_level,
            job_type=req.job_type,
            employment_type=req.employment_type,
        )
        return {"job": _job_to_dict(new_job)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
def get_jobs():
    """Get all jobs"""
    try:
        jobs = get_all_jobs()
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    """Get a specific job by ID"""
    try:
        job = get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"job": _job_to_dict(job)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/matches")
def get_job_matches(job_id: int):
    """Get matched candidates for a job"""
    try:
        job = get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        db = SessionLocal()
        try:
            all_students = db.query(StudentModel).all()
        finally:
            db.close()

        # Same agent as /api/jobs/{job_id}/candidates — identical scores.
        matches = match_candidates_for_job(job, all_students)
        
        return {"candidate_matches": matches}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/jobs/{job_id}")
def update_job(job_id: int, req: RecruiterJobUpdateRequest):
    """Update a job"""
    try:
        update_data = {}
        
        if req.job_title is not None:
            update_data["title"] = req.job_title  # model column is "title"
        if req.location is not None:
            update_data["location"] = req.location
        if req.required_skills is not None:
            update_data["required_skills"] = req.required_skills
        if req.min_cgpa is not None:
            update_data["min_cgpa"] = req.min_cgpa
        if req.experience_level is not None:
            update_data["experience_level"] = req.experience_level
        if req.job_type is not None:
            update_data["job_type"] = req.job_type
        if req.employment_type is not None:
            update_data["employment_type"] = req.employment_type
        
        updated_job = update_job_by_id(job_id, update_data)
        if not updated_job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"job": _job_to_dict(updated_job)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    """Delete a job"""
    try:
        success = delete_job_by_id(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))