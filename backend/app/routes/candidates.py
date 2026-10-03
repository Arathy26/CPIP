"""
Candidate Profile Routes
API endpoints for candidate profile evaluation and creation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.candidate_profile_agent import candidate_profile_agent, validate_profile
from app.data import seed_data
from app.data.database import SessionLocal, StudentModel, ResumeModel, StudentRoleHistoryModel
import json
from datetime import datetime

router = APIRouter()


class CreateCandidateRequest(BaseModel):
    name: str
    email: str
    degree: str
    cgpa: float
    skills: List[str]
    target_role: str
    github_link: Optional[str] = ""
    linkedin_id: Optional[str] = ""


@router.post("/candidates")
def create_candidate(data: CreateCandidateRequest):
    print(f"\n{'='*70}")
    print(f"✅ CREATE CANDIDATE - POST REQUEST")
    print(f"  Name: {data.name} | Email: {data.email} | Role: {data.target_role}")
    print(f"{'='*70}\n")

    try:
        if not data.name or not data.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        if not data.email or not data.email.strip():
            raise HTTPException(status_code=400, detail="Email is required")
        if not data.target_role or not data.target_role.strip():
            raise HTTPException(status_code=400, detail="Target role is required")
        if not data.skills or len(data.skills) == 0:
            raise HTTPException(status_code=400, detail="At least one skill is required")

        skills = [s.strip() for s in data.skills if s.strip()]
        student_data = {
            "name": data.name.strip(),
            "email": data.email.strip(),
            "degree": data.degree,
            "cgpa": data.cgpa,
            "skills": skills,
            "target_role": data.target_role.strip(),
            "github_link": data.github_link.strip() if data.github_link else "",
            "linkedin_id": data.linkedin_id.strip() if data.linkedin_id else "",
        }

        student = seed_data.add_student(student_data)
        print(f"✅ Student created: ID={student['id']}")

        return {
            "id": student["id"],
            "name": student["name"],
            "email": student["email"],
            "target_role": student["target_role"],
            "skills": student["skills"],
            "message": f"✅ Welcome {student['name']}! Your profile is ready.",
            "next_step": "job-matching"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error creating candidate: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating candidate: {str(e)}")


@router.get("/candidates/{student_id}")
def get_candidate_profile(student_id: int):
    student_data = seed_data.get_student(student_id)
    if not student_data:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    profile = candidate_profile_agent(student_data)
    validation = validate_profile(profile)

    return {
        "candidate_profile": profile,
        "validation": validation,
        "message": "Candidate profile successfully generated"
    }


@router.get("/candidates")
def list_all_candidates():
    profiles = []
    for student_data in seed_data.get_all_students():
        profile = candidate_profile_agent(student_data)
        profiles.append(profile)

    return {
        "total_candidates": len(profiles),
        "candidates": profiles,
        "message": "All candidate profiles retrieved"
    }


@router.get("/readiness-scores/{student_id}")
def get_readiness_scores(student_id: int):
    student = seed_data.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    # Computed LIVE from the agents (not a stale stored row).
    # None means "not assessed yet" - never a fake 0.
    from app.services.orchestrator import collect_agent_outputs, explain
    ctx = collect_agent_outputs(student_id)
    explanation = explain(ctx)
    return {
        "student_id": student_id,
        **ctx["scores"],
        "overall_readiness": explanation["overall_readiness_score"],
        "scores_missing": explanation["scores_missing"],
        "readiness_band": explanation["readiness_band"],
        "calculation": {
            "method": explanation["method"],
            "formula": explanation["formula"],
            "breakdown": explanation["breakdown"],
        },
        "target_role": ctx["target_role"],
    }


@router.get("/students/with-resumes")
def get_students_with_resumes():
    """List all students who have at least one uploaded resume"""
    db = SessionLocal()
    try:
        students_with_resumes = (
            db.query(StudentModel)
            .filter(
                StudentModel.id.in_(
                    db.query(ResumeModel.student_id).distinct()
                )
            )
            .order_by(StudentModel.updated_at.desc())
            .all()
        )

        students = []
        for student in students_with_resumes:
            resumes = (
                db.query(ResumeModel)
                .filter(ResumeModel.student_id == student.id)
                .order_by(ResumeModel.uploaded_at.desc())
                .all()
            )

            skills_list = []
            if student.skills:
                try:
                    skills_list = json.loads(student.skills)
                except:
                    skills_list = [s.strip() for s in student.skills.split(",") if s.strip()]

            selected_resume = next(
                (r for r in resumes if r.is_selected),
                resumes[0] if resumes else None
            )

            students.append({
                "id": student.id,
                "name": student.name or "Unknown",
                "email": student.email,
                "target_role": student.target_role,
                "skills": skills_list,
                "skills_count": len(skills_list),
                "location": student.location,
                "resume_count": len(resumes),
                "resume_status": selected_resume.extraction_status if selected_resume else "none",
                "resume_file": selected_resume.file_name if selected_resume else None,
                "last_upload": selected_resume.uploaded_at.isoformat() if selected_resume and selected_resume.uploaded_at else None,
            })

        return {"total": len(students), "students": students}
    finally:
        db.close()


@router.put("/students/{student_id}/target-role")
def update_target_role(student_id: int, data: dict):
    """Update student target role and save history"""
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        new_role = data.get("target_role", "").strip()
        if not new_role:
            raise HTTPException(status_code=400, detail="target_role is required")

        history = StudentRoleHistoryModel(
            student_id=student_id,
            previous_role=student.target_role,
            new_role=new_role,
            changed_at=datetime.utcnow()
        )
        db.add(history)

        student.target_role = new_role
        student.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "student_id": student_id,
            "previous_role": history.previous_role,
            "new_role": new_role,
            "message": f"Role updated to {new_role}"
        }
    finally:
        db.close()


@router.get("/students/{student_id}/role-history")
def get_role_history(student_id: int):
    """Get role change history for a student"""
    db = SessionLocal()
    try:
        history = (
            db.query(StudentRoleHistoryModel)
            .filter(StudentRoleHistoryModel.student_id == student_id)
            .order_by(StudentRoleHistoryModel.changed_at.desc())
            .all()
        )

        return {
            "student_id": student_id,
            "total_changes": len(history),
            "history": [
                {
                    "id": h.id,
                    "previous_role": h.previous_role,
                    "new_role": h.new_role,
                    "changed_at": h.changed_at.isoformat() if h.changed_at else None
                }
                for h in history
            ]
        }
    finally:
        db.close()


class SkillsUpdateRequest(BaseModel):
    skills: List[str]


@router.put("/students/{student_id}/skills")
def update_student_skills(student_id: int, data: SkillsUpdateRequest):
    """Student adds/removes skills the resume parser missed. Replaces the list."""
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        cleaned, seen = [], set()
        for skill in data.skills:
            name = (skill or "").strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                cleaned.append(name)
        student.skills = json.dumps(cleaned)
        student.updated_at = datetime.utcnow()
        db.commit()
        return {"success": True, "student_id": student_id, "skills": cleaned,
                "message": f"{len(cleaned)} skill(s) saved"}
    finally:
        db.close()


class PortfolioLinksRequest(BaseModel):
    github_link: Optional[str] = None
    linkedin_id: Optional[str] = None
    deployed_demo_link: Optional[str] = None
    project_readme_link: Optional[str] = None


@router.put("/students/{student_id}/portfolio-links")
def update_portfolio_links(student_id: int, data: PortfolioLinksRequest):
    """
    Student adds or updates their own portfolio evidence links.
    Only fields that are sent are changed. Send "" to clear a link.
    """
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        updates = data.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No links provided")

        url_fields = {"github_link", "deployed_demo_link", "project_readme_link"}
        for field, value in updates.items():
            value = (value or "").strip()
            if value and field in url_fields and not value.lower().startswith(("http://", "https://")):
                raise HTTPException(status_code=400, detail=f"{field} must start with http:// or https://")
            setattr(student, field, value or None)

        student.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "student_id": student_id,
            "github_link": student.github_link,
            "linkedin_id": student.linkedin_id,
            "deployed_demo_link": student.deployed_demo_link,
            "project_readme_link": student.project_readme_link,
            "message": "Portfolio links updated"
        }
    finally:
        db.close()


@router.put("/students/{student_id}/location")
def update_student_location(student_id: int, data: dict):
    """Update student preferred location"""
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        new_location = data.get("location", "").strip().lower()
        if not new_location:
            raise HTTPException(status_code=400, detail="location is required")

        student.location = new_location
        student.updated_at = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "student_id": student_id,
            "location": new_location,
            "message": f"Location updated to {new_location}"
        }
    finally:
        db.close()