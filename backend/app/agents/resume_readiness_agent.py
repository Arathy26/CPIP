"""
Resume Readiness Agent
Evaluates whether a student's resume is complete and interview-ready
"""

def resume_readiness_agent(resume_data):
    """
    Evaluates student resume completeness and quality.
    
    Args:
        resume_data: Dictionary with resume information
        {
            "education": "B.Tech Computer Science",
            "skills": ["Python", "React", "SQL"],
            "projects": ["Project 1", "Project 2"],
            "contact": {"email": "...", "phone": "..."},
            "role_alignment": "Target role mentioned"
        }
        
    Returns:
        Dictionary with resume readiness score and gaps
    """
    
    # Initialize section checklist
    sections_present = []
    sections_missing = []
    
    # Check Education section
    if resume_data.get("education"):
        sections_present.append("Education")
    else:
        sections_missing.append("Education")
    
    # Check Skills section
    if resume_data.get("skills") and len(resume_data.get("skills", [])) > 0:
        sections_present.append("Skills")
    else:
        sections_missing.append("Skills")
    
    # Check Projects section
    if resume_data.get("projects") and len(resume_data.get("projects", [])) > 0:
        sections_present.append("Projects/Experience")
    else:
        sections_missing.append("Projects/Experience")
    
    # Check Contact Details section
    contact_info = resume_data.get("contact", {})
    if contact_info.get("email") or contact_info.get("phone"):
        sections_present.append("Contact Details")
    else:
        sections_missing.append("Contact Details")
    
    # Check Role Alignment
    if resume_data.get("role_alignment"):
        sections_present.append("Role Alignment")
    else:
        sections_missing.append("Role Alignment")
    
    # Calculate resume readiness score (0-100)
    # Each section = 20 points
    total_possible = 5  # Education, Skills, Projects, Contact, Role Alignment
    present_count = len(sections_present)
    resume_score = int((present_count / total_possible) * 100)
    
    # Determine readiness level
    if resume_score >= 80:
        readiness = "High - Interview ready"
    elif resume_score >= 60:
        readiness = "Medium - Some sections weak"
    elif resume_score >= 40:
        readiness = "Low - Major sections missing"
    else:
        readiness = "Very Low - Incomplete resume"
    
    return {
        "resume_score": resume_score,
        "sections_present": sections_present,
        "sections_missing": sections_missing,
        "total_sections": len(sections_present),
        "sections_needed": len(sections_missing),
        "readiness_level": readiness,
        "resume_analysis": f"{present_count} of {total_possible} resume sections complete"
    }


def validate_resume_result(result):
    """
    Validates that resume readiness result is complete.
    
    Args:
        result: The output from resume_readiness_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "resume_score", "sections_present", "sections_missing",
        "readiness_level", "resume_analysis"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Resume readiness analysis is valid and complete"
    }