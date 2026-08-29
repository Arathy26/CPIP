"""
Training Recommendation Agent - CLEANED (No Hardcoding)
Recommends training based on MARKET DEMAND (not hardcoded training plans)
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, MarketSkillCacheModel
import json

router = APIRouter()

@router.get("/training-plan/{student_id}")
def get_training_plan(student_id: int, role: str = None):
    """
    Generate training plan based on MARKET DATA (not hardcoded plans)
    
    Flow:
    1. Get student skills and target role
    2. Fetch market skills with demand weights
    3. Find missing skills (not hardcoded)
    4. Sort by demand weight (market-driven)
    5. Create learning path for top 5
    """
    db = SessionLocal()
    try:
        # Get student
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})
        
        # Get target role
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
        
        # Get market skills from database (market_skill_fetcher populates this)
        market_skills = db.query(MarketSkillCacheModel).filter(
            MarketSkillCacheModel.target_role == target_role
        ).all()
        
        if not market_skills:
            return {
                "training_plan": {
                    "priority_actions": [],
                    "message": f"No market data yet for {target_role}. Run market fetcher first."
                }
            }
        
        # Find missing skills
        missing_skills = []
        
        for market_skill in market_skills:
            skill_name = market_skill.skill_name
            demand_weight = market_skill.demand_weight
            postings = market_skill.postings_requiring_it
            
            has_skill = any(
                skill_name.lower() in s.lower() or s.lower() in skill_name.lower() 
                for s in student_skills
            )
            
            if not has_skill:
                missing_skills.append({
                    "skill": skill_name,
                    "demand_weight": demand_weight,
                    "jobs_count": postings
                })
        
        # Sort by demand weight (market-driven, not hardcoded)
        missing_skills.sort(key=lambda x: x["demand_weight"], reverse=True)
        
        # Top 5 priority skills
        top_5 = missing_skills[:5]
        
        # Generate training actions (dynamic, not hardcoded)
        training_actions = []
        
        for idx, item in enumerate(top_5, 1):
            skill = item["skill"]
            demand = item["demand_weight"]
            jobs_count = item["jobs_count"]
            
            # Estimate duration based on complexity (can be ML model later)
            # For now, use demand to estimate: higher demand = more foundational = longer
            if demand > 80:
                duration_weeks = 4
                urgency = "urgent"
            elif demand > 60:
                duration_weeks = 3
                urgency = "high"
            else:
                duration_weeks = 2
                urgency = "medium"
            
            training_actions.append({
                "rank": idx,
                "skill": skill,
                "demand_weight": demand,
                "jobs_requiring": jobs_count,
                "estimated_weeks": duration_weeks,
                "urgency": urgency,
                "reason": f"{demand}% of {target_role} jobs require this skill"
            })
        
        return {
            "training_plan": {
                "target_role": target_role,
                "priority_actions": training_actions,
                "total_missing": len(missing_skills),
                "top_5_count": len(top_5)
            }
        }
    finally:
        db.close()