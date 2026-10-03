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

# Quantified impact: "30%", "15 %", "500+", "3x" / "3X"
_METRIC_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*%|\d+\s*\+|\b\d+(?:\.\d+)?\s*[xX]\b")


# A "Skills" heading at the start of a line, e.g. "SKILLS", "Technical Skills:",
# "Core Competencies", "Tech Stack". Detects the SECTION, independent of which
# skills recruiters have posted.
_SKILLS_HEADING = re.compile(
    r"^\s*(technical\s+skills|key\s+skills|core\s+skills|skills|"
    r"core\s+competencies|tech(?:nical)?\s+stack|technologies)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _clean(skills):
    """Trimmed, lowercase, no empty entries."""
    return {str(s).strip().lower() for s in (skills or []) if s and str(s).strip()}


def _contains_skill(text_lower, skill_lower):
    """Whole-skill match: 'c' must not match inside 'react', 'java' not inside 'javascript'."""
    pattern = r"(?<![a-z0-9+#.])" + re.escape(skill_lower) + r"(?![a-z0-9+#])"
    return re.search(pattern, text_lower) is not None


def resume_readiness_agent(resume_data, required_skills=None):
    """
    Evaluates student resume completeness and quality.

    Args:
        resume_data: dict with education, skills, projects, contact,
            role_alignment, and now raw_text (from resume_parser.py)
        required_skills: list of skills required for the student's target
            role (pass in seed_data.get_role_requirements(role)["required_skills"]).
            Comes from recruiter postings (seed_data.get_role_requirements)
            or from ONE selected job. If None, role alignment falls back to
            the older text-match signal instead of skill overlap.

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

    # ---- Skills section (resume QUALITY) ------------------------------------
    # Present if recruiter-known skills were found OR the resume has a Skills
    # heading. Whether those skills fit the role is judged by Role Alignment,
    # so a good resume is not penalised just because no jobs are posted yet.
    has_skill_matches = bool(resume_data.get("skills"))
    has_skills_heading = bool(_SKILLS_HEADING.search(raw_text))
    if has_skill_matches or has_skills_heading:
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
    # Role alignment earns PARTIAL credit (matched / required) instead of a
    # yes/no — so 1 of 10 skills no longer counts as fully aligned, and no
    # arbitrary pass threshold is needed.
    role_alignment_score = None
    role_alignment_credit = 0.0
    required_lower = _clean(required_skills)
    if required_lower:
        candidate_skills_lower = _clean(resume_data.get("skills", []))
        matched = candidate_skills_lower & required_lower
        role_alignment_credit = len(matched) / len(required_lower)
        role_alignment_score = int(role_alignment_credit * 100)
        display = {str(s).strip().lower(): str(s).strip() for s in required_skills if s and str(s).strip()}
        missing_for_role = [display.get(k, k) for k in sorted(required_lower - candidate_skills_lower)]
        if not missing_for_role:
            sections_present.append("Role Alignment")
        else:
            sections_missing.append("Role Alignment")
            tips.append(
                f"Your resume shows {len(matched)} of {len(required_lower)} skills "
                f"recruiters ask for in this role. Missing: {', '.join(missing_for_role)}."
            )
    else:
        # No configured requirements for this role — fall back to the
        # older, weaker text-match signal rather than skipping the check.
        if resume_data.get("role_alignment"):
            sections_present.append("Role Alignment")
            role_alignment_credit = 1.0
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
    if required_lower and raw_text:
        text_lower = raw_text.lower()
        present_keywords = [s for s in required_lower if _contains_skill(text_lower, s)]
        keyword_match_percent = int((len(present_keywords) / len(required_lower)) * 100)

    # ---- Score: 6 sections now (added Quantified Impact) -------------------
    # 5 yes/no checks + role alignment (partial credit 0.0-1.0)
    total_possible = 6
    yes_no_present = len([x for x in sections_present if x != "Role Alignment"])
    earned = yes_no_present + role_alignment_credit
    present_count = len(sections_present)
    resume_score = int((earned / total_possible) * 100)

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
        "role_requirements_available": bool(required_lower),
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