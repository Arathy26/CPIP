"""
Role Matching Agent
Recommends suitable job roles by comparing the student's skills with the
roles recruiters have actually posted in CPIP.

Pure function: no database access. The caller passes in role_requirements
(from seed_data.get_all_target_roles()). No role list is hardcoded here.

Fit score = matched required skills / required skills x 100
Readiness scores are NOT mixed into the fit score: role fit answers
"do your skills match this role?", readiness is reported by its own agents.
"""


def _clean(skills):
    """Map lowercase -> original text, trimmed, empties removed."""
    out = {}
    for s in skills or []:
        if s and str(s).strip():
            out.setdefault(str(s).strip().lower(), str(s).strip())
    return out


def _suitability(fit_score):
    # Fit categories from the CPIP Employer & Job Demand Guide
    if fit_score >= 80:
        return "Strong Fit"
    if fit_score >= 60:
        return "Good Fit"
    if fit_score >= 40:
        return "Stretch Fit"
    return "Not Suitable Yet"


def role_matching_agent(candidate_profile, readiness_scores=None, role_requirements=None, top_n=5):
    """
    Args:
        candidate_profile: {"candidate_id", "skills", "target_role"}
        readiness_scores: accepted for workflow compatibility; not used in fit
        role_requirements: {role_title: {"required_skills": [...],
                                         "skill_demand": {skill: count},
                                         "job_postings": n}}
        top_n: how many roles to recommend

    Returns:
        Dictionary with role recommendations
    """
    candidate_id = candidate_profile.get("candidate_id")
    target_role = candidate_profile.get("target_role")
    candidate = _clean(candidate_profile.get("skills", []))

    if not role_requirements:
        return {
            "candidate_id": candidate_id,
            "target_career_goal": target_role,
            "recommended_roles": [],
            "all_matches": [],
            "total_roles_analyzed": 0,
            "recommendation_summary": "No roles available yet. Recruiters have not posted any jobs.",
        }

    role_matches = []
    for role, data in role_requirements.items():
        required = _clean(data.get("required_skills", []))
        if not required:
            continue

        demand = {k.strip().lower(): v for k, v in (data.get("skill_demand") or {}).items()}
        postings = data.get("job_postings") or 0

        matched_keys = sorted(set(required) & set(candidate))
        missing_keys = sorted(set(required) - set(candidate))
        fit_score = int(len(matched_keys) / len(required) * 100)

        missing = [
            {
                "skill": required[k],
                "jobs_requiring": demand.get(k),
                "demand_weight": round(demand[k] / postings * 100) if postings and k in demand else None,
            }
            for k in missing_keys
        ]
        missing.sort(key=lambda m: (-(m["demand_weight"] or 0), m["skill"].lower()))

        role_matches.append({
            "role": role,
            "fit_score": fit_score,
            "suitability": _suitability(fit_score),
            "is_target_role": bool(target_role) and target_role.strip().lower() in role.lower(),
            "required_skills": list(required.values()),
            "matched_skills": [required[k] for k in matched_keys],
            "missing_skills": missing,
            "total_skills_required": len(required),
            "job_postings_for_role": postings,
        })

    # Highest fit first; ties broken by more postings, then name (deterministic)
    role_matches.sort(key=lambda r: (-r["fit_score"], -r["job_postings_for_role"], r["role"].lower()))
    top = role_matches[:top_n]

    summary = (
        f"Top recommendation: {top[0]['role']} (Fit Score: {top[0]['fit_score']})"
        if top else "No posted role has required skills defined yet."
    )

    return {
        "candidate_id": candidate_id,
        "target_career_goal": target_role,
        "recommended_roles": top,
        "all_matches": role_matches,
        "total_roles_analyzed": len(role_matches),
        "recommendation_summary": summary,
    }


def validate_role_match_result(result):
    """Validates that role matching result is complete."""
    required_fields = ["candidate_id", "recommended_roles", "recommendation_summary"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Role matching analysis is valid and complete"}
