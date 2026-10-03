"""
CPIP Seed Data — DATABASE VERSION
All data now persists in PostgreSQL database.
"""

import json
from datetime import datetime
from app.data.database import SessionLocal, init_db
from app.data.database import (
    StudentModel, JobPostingModel, ResumeModel, InterviewAssessmentModel,
    ReadinessScoreModel,
    AuditLogModel,
    RecruiterModel, JobApplicationModel
)

# Initialize database on startup
init_db()


def _get_db():
    return SessionLocal()


# ── STUDENTS ──

def get_student(student_id):
    db = _get_db()
    try:
        s = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not s:
            return None
        return _student_to_dict(s)
    finally:
        db.close()


def get_all_students():
    db = _get_db()
    try:
        students = db.query(StudentModel).all()
        return [_student_to_dict(s) for s in students]
    finally:
        db.close()


def add_student(student_data):
    db = _get_db()
    try:
        email = student_data.get("email", "")

        if email:
            existing = db.query(StudentModel).filter(
                StudentModel.email == email
            ).first()
            if existing:
                old_role = existing.target_role
                new_role = student_data.get("target_role", existing.target_role)

                existing.name = student_data.get("name", existing.name)
                existing.target_role = new_role
                existing.skills = json.dumps(student_data.get("skills", []))
                existing.degree = student_data.get("degree", existing.degree)
                existing.resume = student_data.get("resume", existing.resume)

                if student_data.get("github_link"):
                    existing.github_link = student_data.get("github_link")
                if student_data.get("linkedin_id"):
                    existing.linkedin_id = student_data.get("linkedin_id")

                db.commit()
                db.refresh(existing)

                if old_role and new_role and old_role.strip().lower() != new_role.strip().lower():
                    old_scores = db.query(ReadinessScoreModel).filter(
                        ReadinessScoreModel.student_id == existing.id
                    ).first()
                    if old_scores:
                        old_scores.skill_gap_score = 0
                        old_scores.portfolio_score = 0
                        old_scores.resume_score = 0
                        old_scores.interview_readiness_score = 0
                        db.commit()

                return _student_to_dict(existing)

        new_student = StudentModel(
            name=student_data.get("name", "Candidate"),
            email=student_data.get("email", ""),
            degree=student_data.get("degree", "Not specified"),
            cgpa=student_data.get("cgpa", 0),
            location=student_data.get("location", "Not specified"),
            target_role=student_data.get("target_role", ""),
            github_link=student_data.get("github_link", ""),
            linkedin_id=student_data.get("linkedin_id", ""),
            resume=student_data.get("resume", ""),
            salary_expected=student_data.get("salary_expected", 0),
            skills=json.dumps(student_data.get("skills", [])),
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return _student_to_dict(new_student)
    finally:
        db.close()


def _student_to_dict(s):
    return {
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "degree": s.degree,
        "cgpa": s.cgpa,
        "location": s.location,
        "target_role": s.target_role,
        "github_link": s.github_link,
        "linkedin_id": s.linkedin_id,
        "deployed_demo_link": s.deployed_demo_link,
        "project_readme_link": s.project_readme_link,
        "resume": s.resume,
        "salary_expected": s.salary_expected,
        "skills": json.loads(s.skills) if s.skills else [],
    }


# ── JOBS ──

def get_all_jobs():
    db = _get_db()
    try:
        jobs = db.query(JobPostingModel).filter(
            JobPostingModel.is_active == True
        ).all()
        return [_job_to_dict(j) for j in jobs]
    finally:
        db.close()


def get_job(job_id):
    db = _get_db()
    try:
        j = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        return _job_to_dict(j) if j else None
    finally:
        db.close()


def get_job_by_id(job_id):
    db = _get_db()
    try:
        return db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
    finally:
        db.close()


def add_job(job_data):
    db = _get_db()
    try:
        new_job = JobPostingModel(
            title=job_data.get("job_title") or job_data.get("title", "Untitled"),
            company_name=job_data.get("company_name", "Unknown"),
            location=job_data.get("location", "Remote"),
            required_skills=json.dumps(job_data.get("required_skills", [])),
            preferred_skills=json.dumps(job_data.get("preferred_skills", [])),
            min_cgpa=job_data.get("min_cgpa", 0),
            experience_level=job_data.get("experience_level") or "Fresher",
            employment_type=job_data.get("employment_type", "Full-Time"),
            salary_range=job_data.get("salary_range", None),
            posted_by=job_data.get("posted_by", "Recruiter"),
            is_active=True,
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return _job_to_dict(new_job)
    finally:
        db.close()


def add_job_with_recruiter(
    job_title, company_name, location,
    required_skills, min_cgpa, experience_level,
    job_type, employment_type
):
    db = _get_db()
    try:
        new_job = JobPostingModel(
            title=job_title,
            company_name=company_name,
            location=location,
            required_skills=json.dumps(required_skills),
            preferred_skills=json.dumps([]),
            min_cgpa=min_cgpa,
            experience_level=experience_level,
            employment_type=employment_type,
            is_active=True,
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job
    finally:
        db.close()


def update_job_by_id(job_id, update_data):
    db = _get_db()
    try:
        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            return None
        for key, value in update_data.items():
            if key == "required_skills" and isinstance(value, list):
                value = json.dumps(value)
            if hasattr(job, key):
                setattr(job, key, value)
        db.commit()
        db.refresh(job)
        return job
    finally:
        db.close()


def delete_job_by_id(job_id):
    db = _get_db()
    try:
        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            return False
        job.is_active = False
        db.commit()
        return True
    finally:
        db.close()


def job_exists(job_title, company_name):
    db = _get_db()
    try:
        existing = db.query(JobPostingModel).filter(
            JobPostingModel.title == job_title,
            JobPostingModel.company_name == company_name
        ).first()
        return existing is not None
    finally:
        db.close()


def search_jobs(jobs, query):
    if not query or not query.strip():
        return jobs
    q = query.strip().lower()
    results = []
    for job in jobs:
        haystack = " ".join([
            job.get("job_title", ""),
            job.get("company_name", ""),
            job.get("location", ""),
            " ".join(job.get("required_skills", [])),
        ]).lower()
        if q in haystack:
            results.append(job)
    return results


def _job_to_dict(j):
    return {
        "id": j.id,
        "job_title": j.title,
        "company_name": j.company_name,
        "location": j.location,
        "required_skills": json.loads(j.required_skills) if j.required_skills else [],
        "preferred_skills": json.loads(j.preferred_skills) if j.preferred_skills else [],
        "min_cgpa": j.min_cgpa,
        "experience_level": j.experience_level,
        "employment_type": j.employment_type,
        "salary_range": j.salary_range,
        "posted_by": j.posted_by,
        "is_active": j.is_active,
    }


def get_all_skill_names():
    all_skills = set()
    for job in get_all_jobs():
        all_skills.update(job.get("required_skills", []))
        all_skills.update(job.get("preferred_skills", []))
    return sorted(all_skills)


# ── RESUMES ──

def get_resume(student_id):
    db = _get_db()
    try:
        # Prefer the resume the student selected; otherwise the most recent one
        r = db.query(ResumeModel).filter(
            ResumeModel.student_id == student_id
        ).order_by(
            ResumeModel.is_selected.desc(),
            ResumeModel.uploaded_at.desc()
        ).first()
        if not r:
            return None
        if r.resume_json:
            return json.loads(r.resume_json)
        return None
    finally:
        db.close()


def add_resume(student_id, resume_data):
    db = _get_db()
    try:
        existing = db.query(ResumeModel).filter(
            ResumeModel.student_id == student_id
        ).first()
        if existing:
            existing.resume_json = json.dumps(resume_data)
        else:
            new_resume = ResumeModel(
                student_id=student_id,
                resume_json=json.dumps(resume_data),
            )
            db.add(new_resume)
        db.commit()
        return resume_data
    finally:
        db.close()


# ── READINESS SCORES ──

def get_readiness_scores(student_id):
    db = _get_db()
    try:
        r = db.query(ReadinessScoreModel).filter(
            ReadinessScoreModel.student_id == student_id
        ).first()
        if not r:
            return {
                "skill_gap_score": 0,
                "portfolio_score": 0,
                "resume_score": 0,
                "interview_readiness_score": 0,
            }
        return {
            "skill_gap_score": r.skill_gap_score,
            "portfolio_score": r.portfolio_score,
            "resume_score": r.resume_score,
            "interview_readiness_score": r.interview_readiness_score,
        }
    finally:
        db.close()


def update_readiness_scores(student_id, scores):
    db = _get_db()
    try:
        existing = db.query(ReadinessScoreModel).filter(
            ReadinessScoreModel.student_id == student_id
        ).first()
        if existing:
            for key, value in scores.items():
                setattr(existing, key, value)
        else:
            new_score = ReadinessScoreModel(
                student_id=student_id,
                **scores
            )
            db.add(new_score)
        db.commit()
    finally:
        db.close()


# ── ROLE REQUIREMENTS ──

def _parse_skill_list(raw):
    """Skills are stored as a JSON array, but tolerate comma-separated text."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except (ValueError, TypeError):
        return [s.strip() for s in str(raw).split(",")]


def get_role_requirements(role_name):
    """
    Required skills for a target ROLE, built from real recruiter postings.

    Source: every ACTIVE job posting whose title contains role_name.
    Skills are combined across those postings; skills asked for by more
    postings come first. Nothing is hardcoded.

    Returns None when no recruiter has posted a job for this role yet, so
    callers can honestly say "no role data yet" instead of guessing.
    """
    if not role_name or not str(role_name).strip():
        return None

    db = _get_db()
    try:
        postings = db.query(JobPostingModel).filter(
            JobPostingModel.is_active == True,
            JobPostingModel.title.ilike(f"%{role_name.strip()}%")
        ).all()
        if not postings:
            return None

        demand = {}  # lowercase skill -> {"skill": display name, "count": n}
        for job in postings:
            seen_in_this_job = set()
            for skill in _parse_skill_list(job.required_skills):
                name = str(skill).strip()
                key = name.lower()
                if not key or key in seen_in_this_job:
                    continue
                seen_in_this_job.add(key)
                if key in demand:
                    demand[key]["count"] += 1
                else:
                    demand[key] = {"skill": name, "count": 1}

        if not demand:
            return None

        ordered = sorted(demand.values(), key=lambda d: (-d["count"], d["skill"].lower()))
        return {
            "role": role_name.strip(),
            "required_skills": [d["skill"] for d in ordered],
            "skill_demand": {d["skill"]: d["count"] for d in ordered},
            "job_postings_analyzed": len(postings),
            "source": "recruiter_job_postings",
        }
    finally:
        db.close()

def get_role_names():
    return []

def get_all_target_roles():
    """
    Every distinct role title recruiters have posted (active jobs only),
    with the required skills combined across postings of that title.
    Returns {display_title: {"required_skills": [...], "skill_demand": {...},
                             "job_postings": n}}. Empty dict if no postings.
    """
    db = _get_db()
    try:
        postings = db.query(JobPostingModel).filter(JobPostingModel.is_active == True).all()
        roles = {}
        for job in postings:
            if not job.title or not job.title.strip():
                continue
            key = job.title.strip().lower()
            role = roles.setdefault(key, {"title": job.title.strip(), "demand": {}, "job_postings": 0})
            role["job_postings"] += 1
            seen = set()
            for skill in _parse_skill_list(job.required_skills):
                name = str(skill).strip()
                k = name.lower()
                if not k or k in seen:
                    continue
                seen.add(k)
                entry = role["demand"].setdefault(k, {"skill": name, "count": 0})
                entry["count"] += 1

        result = {}
        for role in roles.values():
            ordered = sorted(role["demand"].values(), key=lambda d: (-d["count"], d["skill"].lower()))
            result[role["title"]] = {
                "required_skills": [d["skill"] for d in ordered],
                "skill_demand": {d["skill"]: d["count"] for d in ordered},
                "job_postings": role["job_postings"],
            }
        return result
    finally:
        db.close()


# ── RECRUITERS ──

def add_recruiter(recruiter_data):
    db = _get_db()
    try:
        new_recruiter = RecruiterModel(
            name=recruiter_data.get("name", "Recruiter"),
            email=recruiter_data.get("email", ""),
            company=recruiter_data.get("company", "Unknown"),
            phone=recruiter_data.get("phone", ""),
        )
        db.add(new_recruiter)
        db.commit()
        db.refresh(new_recruiter)
        return _recruiter_to_dict(new_recruiter)
    finally:
        db.close()


def get_recruiter(recruiter_id):
    db = _get_db()
    try:
        r = db.query(RecruiterModel).filter(RecruiterModel.id == recruiter_id).first()
        return _recruiter_to_dict(r) if r else None
    finally:
        db.close()


def _recruiter_to_dict(r):
    if not r:
        return None
    return {
        "id": r.id,
        "name": r.name,
        "email": r.email,
        "company": r.company,
        "phone": r.phone,
        "created_at": str(r.created_at) if r.created_at else None,
    }


# ── JOB APPLICATIONS ──

def add_job_application(application_data):
    db = _get_db()
    try:
        new_app = JobApplicationModel(
            job_id=application_data.get("job_id"),
            student_id=application_data.get("student_id"),
            status=application_data.get("status", "Applied"),
            fit_score=application_data.get("fit_score", 0),
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return _job_application_to_dict(new_app)
    finally:
        db.close()


def get_job_application(application_id):
    db = _get_db()
    try:
        app = db.query(JobApplicationModel).filter(
            JobApplicationModel.id == application_id
        ).first()
        return _job_application_to_dict(app) if app else None
    finally:
        db.close()


def get_applications_for_job(job_id):
    db = _get_db()
    try:
        apps = db.query(JobApplicationModel).filter(
            JobApplicationModel.job_id == job_id
        ).all()
        return [_job_application_to_dict(a) for a in apps]
    finally:
        db.close()


def get_applications_for_student(student_id):
    db = _get_db()
    try:
        apps = db.query(JobApplicationModel).filter(
            JobApplicationModel.student_id == student_id
        ).all()
        return [_job_application_to_dict(a) for a in apps]
    finally:
        db.close()


def update_application_status(application_id, new_status):
    db = _get_db()
    try:
        app = db.query(JobApplicationModel).filter(
            JobApplicationModel.id == application_id
        ).first()
        if not app:
            return None
        app.status = new_status
        if new_status == "Shortlisted":
            app.shortlisted_date = datetime.utcnow()
        elif new_status == "Interview":
            app.interviewed_date = datetime.utcnow()
        elif new_status == "Offered":
            app.offer_date = datetime.utcnow()
        db.commit()
        db.refresh(app)
        return _job_application_to_dict(app)
    finally:
        db.close()


def _job_application_to_dict(app):
    if not app:
        return None
    return {
        "id": app.id,
        "job_id": app.job_id,
        "student_id": app.student_id,
        "status": app.status,
        "fit_score": app.fit_score,
        "applied_date": str(app.applied_date) if app.applied_date else None,
        "shortlisted_date": str(app.shortlisted_date) if app.shortlisted_date else None,
        "interviewed_date": str(app.interviewed_date) if app.interviewed_date else None,
        "offer_date": str(app.offer_date) if app.offer_date else None,
    }


def mark_notification_read(notification_id):
    return None

# ── INTERVIEW ASSESSMENTS (mock interviews recorded by a human) ──

INTERVIEW_DIMENSIONS = ["aptitude", "technical", "communication", "project_explanation"]


def _assessment_to_dict(a):
    return {
        "id": a.id,
        "student_id": a.student_id,
        "aptitude_score": a.aptitude_score,
        "technical_score": a.technical_score,
        "communication_score": a.communication_score,
        "project_explanation_score": a.project_explanation_score,
        "notes": a.notes,
        "assessed_by": a.assessed_by,
        "assessed_at": a.assessed_at.isoformat() if a.assessed_at else None,
    }


def add_interview_assessment(student_id, data):
    db = _get_db()
    try:
        row = InterviewAssessmentModel(
            student_id=student_id,
            aptitude_score=data.get("aptitude_score"),
            technical_score=data.get("technical_score"),
            communication_score=data.get("communication_score"),
            project_explanation_score=data.get("project_explanation_score"),
            notes=data.get("notes"),
            assessed_by=data["assessed_by"],
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _assessment_to_dict(row)
    finally:
        db.close()


def get_interview_assessments(student_id):
    """All assessments for a student, newest first."""
    db = _get_db()
    try:
        rows = db.query(InterviewAssessmentModel).filter(
            InterviewAssessmentModel.student_id == student_id
        ).order_by(InterviewAssessmentModel.assessed_at.desc(), InterviewAssessmentModel.id.desc()).all()
        return [_assessment_to_dict(r) for r in rows]
    finally:
        db.close()


def get_latest_interview_scores(student_id):
    """
    Most recent assessed value for EACH dimension (a later session may assess
    only some dimensions). Unassessed dimensions are None — never a default.
    Returns (scores_dict, evidence_dict).
    """
    scores = {f"{d}_score": None for d in INTERVIEW_DIMENSIONS}
    evidence = {}
    for a in get_interview_assessments(student_id):  # newest first
        for d in INTERVIEW_DIMENSIONS:
            key = f"{d}_score"
            if scores[key] is None and a.get(key) is not None:
                scores[key] = a[key]
                evidence[d] = {
                    "assessment_id": a["id"],
                    "assessed_by": a["assessed_by"],
                    "assessed_at": a["assessed_at"],
                    "notes": a["notes"],
                }
    return scores, evidence


# ── AUDIT TRAIL ──

def save_audit_record(record):
    """Persist an audit_agent record into audit_logs. Returns it with its real id."""
    from app.data.database import AuditLogModel
    db = _get_db()
    try:
        row = AuditLogModel(
            student_id=record.get("candidate_id"),
            event_type=record.get("event_type"),
            details=json.dumps(record, default=str),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {**record, "audit_id": row.id, "audit_status": "recorded"}
    finally:
        db.close()


def get_audit_logs(student_id, limit=50):
    from app.data.database import AuditLogModel
    db = _get_db()
    try:
        rows = db.query(AuditLogModel).filter(
            AuditLogModel.student_id == student_id
        ).order_by(AuditLogModel.created_at.desc(), AuditLogModel.id.desc()).limit(limit).all()
        out = []
        for r in rows:
            try:
                details = json.loads(r.details) if r.details else {}
            except (ValueError, TypeError):
                details = {"raw": r.details}
            out.append({
                "audit_id": r.id,
                "event_type": r.event_type,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "details": details,
            })
        return out
    finally:
        db.close()
