"""
Interview Readiness Agent
Evaluates interview preparedness across multiple dimensions
"""

def interview_readiness_agent(interview_scores):
    """
    Evaluates interview readiness across multiple dimensions.
    
    Args:
        interview_scores: Dictionary with dimension scores
        {
            "aptitude_score": 75,  # Reasoning, quantitative
            "technical_score": 80,  # Coding, concepts
            "communication_score": 70,  # Clarity, professionalism
            "project_explanation_score": 65  # Ability to discuss work
        }
        
    Returns:
        Dictionary with interview readiness assessment
    """
    
    # Extract scores
    aptitude = interview_scores.get("aptitude_score", 0)
    technical = interview_scores.get("technical_score", 0)
    communication = interview_scores.get("communication_score", 0)
    project_explain = interview_scores.get("project_explanation_score", 0)
    
    # Calculate composite score
    composite_score = int((aptitude + technical + communication + project_explain) / 4)
    
    # Analyze each dimension
    dimension_analysis = {
        "aptitude": {
            "score": aptitude,
            "status": "Strong" if aptitude >= 75 else "Moderate" if aptitude >= 60 else "Needs Work",
            "focus": "Logical reasoning and quantitative skills"
        },
        "technical": {
            "score": technical,
            "status": "Strong" if technical >= 75 else "Moderate" if technical >= 60 else "Needs Work",
            "focus": "Coding ability and concept knowledge"
        },
        "communication": {
            "score": communication,
            "status": "Strong" if communication >= 75 else "Moderate" if communication >= 60 else "Needs Work",
            "focus": "Clarity and professionalism in speaking"
        },
        "project_explanation": {
            "score": project_explain,
            "status": "Strong" if project_explain >= 75 else "Moderate" if project_explain >= 60 else "Needs Work",
            "focus": "Ability to discuss and explain projects"
        }
    }
    
    # Determine readiness level
    if composite_score >= 80:
        readiness = "High - Interview Ready"
    elif composite_score >= 70:
        readiness = "Good - Minor Preparation Needed"
    elif composite_score >= 60:
        readiness = "Fair - Moderate Preparation Needed"
    else:
        readiness = "Low - Significant Preparation Required"
    
    # Identify weakest dimensions for improvement focus
    weak_dimensions = []
    for dim, data in dimension_analysis.items():
        if data["score"] < 70:
            weak_dimensions.append(dim)
    
    return {
        "interview_readiness_score": composite_score,
        "readiness_level": readiness,
        "dimension_analysis": dimension_analysis,
        "weak_dimensions": weak_dimensions,
        "preparation_focus": f"Focus on: {', '.join(weak_dimensions) if weak_dimensions else 'General confidence building'}"
    }


def validate_interview_result(result):
    """
    Validates that interview readiness result is complete.
    
    Args:
        result: The output from interview_readiness_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "interview_readiness_score", "readiness_level", "dimension_analysis"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Interview readiness analysis is valid and complete"
    }