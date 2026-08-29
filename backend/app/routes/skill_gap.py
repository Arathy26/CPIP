"""
Skill Gap Agent - Location-Aware with On-Demand Market Cache Population
No hardcoding — dynamically fetches market data from Adzuna via Groq
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, MarketSkillCacheModel
import json

router = APIRouter()


@router.get("/skill-gap/{student_id}")
def get_skill_gap(student_id: int, role: str = None):
    db = SessionLocal()
    try:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})

        target_role = role or student.target_role
        if not target_role:
            return JSONResponse(status_code=400, content={"detail": "No target role specified"})

        # Parse student skills
        student_skills = []
        if student.skills:
            try:
                student_skills = json.loads(student.skills) if isinstance(student.skills, str) else student.skills
            except:
                student_skills = [s.strip() for s in str(student.skills).split(",")]

        # Get student location
        student_location = (student.location or "india").lower().strip()
        location_map = {
            "bangalore": "bangalore", "bengaluru": "bangalore",
            "delhi": "delhi", "new delhi": "delhi",
            "mumbai": "mumbai", "bombay": "mumbai",
            "hyderabad": "hyderabad", "pune": "pune",
            "kochi": "kochi", "cochin": "kochi",
            "remote": "india", "not specified": "india",
        }
        normalized_location = location_map.get(student_location, student_location)

        def fetch_market_skills(location, role_name):
            """Fetch market skills from cache for given location and role"""
            skills = db.query(MarketSkillCacheModel).filter(
                MarketSkillCacheModel.target_role == role_name.lower().strip(),
                MarketSkillCacheModel.location == location
            ).all()
            return skills

        # Try location-specific market skills
        market_skills = fetch_market_skills(normalized_location, target_role)

        # Fallback to india-wide
        if not market_skills and normalized_location != "india":
            print(f"No cache for {normalized_location}, trying india...")
            market_skills = fetch_market_skills("india", target_role)

        # Fallback to any location
        if not market_skills:
            market_skills = db.query(MarketSkillCacheModel).filter(
                MarketSkillCacheModel.target_role == target_role.lower().strip()
            ).all()

        # ── ON-DEMAND POPULATE if still empty ──────────────────────
        if not market_skills:
            print(f"🔄 On-demand market cache populate for {normalized_location}/{target_role}")
            try:
                from app.services.market_skill_fetcher import populate_market_skills_for_location_and_role
                populate_market_skills_for_location_and_role(
                    location=normalized_location,
                    target_role=target_role.lower().strip(),
                    max_postings=25
                )
                # Re-query after populate
                market_skills = fetch_market_skills(normalized_location, target_role)
                if not market_skills:
                    market_skills = fetch_market_skills("india", target_role)
                print(f"✅ On-demand populate done: {len(market_skills)} skills cached")
            except Exception as e:
                print(f"⚠️ On-demand populate failed: {e}")

        if not market_skills:
            return {
                "gap_analysis": {
                    "gap_score": 0,
                    "matched_skills": [],
                    "missing_skills": [],
                    "target_role": target_role,
                    "location": normalized_location,
                    "message": f"Could not fetch market data for '{target_role}' in '{normalized_location}'.",
                }
            }

        # Calculate gap
        matched = []
        missing_with_weight = []

        for market_skill in market_skills:
            skill_name = market_skill.skill_name
            demand_weight = market_skill.demand_weight

            has_skill = any(
                skill_name.lower() in s.lower() or s.lower() in skill_name.lower()
                for s in student_skills
            )

            if has_skill:
                matched.append(skill_name)
            else:
                missing_with_weight.append({
                    "skill": skill_name,
                    "demand_weight": demand_weight,
                    "jobs_requiring": market_skill.postings_requiring_it
                })

        missing_with_weight.sort(key=lambda x: x["demand_weight"], reverse=True)

        total = len(market_skills)
        gap_score = int((len(matched) / total * 100)) if total > 0 else 0

        return {
            "gap_analysis": {
                "gap_score": gap_score,
                "matched_skills": matched,
                "missing_skills": missing_with_weight,
                "target_role": target_role,
                "location": normalized_location,
                "total_market_skills": total,
                "matched_count": len(matched),
                "missing_count": len(missing_with_weight),
                "basedOnPostings": True
            }
        }
    finally:
        db.close()