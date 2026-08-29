"""
Smart Job Fetcher - PRODUCTION FIX
With comprehensive error handling, fallbacks, and debug logging
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SmartJobFetcher:
    """Intelligent job fetcher with multi-layer caching and fallbacks"""
    
    def fetch_jobs_for_student(
        self,
        student_id: int,
        target_role: str,
        resume_skills: List[str],
        resume_text: str = ""
    ) -> Dict[str, Any]:
        """
        Main entry point with FULL ERROR HANDLING AND FALLBACKS
        """
        
        print(f"\n{'='*70}")
        print(f"🔧 [SmartJobFetcher] STARTING JOB FETCH")
        print(f"{'='*70}")
        print(f"  📋 student_id: {student_id}")
        print(f"  🎯 target_role: '{target_role}'")
        print(f"  💼 resume_skills: {resume_skills}")
        print(f"{'='*70}\n")
        
        try:
            from app.data import seed_data
            from app.services.semantic_query_builder import (
                normalize_role,
                build_semantic_query
            )
            from app.services.external_jobs_service import (
                search_external_jobs,
                ExternalJobsConfigError,
                ExternalJobsRequestError,
            )
            
            # ==========================================
            # STEP 1: VALIDATE INPUT
            # ==========================================
            if not target_role or target_role.strip() == "":
                print(f"⚠️  WARNING: target_role is empty!")
                print(f"    Using fallback: 'Developer'")
                target_role = "Developer"
            
            if not resume_skills:
                print(f"⚠️  WARNING: resume_skills is empty!")
                resume_skills = []
            
            # ==========================================
            # STEP 2: NORMALIZE ROLE
            # ==========================================
            print(f"📝 Step 1: Normalize role")
            try:
                normalized_role = normalize_role(target_role)
                print(f"   ✅ Normalized: '{target_role}' → '{normalized_role}'")
            except Exception as e:
                print(f"   ❌ Normalization failed: {e}")
                normalized_role = target_role.lower().replace(' ', '_')
                print(f"   🔄 Fallback normalized: '{normalized_role}'")
            
            # ==========================================
            # STEP 3: CHECK CACHE
            # ==========================================
            print(f"\n🔍 Step 2: Check cache for '{normalized_role}'")
            try:
                cached_jobs = seed_data.get_cached_jobs_for_role(normalized_role)
                
                if cached_jobs and len(cached_jobs) > 0:
                    print(f"   ✅ CACHE HIT! Found {len(cached_jobs)} cached jobs")
                    
                    # Attach cached skills
                    for job in cached_jobs:
                        job_id = job.get("job_id")
                        if job_id:
                            try:
                                cached_skills = seed_data.get_cached_job_skills(job_id)
                                job["extracted_skills"] = cached_skills if cached_skills else []
                            except:
                                job["extracted_skills"] = []
                    
                    print(f"\n{'='*70}")
                    print(f"✅ SUCCESS: Using cached jobs (instant response)")
                    print(f"{'='*70}\n")
                    
                    return {
                        "jobs": cached_jobs,
                        "source": "cache",
                        "cache_hit": True,
                        "total_jobs": len(cached_jobs),
                        "normalized_role": normalized_role,
                        "metadata": {
                            "message": "Jobs retrieved from cache (no API call)",
                            "cache_benefit": "Saved API call and LLM extraction"
                        }
                    }
                else:
                    print(f"   ❌ CACHE MISS: No cached jobs found")
            
            except Exception as e:
                print(f"   ⚠️  Cache check failed: {e}")
            
            # ==========================================
            # STEP 4: BUILD SEMANTIC QUERY
            # ==========================================
            print(f"\n📋 Step 3: Build semantic query")
            try:
                semantic_query = build_semantic_query(
                    target_role=target_role,
                    resume_skills=resume_skills,
                    resume_text=resume_text
                )
                print(f"   ✅ Query built: '{semantic_query}'")
            except Exception as e:
                print(f"   ⚠️  Query builder failed: {e}")
                semantic_query = target_role
                print(f"   🔄 Fallback query: '{semantic_query}'")
            
            # ==========================================
            # STEP 5: FETCH FROM EXTERNAL API
            # ==========================================
            print(f"\n🌐 Step 4: Fetch from Active Jobs DB API")
            api_jobs = []
            api_error = None
            
            try:
                print(f"   📡 Calling API with query: '{semantic_query}'")
                api_jobs = search_external_jobs(
                    query=semantic_query,
                    location="India",
                    max_results=20
                )
                print(f"   ✅ API Success! Returned {len(api_jobs)} jobs")
            
            except ExternalJobsConfigError as e:
                print(f"   ❌ CONFIG ERROR: {e}")
                api_error = f"Configuration error: {str(e)}"
            
            except ExternalJobsRequestError as e:
                print(f"   ❌ API REQUEST ERROR: {e}")
                api_error = f"API request failed: {str(e)}"
            
            except Exception as e:
                print(f"   ❌ UNEXPECTED ERROR: {e}")
                api_error = f"Unexpected error: {str(e)}"
            
            # ==========================================
            # STEP 6: HANDLE NO RESULTS - FALLBACK 1
            # ==========================================
            if not api_jobs or len(api_jobs) == 0:
                print(f"\n⚠️  WARNING: API returned 0 jobs")
                
                if api_error:
                    print(f"   Error was: {api_error}")
                
                print(f"\n   🔄 Trying FALLBACK 1: Generic search")
                
                try:
                    print(f"   📡 Searching for: '{target_role}'")
                    api_jobs = search_external_jobs(
                        query=target_role,
                        location="India",
                        max_results=15
                    )
                    print(f"   ✅ Fallback 1 succeeded! Got {len(api_jobs)} jobs")
                except Exception as e2:
                    print(f"   ❌ Fallback 1 failed: {e2}")
                    api_jobs = []
            
            # ==========================================
            # STEP 7: FALLBACK 2 - USE SEED DATA
            # ==========================================
            if not api_jobs or len(api_jobs) == 0:
                print(f"\n   🔄 Trying FALLBACK 2: Internal seed data")
                try:
                    internal_jobs = seed_data.get_all_jobs() or []
                    if internal_jobs:
                        api_jobs = [
                            {
                                "job_id": str(j.get("id", "")),
                                "job_title": j.get("job_title", ""),
                                "company": j.get("company_name", ""),
                                "location": j.get("location", ""),
                                "description": "",
                                "apply_link": "",
                                "employment_type": "",
                                "extracted_skills": j.get("required_skills", [])
                            }
                            for j in internal_jobs[:10]
                        ]
                        print(f"   ✅ Fallback 2 succeeded! Got {len(api_jobs)} internal jobs")
                except Exception as e3:
                    print(f"   ❌ Fallback 2 failed: {e3}")
                    api_jobs = []
            
            # ==========================================
            # STEP 8: EXTRACT SKILLS & CACHE
            # ==========================================
            if api_jobs and len(api_jobs) > 0:
                print(f"\n🧠 Step 5: Extract skills and cache")
                
                from app.services.external_jobs_service import extract_skills_from_text
                
                jobs_with_skills = []
                for idx, job in enumerate(api_jobs, 1):
                    try:
                        job_id = job.get("job_id")
                        description = job.get("description", "")
                        title = job.get("job_title", "")
                        
                        # Extract skills
                        skills = extract_skills_from_text(f"{title} {description}")
                        
                        # Cache job
                        try:
                            seed_data.cache_job_for_role(
                                role_normalized=normalized_role,
                                job_data=job
                            )
                        except Exception as cache_err:
                            print(f"      ⚠️  Cache job failed for {title}: {cache_err}")
                        
                        # Cache skills
                        if job_id and skills:
                            try:
                                seed_data.cache_job_skills(job_id, skills)
                            except Exception as skill_err:
                                print(f"      ⚠️  Cache skills failed: {skill_err}")
                        
                        job["extracted_skills"] = skills
                        jobs_with_skills.append(job)
                        
                    except Exception as e:
                        print(f"      ⚠️  Processing job {idx} failed: {e}")
                        job["extracted_skills"] = []
                        jobs_with_skills.append(job)
                
                print(f"   ✅ Processed {len(jobs_with_skills)} jobs")
                
                print(f"\n{'='*70}")
                print(f"✅ SUCCESS: Fetched {len(jobs_with_skills)} jobs")
                print(f"{'='*70}\n")
                
                return {
                    "jobs": jobs_with_skills,
                    "source": "api",
                    "cache_hit": False,
                    "total_jobs": len(api_jobs),
                    "normalized_role": normalized_role,
                    "semantic_query": semantic_query,
                    "metadata": {
                        "message": "Jobs fetched from API and cached for future use",
                        "next_student_benefit": "Instant cache hit, no API call"
                    }
                }
            
            # ==========================================
            # NO JOBS AT ALL - RETURN EMPTY
            # ==========================================
            print(f"\n❌ CRITICAL: NO JOBS FOUND FROM ANY SOURCE")
            print(f"{'='*70}\n")
            
            return {
                "jobs": [],
                "source": "none",
                "cache_hit": False,
                "total_jobs": 0,
                "error": api_error or "No jobs found from any source",
                "troubleshooting": {
                    "check_1": "Is RAPIDAPI_KEY set in .env?",
                    "check_2": "Is Active Jobs DB API quota exceeded?",
                    "check_3": "Is target_role empty or invalid?",
                    "suggestion": "Check backend logs for details"
                }
            }
        
        except Exception as e:
            print(f"\n❌ FATAL ERROR IN FETCHER: {e}")
            print(f"{'='*70}\n")
            
            logger.error(f"SmartJobFetcher fatal error: {e}", exc_info=True)
            
            return {
                "jobs": [],
                "error": str(e),
                "source": "error",
                "message": "An unexpected error occurred in job fetcher"
            }


# Singleton
_fetcher_instance = None

def get_smart_job_fetcher() -> SmartJobFetcher:
    """Get or create fetcher instance"""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = SmartJobFetcher()
    return _fetcher_instance