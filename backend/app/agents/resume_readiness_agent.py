"""
Resume Readiness Agent
Evaluates whether a student's resume is complete and interview-ready

CHANGED (3 real fixes):
1. Added ACTUAL metrics detection (looks for percentages/numbers in the
   resume text) and keyword matching against the target role's required
   skills — before, the UI promised "ATS-friendly, metrics, keywords"
   but the agent never checked any of that, only 5 yes/no section
   checkboxes.
2. role_alignment is now based on real skill overlap with the target
   role's required_skills, not a fragile exact-text match on the role
   name (a great resume for "Backend Developer" shouldn't need to
   literally contain those exact words to count as aligned).
3. Every missing section now comes with a SPECIFIC, actionable tip
   instead of just a vague category name.
"""

import re

_METRIC_PATTERN = re.compile(r"\d+\s*%")  # e.g. "30%", "reduced by 15 %"


def resume_readiness_agent(resume_data, required_skills=None):
    """
    Evaluates student resume completeness and quality.

    Args:
        resume_data: dict with education, skills, projects, contact,
            role_alignment, and now raw_text (from resume_parser.py)
        required_skills: list of skills required for the student's target
            role (pass in seed_data.get_role_requirements(role)["required_skills"]).
            If None, role alignment falls back to the older text-match
            signal instead of skill overlap.

    Returns:
        Dictionary with resume readiness score, gaps, and specific tips.
    """

    sections_present = []
    sections_missing = []
    tips = []
    raw_text = resume_data.get("raw_text", "") or ""

    # ---- Education ------------------------------------------------------
    if resume_data.get("education"):
        sections_present.append("Education")
    else:
        sections_missing.append("Education")
        tips.append("Add your degree/qualification (e.g., B.Tech Computer Science).")

    # ---- Skills -----------------------------------------------------------
    if resume_data.get("skills") and len(resume_data.get("skills", [])) > 0:
        sections_present.append("Skills")
    else:
        sections_missing.append("Skills")
        tips.append("List your technical skills clearly (e.g., Python, SQL, React).")

    # ---- Projects ----------------------------------------------------------
    if resume_data.get("projects") and len(resume_data.get("projects", [])) > 0:
        sections_present.append("Projects/Experience")
    else:
        sections_missing.append("Projects/Experience")
        tips.append("Add at least one project with a short description of what you built.")

    # ---- Contact Details — now differentiates email vs phone --------------
    contact_info = resume_data.get("contact") or {}
    has_email = bool(contact_info.get("email"))
    has_phone = bool(contact_info.get("phone"))
    if has_email or has_phone:
        sections_present.append("Contact Details")
        if not has_email:
            tips.append("Add an email address so recruiters can reach you.")
        if not has_phone:
            tips.append("Add a phone number so recruiters can reach you.")
    else:
        sections_missing.append("Contact Details")
        tips.append("Add your email and phone number so recruiters can reach you.")

    # ---- Role Alignment — FIXED: skill overlap, not exact text match -------
    role_alignment_score = None
    if required_skills:
        candidate_skills_lower = set(s.lower() for s in resume_data.get("skills", []))
        required_lower = set(s.lower() for s in required_skills)
        matched = candidate_skills_lower & required_lower
        role_alignment_score = (
            int((len(matched) / len(required_lower)) * 100) if required_lower else 0
        )
        if role_alignment_score > 0:
            sections_present.append("Role Alignment")
        else:
            sections_missing.append("Role Alignment")
            missing_for_role = sorted(required_lower - candidate_skills_lower)
            if missing_for_role:
                tips.append(
                    f"Your resume doesn't show skills required for this role: "
                    f"{', '.join(missing_for_role)}."
                )
    else:
        # No configured requirements for this role — fall back to the
        # older, weaker text-match signal rather than skipping the check.
        if resume_data.get("role_alignment"):
            sections_present.append("Role Alignment")
        else:
            sections_missing.append("Role Alignment")
            tips.append("Mention your target role or relevant skills clearly in your resume.")

    # ---- Quantified Impact (NEW) — real metrics detection ------------------
    has_metrics = bool(_METRIC_PATTERN.search(raw_text))
    if has_metrics:
        sections_present.append("Quantified Impact")
    else:
        sections_missing.append("Quantified Impact")
        tips.append(
            "Add measurable outcomes to your projects "
            "(e.g., 'reduced load time by 30%', 'served 500+ users')."
        )

    # ---- Keyword match (NEW) — how well the text matches the role's language
    keyword_match_percent = None
    if required_skills and raw_text:
        required_lower = set(s.lower() for s in required_skills)
        text_lower = raw_text.lower()
        present_keywords = [s for s in required_lower if s in text_lower]
        keyword_match_percent = (
            int((len(present_keywords) / len(required_lower)) * 100) if required_lower else None
        )

    # ---- Score: 6 sections now (added Quantified Impact) -------------------
    total_possible = 6
    present_count = len(sections_present)
    resume_score = int((present_count / total_possible) * 100)

    if resume_score >= 80:
        readiness = "High - Interview ready"
    elif resume_score >= 60:
        readiness = "Medium - Some sections weak"
    elif resume_score >= 40:
        readiness = "Low - Major sections missing"
    else:
        readiness = "Very Low - Incomplete resume"

    return {
        "resume_score": resume_score,
        "sections_present": sections_present,
        "sections_missing": sections_missing,
        "improvement_tips": tips,
        "role_alignment_score": role_alignment_score,
        "keyword_match_percent": keyword_match_percent,
        "total_sections": len(sections_present),
        "sections_needed": len(sections_missing),
        "readiness_level": readiness,
        "resume_analysis": f"{present_count} of {total_possible} resume sections complete",
    }


def validate_resume_result(result):
    """Validates that gap analysis result is complete."""
    required_fields = [
        "resume_score", "sections_present", "sections_missing",
        "readiness_level", "resume_analysis", "improvement_tips",
    ]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Resume readiness analysis is valid and complete"}