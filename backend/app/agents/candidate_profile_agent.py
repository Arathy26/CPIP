"""
Candidate Profile Agent
Normalizes student data from the database into a structured profile
"""

def candidate_profile_agent(student_data):
    """
    Takes raw student data and returns a normalized candidate profile.
    
    Args:
        student_data: Dictionary with student information from STUDENT table
        
    Returns:
        Dictionary with structured candidate profile
    """
    
    if not student_data:
        return {"error": "No student data provided"}
    
    # Normalize the data into a structured profile
    profile = {
        "candidate_id": student_data.get("id"),
        "name": student_data.get("name"),
        "contact": {
            "email": student_data.get("email"),
            "location": student_data.get("location")
        },
        "academics": {
            "degree": student_data.get("degree"),
            "cgpa": student_data.get("cgpa")
        },
        "career": {
            "target_role": student_data.get("target_role"),
            "salary_expectation": student_data.get("salary_expected")
        },
        "skills": student_data.get("skills", []),
        "portfolio": {
            "github": student_data.get("github_link"),
            "linkedin": student_data.get("linkedin_id"),
            "deployed_demo": student_data.get("deployed_demo_link"),
            "project_readme": student_data.get("project_readme_link"),
            "resume": student_data.get("resume")
        }
    }
    
    return profile


def validate_profile(profile):
    """
    Validates that the candidate profile has all required fields.
    
    Args:
        profile: The normalized candidate profile
        
    Returns:
        Dictionary with validation result and any errors
    """
    
    required_fields = ["candidate_id", "name", "contact", "academics", "career", "skills", "portfolio"]
    missing_fields = [field for field in required_fields if field not in profile]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Profile is valid and complete"
    }