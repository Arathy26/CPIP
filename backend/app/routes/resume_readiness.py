"""
Resume Readiness Routes
API endpoints for resume readiness evaluation
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.agents.resume_readiness_agent import resume_readiness_agent, validate_resume_result
from app.services.resume_parser import parse_resume, UnsupportedFileTypeError, extract_text
from app.data import seed_data
import json
import os
from groq import Groq

router = APIRouter()


def extract_skills_with_llm(raw_text: str):
    """
    Use Groq LLM to extract skills, github, linkedin from resume.
    Temperature=0 prevents hallucination.
    Verification step ensures only real skills returned.
    """
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""You are a strict resume parser.

RULES:
1. Extract ONLY skills explicitly written in the resume text below
2. Do NOT infer, guess or add any skill not present
3. Include: programming languages, frameworks, tools, libraries, platforms, AI/ML tools
4. Extract github URL and linkedin URL if present

Resume text:
{raw_text}

Return ONLY this exact JSON format, nothing else, no markdown:
{{
    "skills": ["skill1", "skill2"],
    "github_url": "url or null",
    "linkedin_url": "url or null"
}}"""
            }]
        )

        result = json.loads(response.choices[0].message.content)
        llm_skills = result.get("skills", [])
        github_url = result.get("github_url")
        linkedin_url = result.get("linkedin_url")

        # Anti-hallucination: verify each skill exists in raw text
        verified_skills = [
            skill for skill in llm_skills
            if skill.lower() in raw_text.lower()
        ]

        return verified_skills, github_url, linkedin_url

    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return [], None, None


@router.get("/resume-readiness/{student_id}")
def get_resume_readiness(student_id: int):
    student = seed_data.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    resume_data = seed_data.get_resume(student_id)
    if resume_data is None:
        return {
            "student_id": student_id,
            "supported": False,
            "resume_analysis": None,
            "message": "No resume on file. Upload via POST /resume/upload.",
        }

    role_data = seed_data.get_role_requirements(student["target_role"])
    required_skills = role_data["required_skills"] if role_data else None
    resume_result = resume_readiness_agent(resume_data, required_skills=required_skills)
    validation = validate_resume_result(resume_result)

    return {
        "student_id": student_id,
        "supported": True,
        "resume_analysis": resume_result,
        "validation": validation,
        "message": "Resume readiness analysis completed successfully",
    }


@router.get("/resume-readiness")
def list_all_resume_readiness():
    results = []
    for student in seed_data.get_all_students():
        resume_data = seed_data.get_resume(student["id"])
        if resume_data is None:
            continue

        role_data = seed_data.get_role_requirements(student["target_role"])
        required_skills = role_data["required_skills"] if role_data else None
        resume_result = resume_readiness_agent(resume_data, required_skills=required_skills)

        results.append({
            "student_id": student["id"],
            "resume_score": resume_result["resume_score"],
            "readiness_level": resume_result["readiness_level"],
            "sections_present": len(resume_result["sections_present"]),
            "sections_missing": len(resume_result["sections_missing"]),
        })

    return {
        "total_students": len(results),
        "resume_readiness": results,
        "message": "All resume readiness scores retrieved",
    }


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(None),
    name: str = Form(None),
):
    from app.services.resume_parser import OCRSetupError

    file_bytes = await file.read()

    # Step 1: Extract raw text from resume
    raw_text = extract_text(file.filename, file_bytes)

    if len(raw_text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Could not read text from file. Try a different file.",
        )

    # Step 2: LLM extracts skills + links from raw text
    extracted_skills, github_url, linkedin_url = extract_skills_with_llm(raw_text)

    # Step 3: Parse resume for other fields (education, contact, projects)
    try:
        resume_data = parse_resume(
            filename=file.filename,
            file_bytes=file_bytes,
            target_role=target_role or "",
            known_skill_names=extracted_skills,
        )
    except UnsupportedFileTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OCRSetupError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Step 4: Override skills with LLM verified skills
    resume_data["skills"] = extracted_skills

    final_name = name or resume_data.get("name") or "Candidate"

    # Step 5: Save student with all extracted data
    new_student = seed_data.add_student({
        "name": final_name,
        "target_role": target_role or "",
        "skills": extracted_skills,
        "degree": resume_data["education"] or "Not specified",
        "email": resume_data["contact"].get("email") or "",
        "resume": file.filename,
        "github_link": github_url or "",
        "linkedin_id": linkedin_url or "",
    })

    seed_data.add_resume(new_student["id"], resume_data)

    # Agent 1: Resume Score
    role_data = seed_data.get_role_requirements(target_role)
    required_skills = role_data["required_skills"] if role_data else None
    resume_result = resume_readiness_agent(resume_data, required_skills=required_skills)
    validation = validate_resume_result(resume_result)
    seed_data.update_readiness_scores(new_student["id"], {
        "resume_score": resume_result["resume_score"]
    })

    # Run full agent pipeline
    from app.services.orchestrator import run_full_pipeline
    pipeline_result = run_full_pipeline(new_student["id"])

    return {
        "student_id": new_student["id"],
        "student": new_student,
        "resume_analysis": resume_result,
        "validation": validation,
        "pipeline_scores": pipeline_result.get("scores", {}),
        "detected_skills": extracted_skills,
        "github_url": github_url,
        "linkedin_url": linkedin_url,
        "extracted_text_length": len(raw_text),
        "message": f"Resume processed. {len(extracted_skills)} skill(s) detected.",
    }