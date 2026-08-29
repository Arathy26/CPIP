"""
Admin Routes for Location-Aware Market Data Management
"""

from fastapi import APIRouter
from app.services.market_skill_fetcher import (
    populate_market_skills_for_location_and_role,
    populate_all_locations_and_roles,
    get_cached_market_stats_by_location
)

router = APIRouter()


@router.post("/admin/populate-market-data")
def admin_populate_market_data(location: str = "india", role: str = None):
    """
    Admin endpoint: Populate market data for specific location + role
    
    Parameters:
    - location: "bangalore", "delhi", "mumbai", "hyderabad", "pune", "india"
    - role: "AI engineer", "Backend Developer", etc. (optional)
    
    If role not specified, populates all major roles for that location
    
    Usage:
    POST http://localhost:8000/api/admin/populate-market-data?location=bangalore&role=AI+engineer
    
    POST http://localhost:8000/api/admin/populate-market-data?location=bangalore
    (will populate all roles for bangalore)
    """
    
    if role:
        # Single location + role
        print(f"🚀 Populating: {location} / {role}")
        result = populate_market_skills_for_location_and_role(
            location=location,
            target_role=role,
            max_postings=50
        )
        return {
            "status": "success" if result["success"] else "failed",
            "result": result
        }
    else:
        # All roles for specific location
        locations = [location]
        target_roles = [
            "AI engineer",
            "Backend Developer",
            "Frontend Developer",
            "Full Stack Developer",
            "Data Scientist",
            "DevOps Engineer",
        ]
        
        print(f"🚀 Populating {len(target_roles)} roles for {location}")
        
        results = []
        for role in target_roles:
            result = populate_market_skills_for_location_and_role(
                location=location,
                target_role=role,
                max_postings=50
            )
            results.append(result)
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "status": "success",
            "location": location,
            "total_roles": len(target_roles),
            "successful": successful,
            "results": results
        }


@router.post("/admin/populate-market-data/all")
def admin_populate_all_locations_and_roles():
    """
    Admin endpoint: Populate ALL locations + ALL roles
    
    This is comprehensive but takes longer (~10-15 minutes)
    
    Usage:
    POST http://localhost:8000/api/admin/populate-market-data/all
    """
    print("🚀 Starting comprehensive market data population...")
    print("⏱️  This will take 10-15 minutes")
    
    result = populate_all_locations_and_roles()
    
    return {
        "status": "success",
        "message": "Market data population completed",
        "result": result
    }


@router.get("/admin/market-stats")
def admin_get_market_stats(location: str = None):
    """
    Admin endpoint: Check market cache status
    
    Parameters:
    - location: (optional) Show stats for specific location only
    
    Usage:
    GET http://localhost:8000/api/admin/market-stats
    (shows all locations)
    
    GET http://localhost:8000/api/admin/market-stats?location=bangalore
    (shows only bangalore)
    """
    get_cached_market_stats_by_location(location)
    
    return {
        "status": "success",
        "location_filter": location or "all"
    }


@router.get("/health/market-cache")
def health_check_market_cache(location: str = None):
    """
    Health check: Is market cache populated?
    
    Parameters:
    - location: (optional) Check specific location only
    
    Returns True if cache has data
    
    Usage:
    GET http://localhost:8000/api/health/market-cache
    
    GET http://localhost:8000/api/health/market-cache?location=bangalore
    """
    from app.data.database import SessionLocal, MarketSkillCacheModel
    
    db = SessionLocal()
    try:
        if location:
            count = db.query(MarketSkillCacheModel).filter(
                MarketSkillCacheModel.location == location.lower().strip()
            ).count()
        else:
            count = db.query(MarketSkillCacheModel).count()
        
        return {
            "cache_status": "ready" if count > 0 else "empty",
            "total_skills_cached": count,
            "needs_population": count == 0,
            "location_filter": location or "all"
        }
    finally:
        db.close()


@router.get("/market/skills/{location}/{role}")
def get_market_skills_for_location_role(location: str, role: str):
    """
    Get cached market skills for specific location + role
    
    Usage:
    GET http://localhost:8000/api/market/skills/bangalore/AI+engineer
    """
    from app.data.database import SessionLocal, MarketSkillCacheModel
    
    db = SessionLocal()
    try:
        skills = db.query(MarketSkillCacheModel).filter(
            MarketSkillCacheModel.location == location.lower().strip(),
            MarketSkillCacheModel.target_role == role.lower().strip()
        ).order_by(MarketSkillCacheModel.demand_weight.desc()).all()
        
        return {
            "location": location.lower().strip(),
            "role": role.lower().strip(),
            "total_skills": len(skills),
            "skills": [
                {
                    "name": s.skill_name,
                    "demand_weight": s.demand_weight,
                    "jobs_requiring": s.postings_requiring_it
                }
                for s in skills
            ]
        }
    finally:
        db.close()