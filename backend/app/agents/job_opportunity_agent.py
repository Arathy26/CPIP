"""
Job Opportunity Agent
Matches ONE student against recruiter-posted job openings.

There is ONE source of matching logic in CPIP:
app/services/recruiter_matching_agent.py (versioned MATCHING_RULES,
skills-only, CGPA intentionally NOT checked). The API route
/api/job-match/{student_id} already uses it.

This agent is the catalog-named entry point for workflow callers
(orchestrator / LangGraph) that work with plain dicts. It delegates to the
same rules, so a student sees the same result everywhere.

Pure function: jobs are passed in by the caller; no database access here.
"""

from types import SimpleNamespace
from app.services.recruiter_matching_agent import (
    MATCHING_RULES,
    evaluate_match,
    parse_skills,
)


def _as_student(candidate_profile):
    return SimpleNamespace(
        id=candidate_profile.get("candidate_id"),
        skills=candidate_profile.get("skills", []),
    )


def _as_job(job):
    return SimpleNamespace(
        id=job.get("id") or job.get("job_id"),
        title=job.get("job_title") or job.get("title"),
        required_skills=job.get("required_skills", []),
        preferred_skills=job.get("preferred_skills", []),
        is_active=job.get("is_active", True),
    )


def job_opportunity_agent(candidate_profile, job_opportunities=None, readiness_scores=None):
    """
    Args:
        candidate_profile: {"candidate_id", "skills", ...}
        job_opportunities: list of job dicts (seed_data.get_all_jobs() shape)
        readiness_scores: accepted for workflow compatibility; NOT used —
                          matching is skills-only by CPIP rule
    Returns:
        Dictionary with job matches
    """
    candidate_id = candidate_profile.get("candidate_id")

    if not job_opportunities:
        return {
            "candidate_id": candidate_id,
            "all_matches": [],
            "suitable_jobs": [],
            "recommendation_count": 0,
            "open_jobs_evaluated": 0,
            "recommendation_summary": "No open job postings yet. Recruiters have not posted any jobs.",
            "rules_version": MATCHING_RULES["version"],
        }

    student = _as_student(candidate_profile)
    matches = []
    evaluated = 0
    for job in job_opportunities:
        j = _as_job(job)
        if not j.is_active:
            continue
        evaluated += 1
        result = evaluate_match(student, j)
        if result["is_match"]:
            result.update({
                "job_title": j.title,
                "company_name": job.get("company_name"),
                "location": job.get("location"),
                "experience_level": job.get("experience_level"),
                "required_skills": parse_skills(j.required_skills),
                "preferred_skills": parse_skills(j.preferred_skills),
            })
            matches.append(result)

    matches.sort(key=lambda r: (-r["fit_score"], r["job_id"] or 0))

    return {
        "candidate_id": candidate_id,
        "all_matches": matches,
        "suitable_jobs": matches,
        "recommendation_count": len(matches),
        "open_jobs_evaluated": evaluated,
        "recommendation_summary": (
            f"{len(matches)} posted role(s) match this profile" if matches
            else "No open posting matches this profile's skills yet."
        ),
        "rules_version": MATCHING_RULES["version"],
    }


def validate_job_match_result(result):
    """Validates job matching result."""
    required_fields = ["candidate_id", "all_matches", "suitable_jobs"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Job matching analysis is valid and complete"}
