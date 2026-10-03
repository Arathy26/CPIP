
def _clean_skills(skills):
    """Turn a skill list into a clean set: trimmed, lowercase, no empty entries."""
    if not skills:
        return set()
    return {str(s).strip().lower() for s in skills if s and str(s).strip()}


def skill_gap_agent(candidate_skills, required_skills, mandatory_skills=None):
    """
    Compares candidate skills with required skills for ONE job.
    Pure function: no database, no API calls.
    """
    candidate_set = _clean_skills(candidate_skills)
    required_set = _clean_skills(required_skills)
    mandatory_set = _clean_skills(mandatory_skills) if mandatory_skills else required_set

    # No requirements = nothing to compare. Do not invent a score.
    if not required_set:
        return {
            "gap_score": None,
            "matched_skills": [],
            "missing_skills": [],
            "missing_mandatory_skills": [],
            "total_required_skills": 0,
            "skills_matched": 0,
            "readiness_level": "Not calculated",
            "gap_analysis": "This job has no required skills defined"
        }

    matched_skills = sorted(candidate_set & required_set)
    missing_skills = sorted(required_set - candidate_set)
    missing_mandatory = sorted(mandatory_set - candidate_set)

    gap_score = int((len(matched_skills) / len(required_set)) * 100)

    if gap_score >= 80:
        readiness = "High - Ready to apply"
    elif gap_score >= 60:
        readiness = "Medium - Some preparation needed"
    elif gap_score >= 40:
        readiness = "Low - Significant preparation needed"
    else:
        readiness = "Very Low - Major skill development required"

    return {
        "gap_score": gap_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "missing_mandatory_skills": missing_mandatory,
        "total_required_skills": len(required_set),
        "skills_matched": len(matched_skills),
        "readiness_level": readiness,
        "gap_analysis": f"{len(matched_skills)} of {len(required_set)} required skills present"
    }


