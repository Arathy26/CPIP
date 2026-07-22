"""
Job Opportunity Routes
API endpoints for job opportunity matching
"""

from fastapi import APIRouter, HTTPException
from app.agents.job_opportunity_agent import job_opportunity_agent, validate_job_match_result

router = APIRouter()

# Candidate profiles with readiness scores
CANDIDATE_JOB_DATA = {
    1: {
        "profile": {
            "candidate_id": 1,
            "skills": ["Python", "React", "SQL"],
            "cgpa": 7.5,
            "degree": "B.Tech",
            "current_readiness_score": 71
        },
        "readiness_scores": {
            "skill_gap_score": 65,
            "portfolio_score": 50,
            "resume_score": 100,
            "interview_readiness_score": 70
        }
    },
    2: {
        "profile": {
            "candidate_id": 2,
            "skills": ["Python", "FastAPI", "SQL", "Docker"],
            "cgpa": 8.2,
            "degree": "B.Tech",
            "current_readiness_score": 85
        },
        "readiness_scores": {
            "skill_gap_score": 85,
            "portfolio_score": 100,
            "resume_score": 100,
            "interview_readiness_score": 80
        }
    },
    3: {
        "profile": {
            "candidate_id": 3,
            "skills": ["Python", "React", "SQL"],
            "cgpa": 7.2,
            "degree": "B.Tech",
            "current_readiness_score": 75
        },
        "readiness_scores": {
            "skill_gap_score": 75,
            "portfolio_score": 75,
            "resume_score": 80,
            "interview_readiness_score": 70
        }
    }
}


@router.get("/job-match/{student_id}")
def get_job_match(student_id: int):
    """
    Get job opportunities matching for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Job matches with fit scores and eligibility
    """
    
    if student_id not in CANDIDATE_JOB_DATA:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    candidate_data = CANDIDATE_JOB_DATA[student_id]
    
    # Run Job Opportunity Agent
    job_result = job_opportunity_agent(
        candidate_data["profile"],
        candidate_data["readiness_scores"]
    )
    
    # Validate result
    validation = validate_job_match_result(job_result)
    
    return {
        "student_id": student_id,
        "job_match_analysis": job_result,
        "validation": validation,
        "message": "Job matching completed successfully"
    }


@router.get("/job-match")
def list_all_job_matches():
    """
    Get job matches for all students.
    
    Returns:
        Job match summary for all students
    """
    
    results = []
    
    for student_id in CANDIDATE_JOB_DATA:
        candidate_data = CANDIDATE_JOB_DATA[student_id]
        job_result = job_opportunity_agent(
            candidate_data["profile"],
            candidate_data["readiness_scores"]
        )
        
        results.append({
            "student_id": student_id,
            "suitable_jobs_count": job_result["recommendation_count"],
            "top_match": job_result["suitable_jobs"][0]["job_title"] if job_result["suitable_jobs"] else "No suitable matches",
            "total_matches": len(job_result["all_matches"])
        })
    
    return {
        "total_students": len(results),
        "job_matches": results,
        "message": "All job matches retrieved"
    }

