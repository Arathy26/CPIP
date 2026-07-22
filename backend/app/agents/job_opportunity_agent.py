"""
Job Opportunity Agent
Matches students to job openings based on skills and readiness
"""

def job_opportunity_agent(candidate_profile, readiness_scores):
    """
    Matches candidate to suitable job opportunities.
    
    Args:
        candidate_profile: Dictionary with candidate info
        {
            "candidate_id": 1,
            "skills": ["Python", "React", "SQL"],
            "cgpa": 7.5,
            "degree": "B.Tech",
            "current_readiness_score": 71
        }
        readiness_scores: Dictionary with readiness data
        {
            "skill_gap_score": 65,
            "portfolio_score": 50,
            "resume_score": 100,
            "interview_readiness_score": 70
        }
        
    Returns:
        Dictionary with job matches
    """
    
    # Available job opportunities
    JOB_OPPORTUNITIES = {
        "Junior Full Stack Developer": {
            "required_skills": ["Python", "React", "SQL"],
            "preferred_skills": ["Docker", "Git"],
            "min_cgpa": 6.5,
            "degree": "B.Tech",
            "min_readiness": 65
        },
        "Junior Backend Developer": {
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["FastAPI", "Docker"],
            "min_cgpa": 6.5,
            "degree": "B.Tech",
            "min_readiness": 70
        },
        "Junior Frontend Developer": {
            "required_skills": ["React", "JavaScript"],
            "preferred_skills": ["CSS", "TypeScript"],
            "min_cgpa": 6.0,
            "degree": "B.Tech",
            "min_readiness": 60
        },
        "Data Analyst Intern": {
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["Excel", "Tableau"],
            "min_cgpa": 6.5,
            "degree": "B.Tech",
            "min_readiness": 65
        }
    }
    
    candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
    candidate_cgpa = candidate_profile.get("cgpa", 0)
    candidate_readiness = readiness_scores.get("skill_gap_score", 0)
    
    matched_jobs = []
    
    for job_title, requirements in JOB_OPPORTUNITIES.items():
        # Check eligibility
        cgpa_eligible = candidate_cgpa >= requirements["min_cgpa"]
        readiness_eligible = candidate_readiness >= requirements["min_readiness"]
        
        # Calculate skill match
        required_set = set([s.lower() for s in requirements["required_skills"]])
        preferred_set = set([s.lower() for s in requirements["preferred_skills"]])
        
        required_matched = candidate_skills & required_set
        preferred_matched = candidate_skills & preferred_set
        
        # Calculate fit score
        required_percentage = (len(required_matched) / len(required_set)) * 100 if required_set else 0
        preferred_percentage = (len(preferred_matched) / len(preferred_set)) * 100 if preferred_set else 0
        
        fit_score = int((required_percentage * 0.7) + (preferred_percentage * 0.3))
        
        # Determine eligibility
        if cgpa_eligible and readiness_eligible:
            eligibility = "Eligible"
        elif cgpa_eligible or readiness_eligible:
            eligibility = "Conditionally Eligible"
        else:
            eligibility = "Not Eligible"
        
        # Determine suitability
        if fit_score >= 80 and eligibility == "Eligible":
            suitability = "Strong Fit"
        elif fit_score >= 60 and eligibility in ["Eligible", "Conditionally Eligible"]:
            suitability = "Good Fit"
        elif fit_score >= 40:
            suitability = "Stretch Fit"
        else:
            suitability = "Not Suitable"
        
        matched_jobs.append({
            "job_title": job_title,
            "fit_score": fit_score,
            "suitability": suitability,
            "eligibility": eligibility,
            "required_skills_matched": list(required_matched),
            "required_skills_missing": list(required_set - candidate_skills),
            "preferred_skills_missing": list(preferred_set - candidate_skills)
        })
    
    # Sort by fit score
    matched_jobs.sort(key=lambda x: x["fit_score"], reverse=True)
    
    # Get eligible and suitable jobs
    suitable_jobs = [j for j in matched_jobs if j["suitability"] in ["Strong Fit", "Good Fit"] and j["eligibility"] == "Eligible"]
    
    return {
        "candidate_id": candidate_profile.get("candidate_id"),
        "all_matches": matched_jobs,
        "suitable_jobs": suitable_jobs[:3],  # Top 3 recommendations
        "recommendation_count": len(suitable_jobs),
        "recommendation_summary": f"Found {len(suitable_jobs)} suitable job(s) for this candidate"
    }


def validate_job_match_result(result):
    """
    Validates job matching result.
    
    Args:
        result: The output from job_opportunity_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "candidate_id", "all_matches", "suitable_jobs"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Job matching analysis is valid and complete"
    }