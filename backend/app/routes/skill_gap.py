"""
Skill Gap Agent - Compares student skills against recruiter-posted job requirements
No external APIs — all data comes from recruiter job postings in CPIP
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, JobPostingModel
import json
from app.agents.skill_gap_agent import skill_gap_agent

router = APIRouter()


# ---------------------------------------------------------------------------
# Skill gap vs the student's TARGET ROLE (dashboard). Role requirements come
# from all active recruiter postings for that role; comparison is done by
# skill_gap_agent through the orchestrator step (same logic everywhere).
# No postings for the role -> gap_score None ("not assessed"), never 0.
# ---------------------------------------------------------------------------
@router.get("/skill-gap/{student_id}")
def get_skill_gap(student_id: int, role: str = None):
    from app.data import seed_data
    from app.services.orchestrator import step_skill_gap

    student = seed_data.get_student(student_id)
    if not student:
        return JSONResponse(status_code=404, content={"detail": "Student not found"})

    target_role = role or student.get("target_role")
    role_data = seed_data.get_role_requirements(target_role) if target_role else None
    gap = step_skill_gap({"student": student, "role_requirements": role_data})["skill_gap"]

    message = None
    if not target_role:
        message = "No target role set yet."
    elif not role_data:
        message = f"No recruiter has posted a job for '{target_role}' yet."

    return {
        "student_id": student_id,
        "gap_analysis": {
            "gap_score": gap["score"],
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "target_role": target_role,
            "total_market_skills": len(role_data["required_skills"]) if role_data else 0,
            "job_postings_analyzed": gap["postings_analyzed"],
            "message": message,
        },
    }


# ---------------------------------------------------------------------------
# NEW endpoint — skill gap for ONE selected job vs ONE student.
# Route fetches data; skill_gap_agent (pure function) does the comparison.
# ---------------------------------------------------------------------------
def _parse_skills(raw):
    """Skills may be stored as a JSON list, a Python list, or comma text."""
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (ValueError, TypeError):
        return [s.strip() for s in str(raw).split(",")]


@router.get("/skill-gap/{student_id}/job/{job_id}")
def get_skill_gap_for_job(student_id: int, job_id: int):
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})

        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            return JSONResponse(status_code=404, content={"detail": "Job posting not found"})
        if not job.is_active:
            return JSONResponse(status_code=400, content={"detail": "Job posting is no longer active"})

        result = skill_gap_agent(
            candidate_skills=_parse_skills(student.skills),
            required_skills=_parse_skills(job.required_skills)
        )

        return {
            "student_id": student_id,
            "job_id": job_id,
            "job_title": job.title,
            "gap_analysis": result
        }
    finally:
        db.close()