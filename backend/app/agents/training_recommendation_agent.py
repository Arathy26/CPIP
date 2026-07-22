"""
Training Recommendation Agent
Synthesizes all readiness assessments into personalized training plan
"""

def training_recommendation_agent(all_assessments):
    """
    Creates training plan synthesizing all readiness assessments.
    
    Args:
        all_assessments: Dictionary with all agent outputs
        {
            "skill_gap": {"score": 65, "missing_skills": [...]},
            "portfolio": {"score": 50, "evidence_missing": [...]},
            "resume": {"score": 80, "sections_missing": [...]},
            "interview": {"score": 70, "weak_dimensions": [...]},
            "target_role": "Full Stack Developer"
        }
        
    Returns:
        Dictionary with training plan
    """
    
    # Extract scores
    skill_gap_score = all_assessments.get("skill_gap", {}).get("score", 0)
    portfolio_score = all_assessments.get("portfolio", {}).get("score", 0)
    resume_score = all_assessments.get("resume", {}).get("score", 0)
    interview_score = all_assessments.get("interview", {}).get("score", 0)
    
    # Create training actions based on weakest areas
    training_actions = []
    
    # Priority 1: Skill gaps (most important for role readiness)
    if skill_gap_score < 70:
        training_actions.append({
            "priority": 1,
            "category": "Technical Skills",
            "action": "Learn missing skills: Python, FastAPI, Docker",
            "estimated_weeks": 8,
            "impact": "High - directly affects job readiness"
        })
    
    # Priority 2: Portfolio gaps (crucial for interviews)
    if portfolio_score < 70:
        training_actions.append({
            "priority": 2,
            "category": "Portfolio Development",
            "action": "Build and deploy a project, create GitHub README",
            "estimated_weeks": 4,
            "impact": "High - proves capability to employers"
        })
    
    # Priority 3: Interview preparation (weak dimensions)
    weak_dims = all_assessments.get("interview", {}).get("weak_dimensions", [])
    if weak_dims:
        training_actions.append({
            "priority": 3,
            "category": "Interview Preparation",
            "action": f"Practice {', '.join(weak_dims)} through mock interviews",
            "estimated_weeks": 4,
            "impact": "High - essential for passing interviews"
        })
    
    # Priority 4: Resume improvements
    if resume_score < 80:
        training_actions.append({
            "priority": 4,
            "category": "Resume Refinement",
            "action": "Add project impact statements and GitHub links",
            "estimated_weeks": 1,
            "impact": "Medium - improves first impression"
        })
    
    # Calculate total weeks
    total_weeks = sum(action["estimated_weeks"] for action in training_actions)
    
    # Create overall plan
    overall_readiness = int((skill_gap_score + portfolio_score + resume_score + interview_score) / 4)
    
    return {
        "target_role": all_assessments.get("target_role", "Unknown"),
        "current_overall_readiness": overall_readiness,
        "training_actions": training_actions,
        "total_estimated_weeks": total_weeks,
        "recommendation": f"Follow {len(training_actions)} prioritized actions over {total_weeks} weeks to reach interview-ready status",
        "next_milestone": "Complete Priority 1 and 2 before applying to jobs"
    }


def validate_training_result(result):
    """
    Validates training plan completeness.
    
    Args:
        result: The output from training_recommendation_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "target_role", "training_actions", "recommendation"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Training recommendation plan is valid and complete"
    }