"""
Explanation Agent
Converts technical agent outputs into human-readable explanations
"""

def explanation_agent(agent_outputs):
    """
    Creates human-readable explanations from agent outputs.
    
    Args:
        agent_outputs: Dictionary with all agent outputs
        {
            "candidate_id": 1,
            "skill_gap_score": 65,
            "portfolio_score": 50,
            "resume_score": 100,
            "interview_score": 70,
            "role_recommendation": "Junior Full Stack Developer",
            "job_matches": 2,
            "training_actions": 3,
            "workflow_stage": "shortlisted"
        }
        
    Returns:
        Dictionary with explanations
    """
    
    candidate_id = agent_outputs.get("candidate_id")
    skill_gap = agent_outputs.get("skill_gap_score", 0)
    portfolio = agent_outputs.get("portfolio_score", 0)
    resume = agent_outputs.get("resume_score", 0)
    interview = agent_outputs.get("interview_score", 0)
    
    # Calculate overall readiness
    overall = int((skill_gap + portfolio + resume + interview) / 4)
    
    # Build explanations
    explanations = []
    
    # Skill gap explanation
    if skill_gap < 70:
        explanations.append(f"Skills: You have {skill_gap}% skill alignment with your target role. Focus on learning missing technical skills to improve.")
    else:
        explanations.append(f"Skills: Strong alignment ({skill_gap}%) with target role requirements.")
    
    # Portfolio explanation
    if portfolio < 70:
        explanations.append(f"Portfolio: Your project evidence needs strengthening ({portfolio}%). Add deployed demos and improve GitHub README.")
    else:
        explanations.append(f"Portfolio: Strong project evidence ({portfolio}%) with good GitHub and deployment proof.")
    
    # Resume explanation
    if resume < 80:
        explanations.append(f"Resume: Completeness at {resume}%. Add project impact statements and links to deployment.")
    else:
        explanations.append(f"Resume: Well-structured ({resume}%) with all key sections present.")
    
    # Interview explanation
    if interview < 70:
        explanations.append(f"Interview Prep: Readiness at {interview}%. Practice project explanation and technical Q&A.")
    else:
        explanations.append(f"Interview Prep: Good readiness ({interview}%) across all dimensions.")
    
    # Role recommendation explanation
    role = agent_outputs.get("role_recommendation", "Not determined")
    explanations.append(f"Recommended Role: {role} based on your overall profile.")
    
    # Job match explanation
    job_count = agent_outputs.get("job_matches", 0)
    explanations.append(f"Job Opportunities: {job_count} suitable jobs match your profile and are worth applying to.")
    
    # Training explanation
    training_count = agent_outputs.get("training_actions", 0)
    explanations.append(f"Next Steps: Follow {training_count} prioritized training actions to improve readiness.")
    
    # Overall readiness explanation
    if overall >= 80:
        readiness_text = "INTERVIEW READY - You are well-prepared for interviews."
    elif overall >= 70:
        readiness_text = "GOOD READINESS - Minor preparation needed before interviews."
    elif overall >= 60:
        readiness_text = "FAIR READINESS - Moderate preparation recommended."
    else:
        readiness_text = "EARLY STAGE - Significant preparation needed."
    
    explanations.append(f"Overall Readiness: {overall}%. Status: {readiness_text}")
    
    return {
        "candidate_id": candidate_id,
        "overall_readiness_score": overall,
        "explanations": explanations,
        "full_explanation": "\n".join(explanations),
        "summary": f"Candidate {candidate_id}: {overall}% overall readiness. {readiness_text}"
    }


def validate_explanation_result(result):
    """
    Validates explanation result.
    
    Args:
        result: The output from explanation_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = ["candidate_id", "explanations", "full_explanation"]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Explanation is valid and complete"
    }