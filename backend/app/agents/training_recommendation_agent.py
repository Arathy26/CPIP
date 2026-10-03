"""
Training Recommendation Agent
Turns the REAL gaps found by the other agents into a prioritised plan.

Pure function. Every action comes from an actual gap in the input:
  skill gap   -> missing_skills (ordered by how many recruiter postings ask for them)
  portfolio   -> evidence_missing
  interview   -> weak_dimensions / not_assessed_dimensions
  resume      -> improvement_tips
No skill names, durations or scores are invented here.

Category order (documented rule, follows the CPIP readiness lifecycle):
  1 Technical Skills -> 2 Portfolio -> 3 Interview -> 4 Resume
"""

CATEGORY_ORDER = ["Technical Skills", "Portfolio Development", "Interview Preparation", "Resume Refinement"]


def _score(section):
    value = (section or {}).get("score")
    return value if isinstance(value, (int, float)) else None


def training_recommendation_agent(all_assessments):
    """
    Args:
        all_assessments: {
            "skill_gap": {"score", "missing_skills": [str | {"skill","jobs_requiring","demand_weight"}]},
            "portfolio": {"score", "evidence_missing": [str]},
            "resume":    {"score", "improvement_tips": [str]},
            "interview": {"score", "weak_dimensions": [str], "not_assessed_dimensions": [str]},
            "target_role": str
        }
    Returns:
        Dictionary with training plan
    """
    a = all_assessments or {}
    skill_gap = a.get("skill_gap") or {}
    portfolio = a.get("portfolio") or {}
    resume = a.get("resume") or {}
    interview = a.get("interview") or {}
    target_role = a.get("target_role")

    actions = []

    # 1. Technical skills — one action per missing skill, most-demanded first
    for item in skill_gap.get("missing_skills") or []:
        if isinstance(item, str):
            item = {"skill": item}
        skill = (item.get("skill") or "").strip()
        if not skill:
            continue
        jobs = item.get("jobs_requiring")
        reason = (f"Required in {jobs} recruiter posting(s) for {target_role}"
                  if jobs else f"Required for {target_role}")
        actions.append({
            "category": "Technical Skills", "skill": skill,
            "action": f"Learn {skill}", "reason": reason,
            "demand_weight": item.get("demand_weight"), "source_agent": "skill_gap_agent",
        })

    # 2. Portfolio — one action per missing evidence item
    for evidence in portfolio.get("evidence_missing") or []:
        actions.append({
            "category": "Portfolio Development",
            "action": f"Add {evidence} to your portfolio",
            "reason": f"{evidence} is missing from your portfolio evidence",
            "source_agent": "portfolio_readiness_agent",
        })

    # 3. Interview — weak dimensions, then dimensions never assessed
    for dim in interview.get("weak_dimensions") or []:
        label = dim.replace("_", " ")
        actions.append({
            "category": "Interview Preparation",
            "action": f"Practise {label} and book a follow-up mock interview",
            "reason": f"Mentor rated {label} as Needs Work",
            "source_agent": "interview_readiness_agent",
        })
    not_assessed = interview.get("not_assessed_dimensions") or []
    if not_assessed:
        labels = ", ".join(d.replace("_", " ") for d in not_assessed)
        actions.append({
            "category": "Interview Preparation",
            "action": f"Schedule a mock interview covering: {labels}",
            "reason": "These interview dimensions have not been assessed yet",
            "source_agent": "interview_readiness_agent",
        })

    # 4. Resume — the resume agent's own specific tips
    for tip in resume.get("improvement_tips") or []:
        actions.append({
            "category": "Resume Refinement", "action": tip,
            "reason": "Found by resume readiness check",
            "source_agent": "resume_readiness_agent",
        })

    # Deterministic order: category order, then skill demand (high first)
    actions.sort(key=lambda x: (CATEGORY_ORDER.index(x["category"]), -(x.get("demand_weight") or 0)))
    for rank, action in enumerate(actions, 1):
        action["rank"] = rank
        action["priority"] = CATEGORY_ORDER.index(action["category"]) + 1

    scores = {
        "skill_gap": _score(skill_gap), "portfolio": _score(portfolio),
        "resume": _score(resume), "interview": _score(interview),
    }
    available = {k: v for k, v in scores.items() if v is not None}
    overall = int(round(sum(available.values()) / len(available))) if available else None

    if not actions:
        recommendation = "No gaps found in the assessed areas."
    else:
        first_category = actions[0]["category"]
        recommendation = f"{len(actions)} action(s) found. Start with {first_category}."

    return {
        "target_role": target_role or "Not specified",
        "current_overall_readiness": overall,
        "readiness_scores_used": available,
        "readiness_scores_missing": [k for k, v in scores.items() if v is None],
        "training_actions": actions,
        "total_actions": len(actions),
        "recommendation": recommendation,
    }


def validate_training_result(result):
    """Validates training plan completeness."""
    required_fields = ["target_role", "training_actions", "recommendation"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Training recommendation plan is valid and complete"}
