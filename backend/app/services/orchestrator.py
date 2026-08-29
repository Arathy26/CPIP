"""
CPIP Orchestrator
Connects all agents in correct order after resume upload
"""

from app.agents.portfolio_readiness_agent import portfolio_readiness_agent
from app.agents.interview_readiness_agent import interview_readiness_agent
from app.agents.role_matching_agent import role_matching_agent
from app.agents.training_recommendation_agent import training_recommendation_agent
from app.agents.explanation_agent import explanation_agent
from app.agents.audit_agent import audit_agent
from app.data import seed_data
from datetime import datetime


def run_full_pipeline(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        return {"error": "Student not found"}

    resume = seed_data.get_resume(student_id)
    target_role = student.get("target_role", "")

    # ── FETCH REAL JOBS FROM JSEARCH ──
    try:
        from app.services.external_jobs_service import search_external_jobs, get_job_details, extract_skills_from_text
        listings = search_external_jobs(f"{target_role} jobs")
        for listing in listings:
            try:
                details = get_job_details(listing.get("job_id", ""))
                description = details.get("job_description", "") if details else ""
            except Exception:
                description = ""

            skills = extract_skills_from_text(description)
            job_title = listing.get("title", target_role)
            company_name = listing.get("company", "Unknown")

            # Skip if already exists
            if not seed_data.job_exists(job_title, company_name):
                seed_data.add_job({
                    "job_title": job_title,
                    "company_name": company_name,
                    "location": listing.get("location", "Remote"),
                    "required_skills": skills,
                    "preferred_skills": [],
                    "experience_level": listing.get("employment_type", "Not specified"),
                })
    except Exception as e:
        print(f"Job fetch error: {e}")

    # ── AGENT 1: Portfolio Readiness ──
    portfolio_data = {
        "github_link": student.get("github_link", None),
        "deployed_demo": resume.get("deployed_demo", None) if resume else None,
        "readme_quality": resume.get("readme_quality", None) if resume else None,
        "project_explanation": resume.get("project_explanation", False) if resume else False,
        "linkedin_profile": student.get("linkedin_id", None),
    }
    portfolio_result = portfolio_readiness_agent(portfolio_data)
    seed_data.update_readiness_scores(student_id, {
        "portfolio_score": portfolio_result["portfolio_score"]
    })

    # ── AGENT 2: Interview Readiness ──
    skills = student.get("skills", [])
    projects = resume.get("projects", []) if resume else []
    github = student.get("github_link", None)
    linkedin = student.get("linkedin_id", None)
    technical_score = min(50 + len(skills) * 5, 100)
    project_score = min(50 + len(projects) * 10, 100)
    communication_score = min(60 + (15 if github else 0) + (15 if linkedin else 0), 100)

    interview_scores = {
        "aptitude_score": 65,
        "technical_score": technical_score,
        "communication_score": communication_score,
        "project_explanation_score": project_score,
    }
    interview_result = interview_readiness_agent(interview_scores)
    seed_data.update_readiness_scores(student_id, {
        "interview_readiness_score": interview_result["interview_readiness_score"]
    })

    # ── AGENT 3: Role Matching ──
    profile = {
        "candidate_id": student_id,
        "skills": skills,
        "target_role": target_role,
    }
    scores = seed_data.get_readiness_scores(student_id)
    role_result = role_matching_agent(profile, scores)

    # ── AGENT 4: Training Recommendation ──
    assessments = {
        "skill_gap": {"score": scores.get("skill_gap_score", 0), "missing_skills": []},
        "portfolio": {"score": scores.get("portfolio_score", 0), "evidence_missing": []},
        "resume": {"score": scores.get("resume_score", 0), "sections_missing": []},
        "interview": {"score": scores.get("interview_readiness_score", 0), "weak_dimensions": []},
        "target_role": target_role,
    }
    training_result = training_recommendation_agent(assessments)

    # ── AGENT 5: Explanation ──
    agent_outputs = {
        "candidate_id": student_id,
        "skill_gap_score": scores.get("skill_gap_score", 0),
        "portfolio_score": scores.get("portfolio_score", 0),
        "resume_score": scores.get("resume_score", 0),
        "interview_score": scores.get("interview_readiness_score", 0),
        "role_recommendation": target_role,
        "job_matches": len(seed_data.get_all_jobs()),
        "training_actions": len(training_result.get("training_actions", [])),
        "workflow_stage": "not_applied",
    }
    explanation_result = explanation_agent(agent_outputs)

    # ── AGENT 6: Audit ──
    audit_input = {
        "candidate_id": student_id,
        "event_type": "full_pipeline_evaluation",
        "scores": scores,
        "recommendation": target_role,
        "decision_reason": explanation_result["full_explanation"],
        "timestamp": datetime.now().isoformat(),
    }
    audit_result = audit_agent(audit_input)

    return {
        "student_id": student_id,
        "portfolio_result": portfolio_result,
        "interview_result": interview_result,
        "role_result": role_result,
        "training_result": training_result,
        "explanation_result": explanation_result,
        "audit_result": audit_result,
        "scores": seed_data.get_readiness_scores(student_id),
    }