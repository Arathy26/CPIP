"""
Resume Management
Upload, list and select resumes. Skill extraction is DETERMINISTIC:
the resume text is matched against the skills recruiters have posted in
CPIP (seed_data.get_all_skill_names()). No LLM, no external API, no
hardcoded skill list. Students can also edit their skills directly
(PUT /api/students/{id}/skills).
"""

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, ResumeModel
from app.data import seed_data
from app.services.resume_parser import parse_resume, UnsupportedFileTypeError
from datetime import datetime
import os
import json

router = APIRouter()

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _merge_skills(existing, extracted):
    """Keep every skill the student already has, add newly found ones (no duplicates)."""
    merged, seen = [], set()
    for skill in list(existing or []) + list(extracted or []):
        name = str(skill).strip()
        if name and name.lower() not in seen:
            seen.add(name.lower())
            merged.append(name)
    return merged


def _extract_and_save(db, resume, student, file_bytes):
    """
    Parse the resume deterministically and save results on the resume row
    (resume_json is what every readiness agent reads) and on the student.
    """
    target_role = (student.target_role if student else None) or ""
    parsed = parse_resume(
        filename=resume.file_name or "resume.pdf",
        file_bytes=file_bytes,
        target_role=target_role,
        known_skill_names=seed_data.get_all_skill_names(),
    )
    if len((parsed.get("raw_text") or "").strip()) < 10:
        raise ValueError("Could not read text from this file")

    db.query(ResumeModel).filter(
        ResumeModel.student_id == resume.student_id,
        ResumeModel.id != resume.id,
    ).update({"is_selected": False})

    resume.resume_json = json.dumps(parsed)
    resume.skills = json.dumps(parsed["skills"])
    resume.projects = json.dumps(parsed["projects"])
    resume.extraction_status = "completed"
    resume.extraction_error = None
    resume.completed_at = datetime.utcnow()
    resume.is_selected = True

    if student:
        current = json.loads(student.skills) if student.skills else []
        student.skills = json.dumps(_merge_skills(current, parsed["skills"]))
        student.resume = resume.file_path
        links = parsed.get("links") or {}
        if links.get("github") and not student.github_link:
            student.github_link = links["github"]
        if links.get("linkedin") and not student.linkedin_id:
            student.linkedin_id = links["linkedin"]
        student.updated_at = datetime.utcnow()

    db.commit()
    return parsed


def process_resume_background(resume_id: int):
    """Background task for re-uploads: read file, extract deterministically, save."""
    db = SessionLocal()
    resume = None
    try:
        resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not resume:
            return
        if not resume.file_path or not os.path.exists(resume.file_path):
            raise FileNotFoundError(f"File not found: {resume.file_path}")
        with open(resume.file_path, "rb") as f:
            file_bytes = f.read()
        student = db.query(StudentModel).filter(StudentModel.id == resume.student_id).first()
        parsed = _extract_and_save(db, resume, student, file_bytes)
        print(f"Resume {resume_id}: {len(parsed['skills'])} skill(s) matched to recruiter vocabulary")
    except Exception as e:
        print(f"Resume {resume_id} processing failed: {e}")
        if resume is not None:
            db.rollback()
            resume.extraction_status = "failed"
            resume.extraction_error = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/resume/upload")
async def upload_resume_new_student(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    name: str = Form(None),
    email: str = Form(None),
    target_role: str = Form(None),
    location: str = Form(None),
):
    """Upload resume for new OR existing student."""
    db = SessionLocal()
    try:
        if not file.filename.lower().endswith('.pdf'):
            return JSONResponse(status_code=400, content={"detail": "Only PDF files allowed"})

        # Find or create student (by the email the student typed)
        student = None
        if email and email.strip():
            student = db.query(StudentModel).filter(
                StudentModel.email == email.strip()
            ).first()

        if not student:
            safe_name = name.strip() if name and name.strip() else "Candidate"
            safe_email = email.strip() if email and email.strip() else f"candidate_{int(datetime.utcnow().timestamp())}@cpip.local"
            safe_location = location.strip().lower() if location and location.strip() else "not specified"
            safe_role = target_role.strip() if target_role and target_role.strip() else "Not specified"

            student = StudentModel(
                name=safe_name,
                email=safe_email,
                location=safe_location,
                target_role=safe_role,
                skills=json.dumps([]),
                degree="Not specified",
                cgpa=0,
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"✅ New student: name={student.name} role={student.target_role} location={student.location}")
        else:
            if name and name.strip():
                student.name = name.strip()
            if location and location.strip():
                student.location = location.strip().lower()
            if target_role and target_role.strip():
                student.target_role = target_role.strip()
            student.updated_at = datetime.utcnow()
            db.commit()
            print(f"✅ Updated: name={student.name} role={student.target_role} location={student.location}")

        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{student.id}_{file.filename}")
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        print(f"✅ File saved: {file_path}")

        # Create resume record
        resume = ResumeModel(
            student_id=student.id,
            file_name=file.filename,
            file_path=file_path,
            extraction_status="pending",
            uploaded_at=datetime.utcnow()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        # Extract now: deterministic matching is fast, so the dashboard
        # opens with real data instead of an empty profile.
        try:
            parsed = _extract_and_save(db, resume, student, contents)
        except UnsupportedFileTypeError as e:
            return JSONResponse(status_code=400, content={"detail": str(e)})
        except Exception as e:
            db.rollback()
            resume.extraction_status = "failed"
            resume.extraction_error = str(e)
            db.commit()
            return JSONResponse(status_code=400, content={"detail": f"Could not read resume: {e}"})

        # Record the evaluation in the audit trail (never blocks the upload)
        try:
            from app.services.orchestrator import run_full_pipeline
            run_full_pipeline(student.id, event_type="ResumeUploaded")
        except Exception as e:
            print(f"Audit after upload failed: {e}")

        return {
            "success": True,
            "student_id": student.id,
            "resume_id": resume.id,
            "file_name": file.filename,
            "location_saved": student.location,
            "extraction_status": "completed",
            "detected_skills": parsed["skills"],
            "skill_source": "Matched against skills recruiters have posted in CPIP",
            "message": f"Resume uploaded for {student.name}. {len(parsed['skills'])} skill(s) detected."
        }

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        db.close()


@router.post("/resume/upload/{student_id}")
async def upload_resume_existing_student(
    student_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    location: str = Form(None),
    target_role: str = Form(None),
):
    """Upload updated resume for existing student."""
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})

        if not file.filename.lower().endswith('.pdf'):
            return JSONResponse(status_code=400, content={"detail": "Only PDF files allowed"})

        if location and location.strip():
            student.location = location.strip().lower()
        if target_role and target_role.strip():
            student.target_role = target_role.strip()
        student.updated_at = datetime.utcnow()

        file_path = os.path.join(UPLOAD_DIR, f"{student_id}_{file.filename}")
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)

        resume = ResumeModel(
            student_id=student_id,
            file_name=file.filename,
            file_path=file_path,
            extraction_status="pending",
            uploaded_at=datetime.utcnow()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        if background_tasks:
            background_tasks.add_task(process_resume_background, resume.id)

        return {
            "success": True,
            "resume_id": resume.id,
            "student_id": student_id,
            "file_name": file.filename,
            "extraction_status": "pending",
            "message": "Resume uploaded. Extracting skills..."
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
    finally:
        db.close()


@router.get("/resume/list/{student_id}")
def list_resumes(student_id: int):
    db = SessionLocal()
    try:
        resumes = db.query(ResumeModel).filter(
            ResumeModel.student_id == student_id
        ).order_by(ResumeModel.uploaded_at.desc()).all()
        return {
            "student_id": student_id,
            "total": len(resumes),
            "resumes": [
                {
                    "id": r.id,
                    "file_name": r.file_name,
                    "status": r.extraction_status,
                    "skills": json.loads(r.skills) if r.skills else [],
                    "is_selected": r.is_selected,
                    "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None
                }
                for r in resumes
            ]
        }
    finally:
        db.close()


@router.post("/resume/select/{student_id}/{resume_id}")
def select_resume(student_id: int, resume_id: int):
    db = SessionLocal()
    try:
        resume = db.query(ResumeModel).filter(
            ResumeModel.id == resume_id,
            ResumeModel.student_id == student_id
        ).first()
        if not resume:
            return JSONResponse(status_code=404, content={"detail": "Resume not found"})
        if resume.extraction_status != "completed":
            return JSONResponse(status_code=400, content={"detail": "Resume still processing"})

        db.query(ResumeModel).filter(
            ResumeModel.student_id == student_id
        ).update({"is_selected": False})
        resume.is_selected = True

        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if student and resume.skills:
            student.skills = resume.skills
            student.resume = resume.file_path
            student.updated_at = datetime.utcnow()

        db.commit()
        return {
            "success": True,
            "file_name": resume.file_name,
            "skills": json.loads(resume.skills) if resume.skills else []
        }
    finally:
        db.close()


@router.get("/resume/{resume_id}/status")
def get_status(resume_id: int):
    db = SessionLocal()
    try:
        resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not resume:
            return JSONResponse(status_code=404, content={"detail": "Resume not found"})
        return {
            "resume_id": resume_id,
            "status": resume.extraction_status,
            "file_name": resume.file_name,
            "skills_count": len(json.loads(resume.skills)) if resume.skills else 0,
            "error": resume.extraction_error
        }
    finally:
        db.close()