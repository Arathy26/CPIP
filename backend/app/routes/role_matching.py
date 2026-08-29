"""
Role Matching Agent - CLEANED (No Hardcoding)
Matches student to suitable roles based on MARKET DATA
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.data.database import SessionLocal, StudentModel, MarketSkillCacheModel
import json

router = APIRouter()

@router.get("/role-match/{student_id}")
def get_role_match(student_id: int):
    """
    Recommend suitable roles based on student skills vs MARKET DATA (not hardcoded)
    
    Flow:
    1. Get student skills
    2. Query all available role data in market cache
    3. Calculate fit score for each role
    4. Sort by fit score
    5. Return top 3-5 roles
    """
    db = SessionLocal()
    try:
        # Get student
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
        if not student:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})
        
        # Parse student skills
        student_skills = []
        if student.skills:
            try:
                student_skills = json.loads(student.skills) if isinstance(student.skills, str) else student.skills
            except:
                student_skills = [s.strip() for s in str(student.skills).split(",")]
        
        # Get all unique roles from market data
        role_data = db.query(MarketSkillCacheModel.target_role).distinct().all()
        
        if not role_data:
            return {
                "role_matches": [],
                "message": "No market data yet. Run market fetcher first."
            }
        
        # Calculate fit for each role
        role_fits = []
        
        for (role,) in role_data:
            if not role:
                continue
            
            # Get market skills for this role
            market_skills = db.query(MarketSkillCacheModel).filter(
                MarketSkillCacheModel.target_role == role
            ).all()
            
            if not market_skills:
                continue
            
            # Calculate match score
            matched_count = 0
            total_weight = 0
            
            for market_skill in market_skills:
                skill_name = market_skill.skill_name
                demand_weight = market_skill.demand_weight
                
                has_skill = any(
                    skill_name.lower() in s.lower() or s.lower() in skill_name.lower() 
                    for s in student_skills
                )
                
                if has_skill:
                    matched_count += demand_weight
                
                total_weight += demand_weight
            
            # Calculate fit score (0-100)
            fit_score = int((matched_count / total_weight * 100)) if total_weight > 0 else 0
            
            role_fits.append({
                "role": role,
                "fit_score": fit_score,
                "matched_skills_weight": matched_count,
                "total_market_weight": total_weight
            })
        
        # Sort by fit score (highest first)
        role_fits.sort(key=lambda x: x["fit_score"], reverse=True)
        
        # Top 5 roles
        top_roles = role_fits[:5]
        
        return {
            "role_matches": top_roles,
            "student_id": student_id,
            "total_roles_analyzed": len(role_fits)
        }
    finally:
        db.close()