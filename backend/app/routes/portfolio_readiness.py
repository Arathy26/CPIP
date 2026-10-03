"""
Portfolio Readiness Routes
API endpoints for portfolio readiness evaluation

Evidence source rule (Option C):
  1. Link the student entered on their profile  -> source "student"
  2. Otherwise, evidence found in their selected resume -> source "resume"
  3. Otherwise, the evidence is missing           -> source None
The route only gathers evidence. portfolio_readiness_agent does the scoring.
"""

import re
from fastapi import APIRouter, HTTPException
from app.agents.portfolio_readiness_agent import portfolio_readiness_agent, validate_portfolio_result
from app.data import seed_data

router = APIRouter()

_URL_PATTERN = re.compile(r"(https?://[^\s<>()\[\]\"',]+|www\.[^\s<>()\[\]\"',]+)", re.IGNORECASE)


def _urls_in_resume(resume):
    """All URLs written in the resume text, in the order they appear."""
    if not resume:
        return []
    text = resume.get("raw_text") or ""
    return [u.rstrip(".;:") for u in _URL_PATTERN.findall(text)]


def _resolve_portfolio_evidence(student, resume):
    """Returns (portfolio_data for the agent, evidence_sources for transparency)."""
    urls = _urls_in_resume(resume)
    github_urls = [u for u in urls if "github.com" in u.lower()]
    linkedin_urls = [u for u in urls if "linkedin.com" in u.lower()]
    other_urls = [u for u in urls if u not in github_urls and u not in linkedin_urls]

    def pick(student_value, resume_value):
        if student_value:
            return student_value, "student"
        if resume_value:
            return resume_value, "resume"
        return None, None

    github, github_src = pick(student.get("github_link"), github_urls[0] if github_urls else None)
    linkedin, linkedin_src = pick(student.get("linkedin_id"), linkedin_urls[0] if linkedin_urls else None)
    demo, demo_src = pick(student.get("deployed_demo_link"), other_urls[0] if other_urls else None)

    resume_projects = (resume or {}).get("projects") or []
    explanation, explanation_src = pick(
        student.get("project_readme_link"),
        f"{len(resume_projects)} project(s) described in resume" if resume_projects else None
    )

    portfolio_data = {
        "github_link": github,
        "deployed_demo": demo,
        "project_explanation": bool(explanation),
        "linkedin_profile": linkedin,
    }
    evidence_sources = {
        "github": {"value": github, "source": github_src},
        "deployed_demo": {"value": demo, "source": demo_src},
        "project_explanation": {"value": explanation, "source": explanation_src},
        "linkedin": {"value": linkedin, "source": linkedin_src},
    }
    return portfolio_data, evidence_sources


@router.get("/portfolio-readiness/{student_id}")
def get_portfolio_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    resume = seed_data.get_resume(student_id)
    portfolio_data, evidence_sources = _resolve_portfolio_evidence(student, resume)

    portfolio_result = portfolio_readiness_agent(portfolio_data)
    validation = validate_portfolio_result(portfolio_result)

    return {
        "student_id": student_id,
        "portfolio_analysis": portfolio_result,
        "evidence_sources": evidence_sources,
        "validation": validation,
        "message": "Portfolio readiness analysis completed successfully"
    }


@router.get("/portfolio-readiness")
def list_all_portfolio_readiness():
    results = []

    for student in seed_data.get_all_students():
        student_id = student["id"]
        resume = seed_data.get_resume(student_id)
        portfolio_data, _ = _resolve_portfolio_evidence(student, resume)

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
