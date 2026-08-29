"""
Resume Management - Production Version
Uses OCR + Groq LLM for skill extraction — no hardcoding
"""

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, ResumeModel
from datetime import datetime
import os
import json

router = APIRouter()

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_resume_background(resume_id: int):
    """
    Background task:
    1. Read PDF bytes
    2. Extract text via OCR
    3. Extract skills via Groq LLM
    4. Auto-populate market cache for student's role+location
    5. Save to DB
    """
    db = SessionLocal()
    try:
        resume = db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not resume:
            return

        print(f"🔄 Processing resume {resume_id}...")

        # Step 1: Read file
        if not resume.file_path or not os.path.exists(resume.file_path):
            resume.extraction_status = "failed"
            resume.extraction_error = f"File not found: {resume.file_path}"
            db.commit()
            return

        with open(resume.file_path, 'rb') as f:
            file_bytes = f.read()

        # Step 2: Extract text via OCR
        try:
            from app.services.resume_parser import extract_text
            text = extract_text(resume.file_name or 'resume.pdf', file_bytes)
            print(f"📄 Text extracted: {len(text)} chars")
        except Exception as e:
            print(f"❌ OCR failed: {e}")
            resume.extraction_status = "failed"
            resume.extraction_error = f"OCR failed: {str(e)}"
            db.commit()
            return

        if not text or len(text.strip()) < 10:
            resume.extraction_status = "failed"
            resume.extraction_error = "Could not extract text from PDF"
            db.commit()
            return

        # Step 3: Get student
        student = db.query(StudentModel).filter(
            StudentModel.id == resume.student_id
        ).first()
        target_role = student.target_role if student else "software engineer"

        # Step 4: Extract skills via Groq LLM
        try:
            from app.services.external_jobs_service import extract_skills_from_text
            skills = extract_skills_from_text(text, target_role=target_role)
            print(f"✅ Skills extracted by Groq: {skills}")
        except Exception as e:
            print(f"❌ Groq extraction failed: {e}")
            skills = []

        # Step 5: Deselect old resumes
        db.query(ResumeModel).filter(
            ResumeModel.student_id == resume.student_id,
            ResumeModel.id != resume.id
        ).update({"is_selected": False})

        resume.skills = json.dumps(skills)
        resume.extraction_status = "completed"
        resume.completed_at = datetime.utcnow()
        resume.is_selected = True

        # Update student skills
        if student:
            student.skills = json.dumps(skills)
            student.resume = resume.file_path
            student.updated_at = datetime.utcnow()

        db.commit()
        print(f"✅ Resume {resume_id} done! {len(skills)} skills saved.")

        # Step 6: Auto-populate market cache — INSIDE the function
        try:
            from app.services.market_skill_fetcher import populate_market_skills_for_location_and_role
            if student and student.target_role and student.location:
                print(f"🔄 Auto-populating market cache for {student.location}/{student.target_role}")
                populate_market_skills_for_location_and_role(
                    location=student.location,
                    target_role=student.target_role,
                    max_postings=30
                )
                print(f"✅ Market cache ready for {student.target_role} in {student.location}")
        except Exception as e:
            print(f"⚠️ Market cache population failed (non-critical): {e}")

    except Exception as e:
        print(f"❌ Error processing resume: {e}")
        try:
            resume.extraction_status = "failed"
            resume.extraction_error = str(e)
            db.commit()
        except:
            pass
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
        if not file.filename.endswith('.pdf'):
            return JSONResponse(status_code=400, content={"detail": "Only PDF files allowed"})

        # Find or create student
        student = None
        if email and email.strip():
            student = db.query(StudentModel).filter(
                StudentModel.email == email.strip()
            ).first()

        if not student:
            # Safety checks — never save wrong data
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
            # Only update fields that are actually provided
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

        if background_tasks:
            background_tasks.add_task(process_resume_background, resume.id)

        return {
            "success": True,
            "student_id": student.id,
            "resume_id": resume.id,
            "file_name": file.filename,
            "location_saved": student.location,
            "extraction_status": "pending",
            "message": f"Resume uploaded for {student.name}. Extracting skills via AI..."
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

        if not file.filename.endswith('.pdf'):
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
            "message": "Resume uploaded. Extracting skills via AI..."
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