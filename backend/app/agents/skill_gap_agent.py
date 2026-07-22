"""
Skill Gap Agent
Compares candidate skills with job requirements and calculates skill gap score
"""

def skill_gap_agent(candidate_skills, required_skills, mandatory_skills=None):
    """
    Compares candidate skills with required skills for a role.
    
    Args:
        candidate_skills: List of skills student has (e.g., ["Python", "React"])
        required_skills: List of skills required for role (e.g., ["Python", "React", "SQL"])
        mandatory_skills: List of skills that MUST be present (subset of required_skills)
        
    Returns:
        Dictionary with gap analysis
    """
    
    if mandatory_skills is None:
        mandatory_skills = required_skills
    
    # Convert to sets for comparison
    candidate_set = set([s.lower() for s in candidate_skills])
    required_set = set([s.lower() for s in required_skills])
    mandatory_set = set([s.lower() for s in mandatory_skills])
    
    # Find matches and gaps
    matched_skills = list(candidate_set & required_set)
    missing_skills = list(required_set - candidate_set)
    missing_mandatory = list(mandatory_set - candidate_set)
    
    # Calculate gap score (0-100)
    if len(required_skills) == 0:
        gap_score = 100
    else:
        matched_count = len(matched_skills)
        gap_score = int((matched_count / len(required_skills)) * 100)
    
    # Determine readiness level
    if gap_score >= 80:
        readiness = "High - Ready to apply"
    elif gap_score >= 60:
        readiness = "Medium - Some preparation needed"
    elif gap_score >= 40:
        readiness = "Low - Significant preparation needed"
    else:
        readiness = "Very Low - Major skill development required"
    
    return {
        "gap_score": gap_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "missing_mandatory_skills": missing_mandatory,
        "total_required_skills": len(required_skills),
        "skills_matched": len(matched_skills),
        "readiness_level": readiness,
        "gap_analysis": f"{len(matched_skills)} of {len(required_skills)} required skills present"
    }


def validate_gap_result(result):
    """
    Validates that gap analysis result is complete.
    
    Args:
        result: The output from skill_gap_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "gap_score", "matched_skills", "missing_skills", 
        "readiness_level", "gap_analysis"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Gap analysis is valid and complete"
    }