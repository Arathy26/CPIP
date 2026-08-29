"""
CPIP Seed Data — DATABASE VERSION
All data now persists in PostgreSQL database.
"""

import json
from datetime import datetime
from app.data.database import SessionLocal, init_db
from app.data.database import (
    StudentModel, JobModel, ResumeModel,
    ReadinessScoreModel,
    MarketSkillCacheModel, AuditLogModel,
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

                # Clear old skill gap cache if role changed
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

        # Create new student
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
        "resume": s.resume,
        "salary_expected": s.salary_expected,
        "skills": json.loads(s.skills) if s.skills else [],
    }


# ── JOBS ──

def get_all_jobs():
    db = _get_db()
    try:
        jobs = db.query(JobModel).all()
        return [_job_to_dict(j) for j in jobs]
    finally:
        db.close()


def get_job(job_id):
    db = _get_db()
    try:
        j = db.query(JobModel).filter(JobModel.id == job_id).first()
        return _job_to_dict(j) if j else None
    finally:
        db.close()


def add_job(job_data):
    db = _get_db()
    try:
        new_job = JobModel(
            job_title=job_data["job_title"],
            company_name=job_data.get("company_name", "Unknown"),
            location=job_data.get("location", "Remote"),
            required_skills=json.dumps(job_data.get("required_skills", [])),
            preferred_skills=json.dumps(job_data.get("preferred_skills", [])),
            min_cgpa=job_data.get("min_cgpa", 0),
            min_readiness=job_data.get("min_readiness", 0),
            experience_level=job_data.get("experience_level") or "Not specified",
            posted_date=datetime.now().strftime("%b %d, %Y"),
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        job_dict = _job_to_dict(new_job)

        try:
            from app.services.vector_store import add_job_to_vector_store
            add_job_to_vector_store(job_dict)
        except Exception as e:
            print(f"Vector store error: {e}")

        return job_dict
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
            " ".join(job.get("preferred_skills", [])),
        ]).lower()
        if q in haystack:
            results.append(job)
    return results


def _job_to_dict(j):
    return {
        "id": j.id,
        "job_title": j.job_title,
        "company_name": j.company_name,
        "location": j.location,
        "required_skills": json.loads(j.required_skills) if j.required_skills else [],
        "preferred_skills": json.loads(j.preferred_skills) if j.preferred_skills else [],
        "min_cgpa": j.min_cgpa,
        "min_readiness": j.min_readiness,
        "experience_level": j.experience_level,
        "posted_date": j.posted_date,
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
        r = db.query(ResumeModel).filter(
            ResumeModel.student_id == student_id
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


# ── ROLE REQUIREMENTS (kept for compatibility) ──

def get_role_requirements(role_name):
    return None


def get_role_names():
    return []


def get_all_target_roles():
    return {}


# ── JOB DESCRIPTION CACHE ──

def get_cached_job_description(job_id: str):
    """Get cached job description to avoid repeated API calls."""
    db = _get_db()
    try:
        from app.data.database import JobDescriptionCacheModel
        entry = db.query(JobDescriptionCacheModel).filter(
            JobDescriptionCacheModel.job_id == job_id
        ).first()
        if not entry:
            return None
        return {
            "job_id": entry.job_id,
            "title": entry.title,
            "company": entry.company,
            "description": entry.description,
            "skills_extracted": json.loads(entry.skills_extracted) if entry.skills_extracted else [],
        }
    finally:
        db.close()


def cache_job_description(job_id: str, title: str, company: str, description: str, skills: list):
    """Cache job description and extracted skills."""
    db = _get_db()
    try:
        from app.data.database import JobDescriptionCacheModel
        existing = db.query(JobDescriptionCacheModel).filter(
            JobDescriptionCacheModel.job_id == job_id
        ).first()
        if existing:
            existing.title = title
            existing.company = company
            existing.description = description
            existing.skills_extracted = json.dumps(skills)
            existing.cached_at = datetime.utcnow()  # ← FIXED: was time.time()
        else:
            new_cache = JobDescriptionCacheModel(
                job_id=job_id,
                title=title,
                company=company,
                description=description,
                skills_extracted=json.dumps(skills),
                cached_at=datetime.utcnow(),         # ← FIXED: was time.time()
            )
            db.add(new_cache)
        db.commit()
    finally:
        db.close()


# ── JOB SKILLS CACHE ──

def cache_job_skills(job_id: str, skills: list):
    """Store extracted skills for a job."""
    db = _get_db()
    try:
        from app.data.database import JobSkillsCacheModel
        for skill in skills:
            skill_entry = JobSkillsCacheModel(
                job_id=job_id,
                skill=skill.lower(),
            )
            db.add(skill_entry)
        db.commit()
        print(f"✓ Cached {len(skills)} skills for job '{job_id}'")
    except Exception as e:
        print(f"❌ Error caching skills: {e}")
    finally:
        db.close()


def get_cached_job_skills(job_id: str) -> list:
    """Get cached skills for a specific job."""
    db = _get_db()
    try:
        from app.data.database import JobSkillsCacheModel
        skills = db.query(JobSkillsCacheModel).filter(
            JobSkillsCacheModel.job_id == job_id
        ).all()
        return [s.skill for s in skills] if skills else []
    finally:
        db.close()


# ── MARKET SKILL CACHE ──

def get_cached_market_skill_demand(target_role):
    """Legacy compatibility — not used by new location-aware system."""
    return None


def cache_market_skill_demand(target_role, skill_frequency, total_postings):
    """Legacy compatibility — not used by new location-aware system."""
    return None


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


def update_application_fit_score(application_id, fit_score):
    db = _get_db()
    try:
        app = db.query(JobApplicationModel).filter(
            JobApplicationModel.id == application_id
        ).first()
        if not app:
            return None
        app.fit_score = fit_score
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
    """Stub — notifications not implemented yet."""
    return None