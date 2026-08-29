"""
Market Skill Fetcher — Location-Aware Version
Populates MarketSkillCacheModel with location-specific skills

Flow:
1. User specifies: location + role
2. Fetch jobs for that location from Adzuna
3. Extract skills from location-specific jobs
4. Calculate demand_weight for that location
5. Store with location as cache key

Example:
- Bangalore AI engineers need: Python (95%), FastAPI (88%), Docker (72%)
- Mumbai AI engineers need: Python (92%), ML (85%), Kubernetes (65%)
- Different locations = different skill demands!
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.database import SessionLocal, MarketSkillCacheModel
from app.services.external_jobs_service import fetch_market_skill_frequency


def populate_market_skills_for_location_and_role(
    location: str, 
    target_role: str, 
    max_postings: int = 50
):
    """
    Fetch market data for specific LOCATION + ROLE combination
    
    Args:
        location: "bangalore", "delhi", "mumbai", "india" (all India)
        target_role: "AI engineer", "Backend Developer", etc.
        max_postings: How many jobs to analyze
    
    Returns:
        dict with success status, skills cached, etc.
    """
    location_normalized = location.lower().strip()
    role_normalized = target_role.lower().strip()
    
    print(f"\n{'='*70}")
    print(f"🔍 Fetching market data")
    print(f"   Location: {location_normalized}")
    print(f"   Role: {role_normalized}")
    print(f"   Max jobs: {max_postings}")
    print(f"{'='*70}")
    
    try:
        # Call external_jobs_service with location
        skill_frequency, total_postings = fetch_market_skill_frequency(
            target_role=target_role,
            location=location,  # Pass actual location to API
            max_postings=max_postings
        )
        
        if not skill_frequency:
            print(f"⚠️  No skills extracted for {location_normalized} / {role_normalized}")
            return {
                "success": False,
                "location": location_normalized,
                "role": role_normalized,
                "message": "No skills extracted"
            }
        
        print(f"\n✅ Extracted {len(skill_frequency)} unique skills from {total_postings} jobs")
        
        # Clear old cache for this location+role combo
        clear_cache_for_location_and_role(location_normalized, role_normalized)
        
        # Populate cache with demand weights
        db = SessionLocal()
        try:
            skills_added = 0
            
            for skill, frequency in sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True):
                # Calculate demand weight: (frequency / total_postings) * 100
                demand_weight = int((frequency / total_postings * 100)) if total_postings > 0 else 0
                
                # Create cache entry WITH location
                cache_entry = MarketSkillCacheModel(
                    location=location_normalized,
                    target_role=role_normalized,
                    skill_name=skill,
                    demand_weight=demand_weight,
                    postings_requiring_it=frequency,
                    cached_at=datetime.utcnow()
                )
                
                db.add(cache_entry)
                skills_added += 1
                
                # Print top skills
                if skills_added <= 10:
                    print(f"  {skill:30} → {demand_weight:3}% ({frequency}/{total_postings} jobs)")
            
            db.commit()
            
            print(f"\n✅ Cached {skills_added} skills for {location_normalized} / {role_normalized}")
            
            return {
                "success": True,
                "location": location_normalized,
                "role": role_normalized,
                "skills_cached": skills_added,
                "total_postings_analyzed": total_postings,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return {
                "success": False,
                "location": location_normalized,
                "role": role_normalized,
                "error": str(e)
            }
        finally:
            db.close()
    
    except Exception as e:
        print(f"❌ Error fetching market data: {e}")
        return {
            "success": False,
            "location": location_normalized,
            "role": role_normalized,
            "error": str(e)
        }


def clear_cache_for_location_and_role(location: str, target_role: str):
    """Clear old cache entries for specific location+role"""
    db = SessionLocal()
    try:
        deleted = db.query(MarketSkillCacheModel).filter(
            MarketSkillCacheModel.location == location.lower().strip(),
            MarketSkillCacheModel.target_role == target_role.lower().strip()
        ).delete()
        db.commit()
        if deleted > 0:
            print(f"🧹 Cleared {deleted} old cache entries")
    except Exception as e:
        print(f"⚠️  Error clearing cache: {e}")
        db.rollback()
    finally:
        db.close()


def populate_all_locations_and_roles():
    """
    Populate market data for all locations + all roles
    Takes longer but comprehensive!
    """
    
    locations = [
        "bangalore",
        "delhi",
        "mumbai",
        "hyderabad",
        "pune",
        "india"  # All India
    ]
    
    target_roles = [
        "AI engineer",
        "Backend Developer",
        "Frontend Developer",
        "Full Stack Developer",
        "Data Scientist",
        "DevOps Engineer",
    ]
    
    print("\n" + "="*70)
    print("MARKET SKILL FETCHER - Location-Aware")
    print("="*70)
    print(f"Locations: {len(locations)}")
    print(f"Roles: {len(target_roles)}")
    print(f"Total combinations: {len(locations) * len(target_roles)}")
    
    results = []
    
    for location in locations:
        print(f"\n📍 LOCATION: {location.upper()}")
        print("="*70)
        
        for role in target_roles:
            result = populate_market_skills_for_location_and_role(
                location=location,
                target_role=role,
                max_postings=50
            )
            results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    total_skills_cached = sum(r.get("skills_cached", 0) for r in results if r["success"])
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"✅ Total skills cached: {total_skills_cached}")
    print(f"⏰ Timestamp: {datetime.utcnow().isoformat()}")
    
    return {
        "total_combinations": len(results),
        "successful": successful,
        "total_skills_cached": total_skills_cached,
        "results": results
    }


def get_cached_market_stats_by_location(location: str = None):
    """Check what's in cache for a specific location (or all)"""
    db = SessionLocal()
    try:
        if location:
            location_normalized = location.lower().strip()
            entries = db.query(MarketSkillCacheModel).filter(
                MarketSkillCacheModel.location == location_normalized
            ).all()
            
            print(f"\n📍 LOCATION: {location_normalized}")
            print(f"   Total skills: {len(entries)}")
            
            roles = set(e.target_role for e in entries)
            for role in sorted(roles):
                count = sum(1 for e in entries if e.target_role == role)
                print(f"     {role}: {count} skills")
        else:
            # All locations
            total = db.query(MarketSkillCacheModel).count()
            locations_in_db = db.query(MarketSkillCacheModel.location).distinct().all()
            
            print(f"\n{'='*70}")
            print(f"CACHE STATUS - All Locations")
            print(f"{'='*70}")
            print(f"Total skills cached: {total}")
            print(f"Unique locations: {len(locations_in_db)}")
            
            for (loc,) in sorted(locations_in_db):
                count = db.query(MarketSkillCacheModel).filter(
                    MarketSkillCacheModel.location == loc
                ).count()
                print(f"\n📍 {loc}: {count} skills")
    
    finally:
        db.close()


if __name__ == "__main__":
    """
    Usage:
    
    python -m app.services.market_skill_fetcher_location_aware
    
    Or via API:
    POST /api/admin/populate-market-data?location=bangalore&role=AI+engineer
    """
    
    import time
    
    start = time.time()
    
    # Check current cache
    print("Checking current cache...")
    get_cached_market_stats_by_location()
    
 
    
    # Option 2: Populate all combinations (takes longer)
    result = populate_all_locations_and_roles()
    
    # Check cache again
    print("\n\nFinal cache status...")
    get_cached_market_stats_by_location()
    
    elapsed = time.time() - start
    print(f"\n⏱️  Total time: {elapsed:.1f} seconds")
    print("\n✅ Market skill fetcher complete!")