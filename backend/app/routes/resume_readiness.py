"""
Resume Readiness Routes
API endpoints for resume readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.resume_readiness_agent import resume_readiness_agent, validate_resume_result
from app.data import seed_data

router = APIRouter()


@router.get("/resume-readiness/{student_id}")
def get_resume_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    resume_data = seed_data.get_resume(student_id)
    if resume_data is None:
        return {
            "student_id": student_id,
            "supported": False,
            "resume_analysis": None,
            "message": "No resume on file. Upload via POST /resume/upload.",
        }

    role_data = seed_data.get_role_requirements(student["target_role"])
    required_skills = role_data["required_skills"] if role_data else None
    resume_result = resume_readiness_agent(resume_data, required_skills=required_skills)
    validation = validate_resume_result(resume_result)

    return {
        "student_id": student_id,
        "supported": True,
        "resume_analysis": resume_result,
        "role_requirements": role_data or {
            "role": student.get("target_role"),
            "required_skills": [],
            "message": "No recruiter has posted a job for this role yet",
        },
        "validation": validation,
        "message": "Resume readiness analysis completed successfully",
    }


@router.get("/resume-readiness/{student_id}/job/{job_id}")
def get_resume_readiness_for_job(student_id: int, job_id: int):
    """Resume readiness against ONE selected recruiter job (option C, part B)."""
    student = seed_data.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    job = seed_data.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if not job.get("is_active"):
        raise HTTPException(status_code=400, detail="Job posting is no longer active")

    resume_data = seed_data.get_resume(student_id)
    if resume_data is None:
        return {
            "student_id": student_id,
            "job_id": job_id,
            "supported": False,
            "resume_analysis": None,
            "message": "No resume on file. Upload via POST /resume/upload.",
        }

    resume_result = resume_readiness_agent(resume_data, required_skills=job.get("required_skills"))
    validation = validate_resume_result(resume_result)

    return {
        "student_id": student_id,
        "job_id": job_id,
        "job_title": job.get("job_title"),
        "supported": True,
        "resume_analysis": resume_result,
        "validation": validation,
        "message": "Resume readiness for selected job completed successfully",
    }


@router.get("/resume-readiness")
def list_all_resume_readiness():
    results = []
    for student in seed_data.get_all_students():
        resume_data = seed_data.get_resume(student["id"])
        if resume_data is None:
            continue

        role_data = seed_data.get_role_requirements(student["target_role"])
        required_skills = role_data["required_skills"] if role_data else None
        resume_result = resume_readiness_agent(resume_data, required_skills=required_skills)

        results.append({
            "student_id": student["id"],
            "resume_score": resume_result["resume_score"],
            "readiness_level": resume_result["readiness_level"],
            "sections_present": len(resume_result["sections_present"]),
            "sections_missing": len(resume_result["sections_missing"]),
        })

    return {
        "total_students": len(results),
        "resume_readiness": results,
        "message": "All resume readiness scores retrieved",
    }


# Resume upload lives in routes/resume_management.py (one upload pipeline).
