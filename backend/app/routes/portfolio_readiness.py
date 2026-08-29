"""
Portfolio Readiness Routes
API endpoints for portfolio readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.portfolio_readiness_agent import portfolio_readiness_agent, validate_portfolio_result
from app.data import seed_data

router = APIRouter()

@router.get("/portfolio-readiness/{student_id}")
def get_portfolio_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    resume = seed_data.get_resume(student_id)

    portfolio_data = {
        "github_link": student.get("github_link", None),
        "deployed_demo": resume.get("deployed_demo", None) if resume else None,
        "readme_quality": resume.get("readme_quality", None) if resume else None,
        "project_explanation": resume.get("project_explanation", False) if resume else False,
        "linkedin_profile": student.get("linkedin_id", None),
    }

    portfolio_result = portfolio_readiness_agent(portfolio_data)
    validation = validate_portfolio_result(portfolio_result)

    return {
        "student_id": student_id,
        "portfolio_analysis": portfolio_result,
        "validation": validation,
        "message": "Portfolio readiness analysis completed successfully"
    }


@router.get("/portfolio-readiness")
def list_all_portfolio_readiness():
    results = []

    for student in seed_data.get_all_students():
        student_id = student["id"]
        resume = seed_data.get_resume(student_id)

        portfolio_data = {
            "github_link": student.get("github_link", None),
            "deployed_demo": resume.get("deployed_demo", None) if resume else None,
            "readme_quality": resume.get("readme_quality", None) if resume else None,
            "project_explanation": resume.get("project_explanation", False) if resume else False,
            "linkedin_profile": student.get("linkedin_id", None),
        }

        portfolio_result = portfolio_readiness_agent(portfolio_data)

        results.append({
            "student_id": student_id,
            "portfolio_score": portfolio_result["portfolio_score"],
            "readiness_level": portfolio_result["readiness_level"],
            "evidence_present": len(portfolio_result["evidence_present"]),
            "evidence_missing": len(portfolio_result["evidence_missing"])
        })

    return {
        "total_students": len(results),
        "portfolio_readiness": results,
        "message": "All portfolio readiness scores retrieved"
    }