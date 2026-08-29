"""
Job Opportunity Routes - With Location+Role Job Caching
Cache strategy:
  1. Check DB for cached jobs for this location+role
  2. If found and fresh (< 24hrs) → return from DB
  3. If not found → call Adzuna → save to DB → return
"""

import logging
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field

from app.agents.job_opportunity_agent import (
    job_opportunity_agent,
    match_candidates_to_job,
    validate_job_match_result,
)
from app.agents.resume_readiness_agent import resume_readiness_agent
from app.data import seed_data
from app.data.database import SessionLocal
from app.services.external_jobs_service import (
    search_external_jobs,
    ExternalJobsConfigError,
    ExternalJobsRequestError,
)

logger = logging.getLogger(__name__)
router = APIRouter()

CACHE_TTL_HOURS = 24  # Jobs cache valid for 24 hours


# ── Job Cache helpers ──────────────────────────────────────────────

def get_cached_jobs_for_location_role(location: str, role: str):
    """Check DB for cached jobs for this location+role combination"""
    try:
        from app.data.database import JobDescriptionCacheModel
        db = SessionLocal()
        cutoff = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)
        
        # Use job_description_cache with location+role as composite key
        cache_key = f"{location.lower().strip()}::{role.lower().strip()}"
        
        cached = db.query(JobDescriptionCacheModel).filter(
            JobDescriptionCacheModel.job_id == cache_key,
            JobDescriptionCacheModel.cached_at > cutoff
        ).first()
        
        db.close()
        
        if cached and cached.skills_extracted:
            import json
            jobs = json.loads(cached.skills_extracted)
            print(f"✅ Cache HIT: {len(jobs)} jobs for {location}/{role}")
            return jobs
        
        print(f"❌ Cache MISS: {location}/{role}")
        return None
    except Exception as e:
        print(f"⚠️ Cache read error: {e}")
        return None


def save_jobs_to_cache(location: str, role: str, jobs: list):
    """Save fetched jobs to DB cache"""
    try:
        from app.data.database import JobDescriptionCacheModel
        import json
        db = SessionLocal()
        
        cache_key = f"{location.lower().strip()}::{role.lower().strip()}"
        
        existing = db.query(JobDescriptionCacheModel).filter(
            JobDescriptionCacheModel.job_id == cache_key
        ).first()
        
        if existing:
            existing.skills_extracted = json.dumps(jobs)
            existing.cached_at = datetime.utcnow()
        else:
            new_cache = JobDescriptionCacheModel(
                job_id=cache_key,
                title=f"Jobs cache: {role} in {location}",
                company="cache",
                description=f"{location}::{role}",
                skills_extracted=json.dumps(jobs),
                cached_at=datetime.utcnow()
            )
            db.add(new_cache)
        
        db.commit()
        db.close()
        print(f"✅ Saved {len(jobs)} jobs to cache for {location}/{role}")
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")


# ── Helper functions ───────────────────────────────────────────────

def _build_profile_and_scores(student):
    profile = {
        "candidate_id": student["id"],
        "name": student["name"],
        "skills": student["skills"],
        "cgpa": student["cgpa"],
        "degree": student["degree"],
        "target_role": student.get("target_role"),
    }
    readiness_scores = seed_data.get_readiness_scores(student["id"])
    resume_data = seed_data.get_resume(student["id"])
    raw_resume_text = resume_data.get("raw_text", "") if resume_data else ""
    return profile, readiness_scores, raw_resume_text


def _enrich_with_resume_quality(matches, student_id):
    resume_data = seed_data.get_resume(student_id)
    if resume_data is None:
        return matches
    for match in matches:
        job_required_skills = match.get("required_skills", [])
        resume_check = resume_readiness_agent(resume_data, required_skills=job_required_skills)
        match["resume_score"] = resume_check["resume_score"]
        match["resume_keyword_match_percent"] = resume_check["keyword_match_percent"]
        match["resume_has_metrics"] = "Quantified Impact" in resume_check["sections_present"]
        match["resume_tips"] = resume_check.get("improvement_tips", [])
    return matches


def _calculate_fit_score(candidate, job, readiness_scores):
    try:
        skill_gap_score = readiness_scores.get("skill_gap_score", 0)
        portfolio_score = readiness_scores.get("portfolio_score", 0)
        resume_score = readiness_scores.get("resume_score", 0)
        interview_score = readiness_scores.get("interview_readiness_score", 0)

        candidate_skills = set(s.lower() for s in candidate.get("skills", []))
        job_required_skills = set(s.lower() for s in job.get("required_skills", []))
        job_preferred_skills = set(s.lower() for s in job.get("preferred_skills", []))

        required_match = len(candidate_skills & job_required_skills) / len(job_required_skills) if job_required_skills else 0.5
        preferred_match = len(candidate_skills & job_preferred_skills) / len(job_preferred_skills) if job_preferred_skills else 0.5

        fit_score = int(
            (required_match * 35) +
            (skill_gap_score * 0.15) +
            (portfolio_score * 0.12) +
            (resume_score * 0.13) +
            (interview_score * 0.15) +
            (preferred_match * 10)
        )

        fit_score = min(100, max(0, fit_score))

        if fit_score >= 80:
            suitability = "Excellent Fit"
        elif fit_score >= 60:
            suitability = "Good Fit"
        elif fit_score >= 40:
            suitability = "Possible Fit"
        else:
            suitability = "Not Suitable Yet"

        return fit_score, suitability, required_match, preferred_match

    except Exception as e:
        logger.error(f"Error calculating fit score: {e}")
        return 0, "Error", 0, 0


# ── Main job match endpoint ────────────────────────────────────────

@router.get("/job-match/{student_id}")
def get_job_matches(student_id: int, location: str = None):
    try:
        candidate = seed_data.get_student(student_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

        profile, readiness_scores, resume_text = _build_profile_and_scores(candidate)
        target_role = candidate.get("target_role", "")

        # Determine search location
        search_location = location or candidate.get("location")
        if not search_location or search_location.lower() in ["not specified", "remote", ""]:
            return {
                "student_id": student_id,
                "job_match_analysis": {
                    "all_matches": [],
                    "suitable_jobs": [],
                    "recommendation_count": 0,
                    "recommendation_summary": "Please enter your preferred job location.",
                    "needs_location": True
                },
                "validation": {"valid": True, "message": "Location required"},
                "message": "Location required for job matching"
            }

        all_jobs = []

        # ── CACHE-FIRST JOB FETCHING ──────────────────────────────
        if target_role:
            cached_listings = get_cached_jobs_for_location_role(search_location, target_role)

            if cached_listings:
                # Use cached jobs — no API call needed
                external_listings = cached_listings
                print(f"📦 Using {len(external_listings)} cached jobs")
            else:
                # Call Adzuna API
                print(f"🌐 Fetching from Adzuna: {target_role} in {search_location}")
                try:
                    external_listings = search_external_jobs(
                        query=target_role,
                        location=search_location,
                        max_results=20
                    )
                    # Save raw listings to cache for next time
                    if external_listings:
                        save_jobs_to_cache(search_location, target_role, external_listings)
                except Exception as e:
                    logger.error(f"Adzuna fetch failed: {e}")
                    external_listings = []

            # Build job objects from listings
            for listing in external_listings:
                cached_desc = seed_data.get_cached_job_description(
                    listing.get("job_id")
                ) if listing.get("job_id") else None
                required_skills = cached_desc["skills_extracted"] if cached_desc else []

                all_jobs.append({
                    "id": listing.get("job_id", ""),
                    "job_title": listing.get("title", ""),
                    "company_name": listing.get("company", "Unknown"),
                    "location": listing.get("location", search_location),
                    "required_skills": required_skills,
                    "preferred_skills": [],
                    "min_cgpa": 0,
                    "min_readiness": 0,
                    "apply_link": listing.get("apply_link", ""),
                    "source": listing.get("source", "external"),
                    "is_remote": listing.get("is_remote", False),
                    "employment_type": listing.get("employment_type", "Full-time"),
                })

        # Add internal DB jobs
        internal_jobs = seed_data.get_all_jobs() or []
        try:
            from app.services.semantic_skill_matcher import get_matcher
            matcher = get_matcher()
            for job in internal_jobs:
                job_title = job.get("job_title", "")
                if matcher and matcher.model:
                    similarity = matcher.semantic_match(target_role.lower(), job_title.lower())
                    if similarity >= 0.4:
                        all_jobs.append(job)
                else:
                    target_words = set(target_role.lower().split())
                    title_words = set(job_title.lower().split())
                    if target_words & title_words:
                        all_jobs.append(job)
        except Exception as e:
            logger.error(f"Internal job matching failed: {e}")
            all_jobs.extend(internal_jobs)

        # Calculate fit scores
        matches = []
        for job in all_jobs:
            fit_score, suitability, req_match, pref_match = _calculate_fit_score(
                candidate, job, readiness_scores
            )

            eligible = True
            eligibility_notes = []

            if candidate.get("cgpa", 0) < job.get("min_cgpa", 0):
                eligible = False
                eligibility_notes.append("CGPA too low")

            overall_readiness = int((
                readiness_scores.get("skill_gap_score", 0) +
                readiness_scores.get("portfolio_score", 0) +
                readiness_scores.get("resume_score", 0) +
                readiness_scores.get("interview_readiness_score", 0)
            ) / 4)

            if overall_readiness < job.get("min_readiness", 0):
                eligible = False
                eligibility_notes.append("Readiness too low")

            if fit_score >= 30:
                matches.append({
                    "job_id": job.get("id"),
                    "job_title": job.get("job_title", ""),
                    "company_name": job.get("company_name", "Unknown"),
                    "location": job.get("location", search_location),
                    "apply_link": job.get("apply_link", ""),
                    "source": job.get("source", "external"),
                    "is_remote": job.get("is_remote", False),
                    "employment_type": job.get("employment_type", "Full-time"),
                    "fit_score": fit_score,
                    "suitability": suitability,
                    "eligible": eligible,
                    "eligibility_notes": eligibility_notes,
                    "required_skills": job.get("required_skills", []),
                    "preferred_skills": job.get("preferred_skills", []),
                    "skill_coverage": {
                        "required_percent": int(req_match * 100),
                        "preferred_percent": int(pref_match * 100),
                    },
                    "agent_scores": {
                        "skill_gap": readiness_scores.get("skill_gap_score", 0),
                        "portfolio": readiness_scores.get("portfolio_score", 0),
                        "resume": readiness_scores.get("resume_score", 0),
                        "interview": readiness_scores.get("interview_readiness_score", 0),
                    }
                })

        matches = _enrich_with_resume_quality(matches, student_id)
        matches.sort(key=lambda x: x["fit_score"], reverse=True)
        suitable_jobs = [m for m in matches if m["eligible"]][:5]

        return {
            "student_id": student_id,
            "job_match_analysis": {
                "candidate_id": student_id,
                "all_matches": matches,
                "suitable_jobs": suitable_jobs,
                "recommendation_count": len(suitable_jobs),
                "location_searched": search_location,
                "recommendation_summary": (
                    f"Found {len(suitable_jobs)} suitable job(s) in {search_location}"
                    if suitable_jobs else
                    "No suitable jobs found. Recommend skill improvement."
                ),
            },
            "validation": {"valid": True, "message": "Job matching completed successfully"},
            "message": "Job matching completed successfully"
        }

    except Exception as e:
        logger.error(f"Error in job matching: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Job matching error: {str(e)}")


@router.get("/job-match")
def list_all_job_matches():
    try:
        results = []
        for student in seed_data.get_all_students():
            student_id = student["id"]
            match_data = get_job_matches(student_id)
            results.append({
                "student_id": student_id,
                "target_role": student.get("target_role"),
                "suitable_jobs_count": len(match_data["job_match_analysis"]["suitable_jobs"]),
            })
        return {"total_students": len(results), "job_matches": results, "message": "All job matches retrieved"}
    except Exception as e:
        logger.error(f"Error retrieving all job matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class JobPostRequest(BaseModel):
    job_title: str
    company_name: str = "Unknown"
    location: str = "Remote"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    min_cgpa: Optional[float] = 0
    min_readiness: Optional[int] = 0
    experience_level: Optional[str] = None


@router.post("/jobs")
def post_job(job: JobPostRequest):
    new_job = seed_data.add_job(job.model_dump())
    return {"job": new_job, "message": f"Job '{new_job['job_title']}' posted successfully."}


@router.get("/jobs")
def list_jobs(query: str = None):
    jobs = seed_data.get_all_jobs()
    if query:
        jobs = seed_data.search_jobs(jobs, query)
    return {"jobs": jobs}


@router.get("/jobs/external/search")
def search_jobs_external(query: str, student_id: int = None, country: str = "in"):
    try:
        results = search_external_jobs(query, location="India")
    except ExternalJobsConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ExternalJobsRequestError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if student_id is not None:
        student = seed_data.get_student(student_id)
        if student is not None:
            candidate_skills = set(s.lower() for s in student.get("skills", []))
            for job in results:
                required = set(t.lower() for t in job.get("required_technologies", []))
                matched = candidate_skills & required
                job["skills_matched"] = list(matched)
                job["skill_overlap_percent"] = (
                    int((len(matched) / len(required)) * 100) if required else None
                )

    return {"query": query, "total_results": len(results), "jobs": results, "message": "External listings via Adzuna"}


@router.get("/jobs/{job_id}/matches")
def get_job_candidate_matches(job_id: int):
    job = seed_data.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"job_id": job_id, "job_title": job["job_title"], "message": "Candidate matching coming soon"}


@router.get("/notifications/{student_id}")
def get_student_notifications(student_id: int):
    student = seed_data.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return {"student_id": student_id, "notifications": [], "unread_count": 0}


@router.post("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: int):
    notification = seed_data.mark_notification_read(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"notification": notification, "message": "Marked as read"}