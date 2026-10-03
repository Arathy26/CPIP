"""
Recruiter Matching Agent
========================
Single source of matching logic for CPIP's recruiter-push job model.

Jobs enter CPIP only when a recruiter posts them (single form or bulk upload).
There are NO external job APIs.

This agent is used in BOTH directions so the result is always identical:
  - Recruiter side: job  -> matching candidates
  - Candidate side: student -> matching open job postings

Deterministic: fit is a rule-based skill score. CGPA is NOT checked.
No LLM is involved in any decision here.
"""

import json

# ---------------------------------------------------------------------------
# MATCHING RULES — the only place thresholds and weights live.
# Change values here (and bump the version) instead of editing logic.
# The version is written into every audit record.
# ---------------------------------------------------------------------------
MATCHING_RULES = {
    "version": "2026-10-01.1",
    # Share of the fit score that comes from required vs preferred skills.
    # Used only when the job has preferred skills; otherwise required = 100%.
    "required_weight": 0.8,
    "preferred_weight": 0.2,
    # Fit categories (checked top-down, score >= min_score).
    "categories": [
        {"label": "Strong Fit", "min_score": 85},
        {"label": "Good Fit", "min_score": 65},
        {"label": "Stretch Fit", "min_score": 40},
        {"label": "Not Suitable Yet", "min_score": 0},
    ],
    # Lowest score that counts as a "match" shown to recruiter or candidate.
    "min_match_score": 40,
}


def parse_skills(raw):
    """Skills are stored as a JSON array string; accept lists or CSV text too."""
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(s).strip() for s in raw if str(s).strip()]
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return [str(s).strip() for s in value if str(s).strip()]
    except (ValueError, TypeError):
        pass
    return [s.strip() for s in str(raw).split(",") if s.strip()]


def _normalise(skills):
    """Map lowercase skill -> original spelling, so output keeps recruiter wording."""
    return {s.lower(): s for s in skills}


def _category(score):
    for cat in MATCHING_RULES["categories"]:
        if score >= cat["min_score"]:
            return cat["label"]
    return MATCHING_RULES["categories"][-1]["label"]


def evaluate_match(student, job):
    """
    Evaluate one student against one job posting.
    `student` is a StudentModel, `job` is a JobPostingModel.
    Returns a plain dict — same structure for both sides.
    """
    student_skills = _normalise(parse_skills(student.skills))
    required = _normalise(parse_skills(job.required_skills))
    preferred = _normalise(parse_skills(job.preferred_skills))

    matched_required = [required[k] for k in required if k in student_skills]
    missing_required = [required[k] for k in required if k not in student_skills]
    matched_preferred = [preferred[k] for k in preferred if k in student_skills]
    missing_preferred = [preferred[k] for k in preferred if k not in student_skills]

    required_pct = (len(matched_required) / len(required) * 100) if required else 0.0
    preferred_pct = (len(matched_preferred) / len(preferred) * 100) if preferred else 0.0

    if preferred:
        fit = (required_pct * MATCHING_RULES["required_weight"]
               + preferred_pct * MATCHING_RULES["preferred_weight"])
    else:
        fit = required_pct
    fit_score = int(round(min(100, max(0, fit))))

    # Matching is skills-only. CGPA is intentionally not checked.
    fit_category = _category(fit_score)
    is_match = fit_score >= MATCHING_RULES["min_match_score"]

    # ── Human-readable reason built only from the facts above ──
    parts = [f"Has {len(matched_required)} of {len(required)} required skills"]
    if missing_required:
        parts.append("missing required: " + ", ".join(missing_required))
    if preferred:
        parts.append(f"has {len(matched_preferred)} of {len(preferred)} preferred skills")
    reason = "; ".join(parts) + "."

    return {
        "student_id": student.id,
        "job_id": job.id,
        "fit_score": fit_score,
        "fit_category": fit_category,
        "is_match": is_match,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_preferred_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "required_coverage_percent": int(round(required_pct)),
        "preferred_coverage_percent": int(round(preferred_pct)),
        "reason": reason,
        "rules_version": MATCHING_RULES["version"],
    }


def match_candidates_for_job(job, students):
    """Recruiter side: every student who matches this posting, best first."""
    results = []
    for student in students:
        result = evaluate_match(student, job)
        if result["is_match"]:
            result.update({
                "name": student.name,
                "degree": student.degree,
                "cgpa": student.cgpa,
            })
            results.append(result)
    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results


def match_jobs_for_student(student, jobs):
    """Candidate side: every OPEN posting that matches this student, best first."""
    results = []
    for job in jobs:
        if not job.is_active:
            continue
        result = evaluate_match(student, job)
        if result["is_match"]:
            result.update({
                "job_title": job.title,
                "company_name": job.company_name,
                "location": job.location,
                "employment_type": job.employment_type,
                "experience_level": job.experience_level,
                "salary_range": job.salary_range,
                "description": job.description,
                "posted_by": job.posted_by,
                "required_skills": parse_skills(job.required_skills),
                "preferred_skills": parse_skills(job.preferred_skills),
            })
            results.append(result)
    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results


# Backwards-compatible name used by routes/recruiter_jobs.py
def get_matched_candidates_for_job(job, all_students, readiness_scores_map=None):
    return match_candidates_for_job(job, all_students)
