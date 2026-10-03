"""
Interview Readiness Agent
Evaluates interview preparedness across four dimensions.

Pure function. Scores come ONLY from human mock-interview assessments
(seed_data.get_latest_interview_scores). A dimension that was never
assessed is None and is reported as "Not assessed" — it is NOT treated
as 0 and does NOT count in the composite score.

Rule bands (single definition, used everywhere in this agent):
  Dimension status : >= 75 Strong | >= 60 Moderate | < 60 Needs Work
  Readiness level  : >= 80 High   | >= 70 Good     | >= 60 Fair | < 60 Low
"""

DIMENSIONS = {
    "aptitude": "Logical reasoning and quantitative skills",
    "technical": "Coding ability and concept knowledge",
    "communication": "Clarity and professionalism in speaking",
    "project_explanation": "Ability to discuss and explain projects",
}


def _dimension_status(score):
    if score is None:
        return "Not assessed"
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Moderate"
    return "Needs Work"


def _readiness_level(score):
    if score is None:
        return "Not assessed - Schedule a mock interview"
    if score >= 80:
        return "High - Interview Ready"
    if score >= 70:
        return "Good - Minor Preparation Needed"
    if score >= 60:
        return "Fair - Moderate Preparation Needed"
    return "Low - Significant Preparation Required"


def interview_readiness_agent(interview_scores):
    """
    Args:
        interview_scores: {"aptitude_score", "technical_score",
                           "communication_score", "project_explanation_score"}
                          each a number 0-100 or None (not assessed)
    Returns:
        Dictionary with interview readiness assessment
    """
    dimension_analysis = {}
    assessed = {}
    for dim, focus in DIMENSIONS.items():
        raw = (interview_scores or {}).get(f"{dim}_score")
        score = float(raw) if raw is not None else None
        if score is not None:
            assessed[dim] = score
        dimension_analysis[dim] = {
            "score": score,
            "status": _dimension_status(score),
            "focus": focus,
        }

    composite = int(round(sum(assessed.values()) / len(assessed))) if assessed else None

    weak_dimensions = [d for d, a in dimension_analysis.items() if a["status"] == "Needs Work"]
    not_assessed = [d for d, a in dimension_analysis.items() if a["status"] == "Not assessed"]

    if not assessed:
        focus_text = "No mock interview recorded yet. Schedule one with a mentor."
    elif weak_dimensions:
        focus_text = f"Focus on: {', '.join(weak_dimensions)}"
    else:
        focus_text = "No weak dimensions among those assessed"
    if assessed and not_assessed:
        focus_text += f". Not yet assessed: {', '.join(not_assessed)}"

    return {
        "interview_readiness_score": composite,
        "readiness_level": _readiness_level(composite),
        "dimension_analysis": dimension_analysis,
        "weak_dimensions": weak_dimensions,
        "not_assessed_dimensions": not_assessed,
        "dimensions_assessed": f"{len(assessed)} of {len(DIMENSIONS)}",
        "preparation_focus": focus_text,
    }


def validate_interview_result(result):
    """Validates that interview readiness result is complete."""
    required_fields = ["interview_readiness_score", "readiness_level", "dimension_analysis"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Interview readiness analysis is valid and complete"}
