"""
Job Opportunity Agent
Matches students to job openings based on skills and readiness
"""

import re


def _tier_from_score(fit_score):
    """
    4-tier match labels, agreed thresholds:
    Perfect Match >=95, High Match >=80, Medium Match >=50, Low Match <50.
    """
    if fit_score >= 95:
        return "Perfect Match"
    elif fit_score >= 80:
        return "High Match"
    elif fit_score >= 50:
        return "Medium Match"
    else:
        return "Low Match"


def _text_contains_skill_as_word(text_lower, skill):
    """
    Whole-word match only — NOT plain substring matching. FIXES A REAL
    BUG: checking "react" as a substring would also match inside
    "reactive", "reacted", "reaction" — words that don't actually mean
    the candidate knows React. \\b word boundaries make sure "react" only
    matches the standalone word, not a fragment of a longer word.
    """
    if not text_lower or not skill:
        return False
    pattern = r"\b" + re.escape(skill) + r"\b"
    return bool(re.search(pattern, text_lower))


def _score_fit(candidate_skills_lower, candidate_cgpa, candidate_readiness, job, raw_resume_text=""):
    """
    Re-scans the candidate's actual resume text against THIS job's
    specific required/preferred skills, not just the frozen
    candidate.skills snapshot from upload time. Uses whole-word matching
    to avoid false positives.
    """
    required_set = set([s.lower() for s in job.get("required_skills", [])])
    preferred_set = set([s.lower() for s in job.get("preferred_skills", [])])
    text_lower = (raw_resume_text or "").lower()

    def _is_matched(skill):
        return skill in candidate_skills_lower or _text_contains_skill_as_word(text_lower, skill)

    required_matched = set(s for s in required_set if _is_matched(s))
    preferred_matched = set(s for s in preferred_set if _is_matched(s))

    required_percentage = (len(required_matched) / len(required_set)) * 100 if required_set else 100
    preferred_percentage = (len(preferred_matched) / len(preferred_set)) * 100 if preferred_set else 100

    fit_score = int((required_percentage * 0.7) + (preferred_percentage * 0.3))

    min_cgpa = job.get("min_cgpa", 0)
    min_readiness = job.get("min_readiness", 0)
    cgpa_eligible = candidate_cgpa >= min_cgpa
    readiness_eligible = candidate_readiness >= min_readiness

    if cgpa_eligible and readiness_eligible:
        eligibility = "Eligible"
    elif cgpa_eligible or readiness_eligible:
        eligibility = "Conditionally Eligible"
    else:
        eligibility = "Not Eligible"

    suitability = _tier_from_score(fit_score)

    return {
        "fit_score": fit_score,
        "suitability": suitability,
        "eligibility": eligibility,
        "required_skills_matched": list(required_matched),
        "required_skills_missing": list(required_set - required_matched),
        "preferred_skills_missing": list(preferred_set - preferred_matched),
        "min_cgpa_required": min_cgpa,
        "candidate_cgpa": candidate_cgpa,
        "min_readiness_required": min_readiness,
        "candidate_readiness": candidate_readiness,
    }


def job_opportunity_agent(candidate_profile, readiness_scores, job_opportunities, raw_resume_text=""):
    """Matches ONE candidate against ALL real job postings."""
    candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
    candidate_cgpa = candidate_profile.get("cgpa", 0)
    candidate_readiness = readiness_scores.get("skill_gap_score", 0)

    matched_jobs = []
    for job in job_opportunities:
        scored = _score_fit(candidate_skills, candidate_cgpa, candidate_readiness, job, raw_resume_text)
        matched_jobs.append({
            "job_id": job.get("id"),
            "job_title": job["job_title"],
            "company_name": job.get("company_name", "Unknown"),
            "location": job.get("location", "Not specified"),
            "experience_level": job.get("experience_level", "Not specified"),
            **scored,
        })

    matched_jobs.sort(key=lambda x: x["fit_score"], reverse=True)

    suitable_jobs = [
        j for j in matched_jobs
        if j["suitability"] in ["Perfect Match", "High Match"] and j["eligibility"] == "Eligible"
    ]

    return {
        "candidate_id": candidate_profile.get("candidate_id"),
        "all_matches": matched_jobs,
        "suitable_jobs": suitable_jobs[:3],
        "recommendation_count": len(suitable_jobs),
        "recommendation_summary": f"Found {len(suitable_jobs)} suitable job(s) for this candidate",
    }


def match_candidates_to_job(job, candidates_with_scores):
    """Matches ONE job against ALL candidates — the recruiter's view."""
    results = []
    for candidate_profile, readiness_scores, raw_resume_text in candidates_with_scores:
        candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
        candidate_cgpa = candidate_profile.get("cgpa", 0)
        candidate_readiness = readiness_scores.get("skill_gap_score", 0)

        scored = _score_fit(candidate_skills, candidate_cgpa, candidate_readiness, job, raw_resume_text)
        results.append({
            "candidate_id": candidate_profile.get("candidate_id"),
            "candidate_name": candidate_profile.get("name"),
            "cgpa": candidate_profile.get("cgpa"),
            "degree": candidate_profile.get("degree"),
            **scored,
        })

    results.sort(key=lambda x: x["fit_score"], reverse=True)
    return results


def validate_job_match_result(result):
    """Validates job matching result."""
    required_fields = ["candidate_id", "all_matches", "suitable_jobs"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Job matching analysis is valid and complete"}