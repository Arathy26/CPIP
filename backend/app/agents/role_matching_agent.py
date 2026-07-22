"""
Role Matching Agent
Recommends suitable job roles based on student profile and readiness scores
"""

def role_matching_agent(candidate_profile, readiness_scores):
    """
    Recommends suitable job roles based on candidate skills and readiness.
    
    Args:
        candidate_profile: Dictionary with candidate info
        {
            "candidate_id": 1,
            "skills": ["Python", "React", "SQL"],
            "target_role": "Full Stack Developer"
        }
        readiness_scores: Dictionary with scores from previous agents
        {
            "skill_gap_score": 75,
            "portfolio_score": 80,
            "resume_score": 85,
            "interview_readiness_score": 70
        }
        
    Returns:
        Dictionary with role recommendations
    """
    
    # Available roles with required skills
    AVAILABLE_ROLES = {
        "Junior Full Stack Developer": ["Python", "React", "SQL"],
        "Junior Backend Developer": ["Python", "SQL"],
        "Junior Frontend Developer": ["React", "JavaScript"],
        "AI Engineer": ["Python", "Machine Learning"],
        "Data Analyst": ["Python", "SQL"]
    }
    
    candidate_skills = set([s.lower() for s in candidate_profile.get("skills", [])])
    
    # Calculate skill matches for each role
    role_matches = []
    
    for role, required_skills in AVAILABLE_ROLES.items():
        required_set = set([s.lower() for s in required_skills])
        matched = candidate_skills & required_set
        match_percentage = (len(matched) / len(required_set)) * 100 if required_set else 0
        
        # Calculate overall fit score (average of all readiness scores)
        avg_readiness = (
            readiness_scores.get("skill_gap_score", 0) +
            readiness_scores.get("portfolio_score", 0) +
            readiness_scores.get("resume_score", 0) +
            readiness_scores.get("interview_readiness_score", 0)
        ) / 4
        
        # Combine skill match with readiness
        fit_score = int((match_percentage + avg_readiness) / 2)
        
        # Determine suitability
        if fit_score >= 80:
            suitability = "Strong Fit"
        elif fit_score >= 60:
            suitability = "Good Fit"
        elif fit_score >= 40:
            suitability = "Stretch Fit"
        else:
            suitability = "Not Suitable Yet"
        
        role_matches.append({
            "role": role,
            "fit_score": fit_score,
            "suitability": suitability,
            "required_skills": required_skills,
            "matched_skills": list(matched)
        })
    
    # Sort by fit score
    role_matches.sort(key=lambda x: x["fit_score"], reverse=True)
    
    # Get top 3 recommendations
    top_recommendations = role_matches[:3]
    
    return {
        "candidate_id": candidate_profile.get("candidate_id"),
        "target_career_goal": candidate_profile.get("target_role"),
        "recommended_roles": top_recommendations,
        "all_matches": role_matches,
        "recommendation_summary": f"Top recommendation: {top_recommendations[0]['role']} (Fit Score: {top_recommendations[0]['fit_score']})"
    }


def validate_role_match_result(result):
    """
    Validates that role matching result is complete.
    
    Args:
        result: The output from role_matching_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "candidate_id", "recommended_roles", "recommendation_summary"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Role matching analysis is valid and complete"
    }