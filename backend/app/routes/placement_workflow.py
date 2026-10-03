"""
Placement Workflow Routes

One workflow per APPLICATION (student + job), stored in job_applications.
Humans move stages; placement_workflow_agent validates the move and
describes the next action. Every change is written to audit_logs.
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data.database import (
    SessionLocal, StudentModel, JobPostingModel, JobApplicationModel, AuditLogModel,
)
from app.agents.placement_workflow_agent import (
    placement_workflow_agent, validate_workflow_result, validate_transition,
    normalise_stage, STAGE_LABELS,
)
from app.services.recruiter_matching_agent import evaluate_match, MATCHING_RULES

router = APIRouter()

INITIAL_STAGES = {"recommended", "applied"}
INTERVIEW_STAGES = {"round_1_scheduled", "round_1_completed", "technical_round", "hr_round"}


class ApplicationCreateRequest(BaseModel):
    student_id: int
    job_id: int
    initial_stage: Optional[str] = "applied"   # "applied" (student) or "recommended" (placement officer)
    created_by: Optional[str] = "student"


class StageUpdateRequest(BaseModel):
    new_stage: str
    updated_by: str            # human making the change (placement officer / recruiter)
    notes: Optional[str] = None


def _audit(db, student_id, event_type, details):
    db.add(AuditLogModel(student_id=student_id, event_type=event_type,
                         details=json.dumps(details, default=str)))


def _describe(app, job, student):
    match = evaluate_match(student, job) if (student and job) else {}
    return placement_workflow_agent({
        "student_id": app.student_id,
        "application_id": app.id,
        "job_id": app.job_id,
        "job_title": job.title if job else None,
        "current_stage": app.status,
        "missing_required_skills": match.get("missing_required_skills", []),
    })


def _application_view(app, job, student):
    workflow = _describe(app, job, student)
    return {
        "application_id": app.id,
        "job_id": app.job_id,
        "job_title": job.title if job else None,
        "company_name": job.company_name if job else None,
        "fit_score_at_application": app.fit_score,
        "applied_date": app.applied_date.isoformat() if app.applied_date else None,
        "shortlisted_date": app.shortlisted_date.isoformat() if app.shortlisted_date else None,
        "interviewed_date": app.interviewed_date.isoformat() if app.interviewed_date else None,
        "offer_date": app.offer_date.isoformat() if app.offer_date else None,
        "last_updated_by": app.updated_by,
        "workflow": workflow,
    }


@router.post("/applications")
def create_application(req: ApplicationCreateRequest):
    stage = normalise_stage(req.initial_stage)
    if stage not in INITIAL_STAGES:
        raise HTTPException(status_code=400, detail=f"initial_stage must be one of: {', '.join(sorted(INITIAL_STAGES))}")

    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == req.student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        job = db.query(JobPostingModel).filter(JobPostingModel.id == req.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if not job.is_active:
            raise HTTPException(status_code=400, detail="Job posting is closed")

        existing = db.query(JobApplicationModel).filter(
            JobApplicationModel.student_id == req.student_id,
            JobApplicationModel.job_id == req.job_id,
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Application already exists (id {existing.id})")

        match = evaluate_match(student, job)
        created_by = (req.created_by or "student").strip()
        app = JobApplicationModel(
            student_id=req.student_id, job_id=req.job_id, status=stage,
            fit_score=match["fit_score"], updated_by=created_by,
        )
        db.add(app)
        db.flush()
        _audit(db, req.student_id, "ApplicationCreated", {
            "application_id": app.id, "job_id": req.job_id, "stage": stage,
            "fit_score": match["fit_score"], "fit_reason": match["reason"],
            "created_by": created_by, "rules_version": MATCHING_RULES["version"],
        })
        db.commit()
        db.refresh(app)
        return {"success": True, "application": _application_view(app, job, student)}
    finally:
        db.close()


@router.put("/applications/{application_id}/status")
def update_application_stage(application_id: int, req: StageUpdateRequest):
    if not req.updated_by or not req.updated_by.strip():
        raise HTTPException(status_code=400, detail="updated_by is required (human-in-the-loop)")

    db = SessionLocal()
    try:
        app = db.query(JobApplicationModel).filter(JobApplicationModel.id == application_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")

        current = normalise_stage(app.status)
        new = normalise_stage(req.new_stage)
        ok, reason = validate_transition(current, new)
        if not ok:
            raise HTTPException(status_code=400, detail=reason)

        now = datetime.utcnow()
        app.status = new
        app.updated_by = req.updated_by.strip()
        if new == "shortlisted" and not app.shortlisted_date:
            app.shortlisted_date = now
        if new in INTERVIEW_STAGES and not app.interviewed_date:
            app.interviewed_date = now
        if new == "offered" and not app.offer_date:
            app.offer_date = now
        if req.notes:
            stamp = f"[{now.isoformat(timespec='minutes')} {app.updated_by}] {req.notes.strip()}"
            app.recruiter_notes = f"{app.recruiter_notes}\n{stamp}" if app.recruiter_notes else stamp

        _audit(db, app.student_id, "WorkflowUpdated", {
            "application_id": app.id, "job_id": app.job_id,
            "from_stage": current, "to_stage": new,
            "updated_by": app.updated_by, "notes": req.notes,
        })
        db.commit()
        db.refresh(app)

        job = db.query(JobPostingModel).filter(JobPostingModel.id == app.job_id).first()
        student = db.query(StudentModel).filter(StudentModel.id == app.student_id).first()
        return {
            "success": True,
            "message": f"Moved from {STAGE_LABELS.get(current, current)} to {STAGE_LABELS[new]}",
            "application": _application_view(app, job, student),
        }
    finally:
        db.close()


@router.get("/placement-workflow/{student_id}")
def get_placement_workflow(student_id: int):
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

        apps = db.query(JobApplicationModel).filter(
            JobApplicationModel.student_id == student_id
        ).order_by(JobApplicationModel.applied_date.desc()).all()

        if not apps:
            workflow = placement_workflow_agent({"student_id": student_id, "current_stage": None})
            return {"student_id": student_id, "total_applications": 0, "applications": [],
                    "placement_workflow": workflow,
                    "validation": validate_workflow_result(workflow)}

        job_ids = {a.job_id for a in apps}
        jobs = {j.id: j for j in db.query(JobPostingModel).filter(JobPostingModel.id.in_(job_ids)).all()}
        views = [_application_view(a, jobs.get(a.job_id), student) for a in apps]
        return {"student_id": student_id, "total_applications": len(views), "applications": views}
    finally:
        db.close()


@router.get("/placement-workflow")
def list_all_placement_workflows():
    db = SessionLocal()
    try:
        rows = db.query(JobApplicationModel).all()
        summary = {}
        for a in rows:
            s = summary.setdefault(a.student_id, {"student_id": a.student_id, "total_applications": 0, "by_stage": {}})
            stage = normalise_stage(a.status)
            s["total_applications"] += 1
            s["by_stage"][stage] = s["by_stage"].get(stage, 0) + 1
        return {"total_students_with_applications": len(summary),
                "placement_workflows": list(summary.values())}
    finally:
        db.close()
