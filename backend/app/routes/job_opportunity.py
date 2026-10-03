"""
Job Opportunity Routes — Recruiter-Posted Jobs Only
===================================================
Jobs enter CPIP only through recruiters:
  - POST /api/jobs        single posting
  - POST /api/jobs/bulk   bulk upload (CSV), validated row by row
No external job APIs.

Matching uses ONE agent (recruiter_matching_agent) in both directions:
  - GET /api/jobs/{job_id}/candidates   recruiter side
  - GET /api/job-match/{student_id}     candidate side ("Matching Roles")
"""

import csv
import io
import json
import logging
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field, field_validator

from app.data.database import AuditLogModel, JobPostingModel, SessionLocal, StudentModel
from app.services.recruiter_matching_agent import (
    MATCHING_RULES,
    match_candidates_for_job,
    match_jobs_for_student,
    parse_skills,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Columns accepted in a bulk upload file. Required columns must be present
# and non-empty on every row.
BULK_REQUIRED_COLUMNS = ["job_title", "company_name", "location", "required_skills"]
BULK_OPTIONAL_COLUMNS = [
    "preferred_skills", "description", "experience_level",
    "employment_type", "salary_range", "posted_by",
]


# ── Helpers ────────────────────────────────────────────────────────

def _job_to_dict(job: JobPostingModel):
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "location": job.location,
        "required_skills": parse_skills(job.required_skills),
        "preferred_skills": parse_skills(job.preferred_skills),
        "description": job.description,
        "min_cgpa": job.min_cgpa,
        "experience_level": job.experience_level,
        "employment_type": job.employment_type,
        "salary_range": job.salary_range,
        "posted_by": job.posted_by,
        "is_active": job.is_active,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def _write_audit(db, event_type: str, details: dict, student_id: Optional[int] = None):
    """Record a decision trail entry. Never blocks the main action."""
    try:
        details = {**details, "rules_version": MATCHING_RULES["version"]}
        db.add(AuditLogModel(
            student_id=student_id,
            event_type=event_type,
            details=json.dumps(details, default=str),
        ))
        db.commit()
    except Exception as exc:  # audit failure must not lose the posting
        db.rollback()
        logger.error("Audit write failed for %s: %s", event_type, exc)


def _audit_summary(matches):
    return [
        {"student_id": m["student_id"], "fit_score": m["fit_score"], "fit_category": m["fit_category"]}
        for m in matches
    ]


def _clean_skill_list(values: List[str]) -> List[str]:
    seen, cleaned = set(), []
    for v in values:
        s = str(v).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            cleaned.append(s)
    return cleaned


# ── Request models ────────────────────────────────────────────────

class JobPostRequest(BaseModel):
    title: str
    company_name: str
    location: str
    required_skills: List[str]
    preferred_skills: List[str] = Field(default_factory=list)
    min_cgpa: Optional[float] = 0
    experience_level: Optional[str] = "Fresher"
    employment_type: Optional[str] = "Full-Time"
    description: Optional[str] = None
    salary_range: Optional[str] = None
    posted_by: Optional[str] = "Recruiter"

    @field_validator("title", "company_name", "location")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()

    @field_validator("required_skills")
    @classmethod
    def needs_required_skills(cls, v: List[str]) -> List[str]:
        cleaned = _clean_skill_list(v)
        if not cleaned:
            raise ValueError("at least one required skill is needed for matching")
        return cleaned

    @field_validator("preferred_skills")
    @classmethod
    def clean_preferred(cls, v: List[str]) -> List[str]:
        return _clean_skill_list(v)

    @field_validator("min_cgpa")
    @classmethod
    def cgpa_range(cls, v: Optional[float]) -> float:
        v = v or 0
        if v < 0 or v > 10:
            raise ValueError("min_cgpa must be between 0 and 10")
        return v


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    min_cgpa: Optional[float] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: Optional[bool] = None


def _create_job(db, data: JobPostRequest) -> JobPostingModel:
    job = JobPostingModel(
        title=data.title,
        company_name=data.company_name,
        location=data.location,
        required_skills=json.dumps(data.required_skills),
        preferred_skills=json.dumps(data.preferred_skills),
        min_cgpa=data.min_cgpa,
        experience_level=data.experience_level,
        employment_type=data.employment_type,
        description=data.description,
        salary_range=data.salary_range,
        posted_by=data.posted_by,
        is_active=True,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# ── Recruiter: post a single job ──────────────────────────────────

@router.post("/jobs")
def post_job(job: JobPostRequest):
    db = SessionLocal()
    try:
        new_job = _create_job(db, job)
        students = db.query(StudentModel).all()
        matches = match_candidates_for_job(new_job, students)

        _write_audit(db, "JobPostedAndMatched", {
            "job_id": new_job.id,
            "source": "single",
            "matched_candidates": _audit_summary(matches),
        })

        return {
            "job": _job_to_dict(new_job),
            "auto_matched_candidates": matches,
            "message": f"Job '{new_job.title}' posted. {len(matches)} candidate(s) matched.",
        }
    finally:
        db.close()


# ── Recruiter: bulk upload (CSV) ──────────────────────────────────

@router.post("/jobs/bulk")
async def bulk_upload_jobs(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded CSV")

    reader = csv.DictReader(io.StringIO(text))
    headers = [h.strip() for h in (reader.fieldnames or [])]
    missing_cols = [c for c in BULK_REQUIRED_COLUMNS if c not in headers]
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required column(s): {', '.join(missing_cols)}. "
                   f"Required: {', '.join(BULK_REQUIRED_COLUMNS)}. "
                   f"Optional: {', '.join(BULK_OPTIONAL_COLUMNS)}.",
        )

    db = SessionLocal()
    try:
        students = db.query(StudentModel).all()
        created, errors = [], []

        # Row 1 is the header, so data starts at row 2 (matches Excel numbering).
        for row_number, row in enumerate(reader, start=2):
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            if not any(row.values()):
                continue  # skip blank lines
            try:
                payload = JobPostRequest(
                    title=row.get("job_title", ""),
                    company_name=row.get("company_name", ""),
                    location=row.get("location", ""),
                    required_skills=row.get("required_skills", "").split(","),
                    preferred_skills=row.get("preferred_skills", "").split(","),
                    min_cgpa=float(row["min_cgpa"]) if row.get("min_cgpa") else 0,
                    experience_level=row.get("experience_level") or "Fresher",
                    employment_type=row.get("employment_type") or "Full-Time",
                    description=row.get("description") or None,
                    salary_range=row.get("salary_range") or None,
                    posted_by=row.get("posted_by") or "Recruiter",
                )
            except ValueError as exc:
                # pydantic ValidationError and float() errors are both ValueError
                errors.append({"row": row_number, "job_title": row.get("job_title", ""),
                               "error": _short_error(exc)})
                continue

            job = _create_job(db, payload)
            matches = match_candidates_for_job(job, students)
            created.append({**_job_to_dict(job), "matched_candidates_count": len(matches)})
            _write_audit(db, "JobPostedAndMatched", {
                "job_id": job.id,
                "source": "bulk",
                "file_name": file.filename,
                "row": row_number,
                "matched_candidates": _audit_summary(matches),
            })

        _write_audit(db, "BulkJobUpload", {
            "file_name": file.filename,
            "saved_count": len(created),
            "error_count": len(errors),
            "errors": errors,
        })

        return {
            "saved_count": len(created),
            "error_count": len(errors),
            "jobs": created,
            "errors": errors,
            "message": f"{len(created)} job(s) saved, {len(errors)} row(s) rejected.",
        }
    finally:
        db.close()


def _short_error(exc: Exception) -> str:
    errors = getattr(exc, "errors", None)
    if callable(errors):
        parts = []
        for e in errors():
            field = ".".join(str(p) for p in e.get("loc", []))
            msg = e.get("msg", "").replace("Value error, ", "")
            parts.append(f"{field}: {msg}" if field else msg)
        return "; ".join(parts)
    return f"min_cgpa: {exc}" if "float" in str(exc) else str(exc)


# ── List jobs ──────────────────────────────────────────────────────

@router.get("/jobs")
def list_jobs(include_closed: bool = False):
    db = SessionLocal()
    try:
        query = db.query(JobPostingModel)
        if not include_closed:
            query = query.filter(JobPostingModel.is_active == True)
        jobs = query.order_by(JobPostingModel.created_at.desc()).all()
        return {"total": len(jobs), "jobs": [_job_to_dict(j) for j in jobs]}
    finally:
        db.close()


# ── Recruiter: edit / close a job ─────────────────────────────────

@router.patch("/jobs/{job_id}")
def update_job(job_id: int, req: JobUpdateRequest):
    db = SessionLocal()
    try:
        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        changes = req.model_dump(exclude_unset=True)
        for field in ("title", "company_name", "location"):
            if field in changes and not (changes[field] or "").strip():
                raise HTTPException(status_code=422, detail=f"{field} must not be empty")
        if "required_skills" in changes:
            cleaned = _clean_skill_list(changes["required_skills"] or [])
            if not cleaned:
                raise HTTPException(status_code=422, detail="at least one required skill is needed")
            changes["required_skills"] = json.dumps(cleaned)
        if "preferred_skills" in changes:
            changes["preferred_skills"] = json.dumps(_clean_skill_list(changes["preferred_skills"] or []))
        if "min_cgpa" in changes and changes["min_cgpa"] is not None and not 0 <= changes["min_cgpa"] <= 10:
            raise HTTPException(status_code=422, detail="min_cgpa must be between 0 and 10")

        for field, value in changes.items():
            setattr(job, field, value)
        db.commit()
        db.refresh(job)

        _write_audit(db, "JobUpdated", {"job_id": job.id, "changed_fields": list(changes.keys())})
        return {"job": _job_to_dict(job)}
    finally:
        db.close()


@router.delete("/jobs/{job_id}")
def close_job(job_id: int):
    """Closes the posting (kept for audit history). Candidates stop seeing it."""
    db = SessionLocal()
    try:
        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        job.is_active = False
        db.commit()
        _write_audit(db, "JobClosed", {"job_id": job.id})
        return {"message": f"Job '{job.title}' closed. It is no longer shown to candidates."}
    finally:
        db.close()


# ── Recruiter side: matching candidates for a job ─────────────────

@router.get("/jobs/{job_id}/candidates")
def get_matched_candidates_for_job(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(JobPostingModel).filter(JobPostingModel.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        students = db.query(StudentModel).all()
        matches = match_candidates_for_job(job, students)
        return {
            "job_id": job_id,
            "job_title": job.title,
            "total_matched": len(matches),
            "candidates": matches,
            "rules_version": MATCHING_RULES["version"],
        }
    finally:
        db.close()


# ── Candidate side: matching roles for a student ──────────────────

@router.get("/job-match/{student_id}")
def get_job_matches(student_id: int, location: Optional[str] = None):
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

        open_jobs = db.query(JobPostingModel).filter(JobPostingModel.is_active == True).all()
        matches = match_jobs_for_student(student, open_jobs)

        _write_audit(db, "MatchingRolesViewed", {
            "open_jobs_evaluated": len(open_jobs),
            "matches": [
                {"job_id": m["job_id"], "fit_score": m["fit_score"], "fit_category": m["fit_category"]}
                for m in matches
            ],
        }, student_id=student_id)

        return {
            "student_id": student_id,
            "job_match_analysis": {
                "all_matches": matches,
                "suitable_jobs": matches,
                "open_jobs_evaluated": len(open_jobs),
                "recommendation_count": len(matches),
                "recommendation_summary": (
                    f"{len(matches)} posted role(s) match your profile"
                    if matches else
                    "No matching roles yet. New roles appear here when recruiters post jobs that fit your skills."
                ),
            },
            "rules_version": MATCHING_RULES["version"],
            "message": "Job matching completed successfully",
        }
    finally:
        db.close()


@router.get("/job-match")
def list_all_job_matches():
    db = SessionLocal()
    try:
        students = db.query(StudentModel).all()
        open_jobs = db.query(JobPostingModel).filter(JobPostingModel.is_active == True).all()
        results = [
            {
                "student_id": s.id,
                "target_role": s.target_role,
                "suitable_jobs_count": len(match_jobs_for_student(s, open_jobs)),
            }
            for s in students
        ]
        return {"total_students": len(results), "job_matches": results}
    finally:
        db.close()


# ── Student notifications (placeholder, unchanged) ────────────────

@router.get("/notifications/{student_id}")
def get_student_notifications(student_id: int):
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        return {"student_id": student_id, "notifications": [], "unread_count": 0}
    finally:
        db.close()
