"""
Portfolio Readiness Agent
Evaluates whether a student's portfolio evidence is complete and interview-ready
"""

def portfolio_readiness_agent(portfolio_data):
    """
    Evaluates student portfolio evidence completeness.
    
    Args:
        portfolio_data: Dictionary with portfolio information
        {
            "github_link": "https://github.com/...",
            "deployed_demo": "https://demo.example.com",
            "readme_quality": "good/average/poor",
            "linkedin_profile": "https://linkedin.com/...",
            "project_explanation": True/False
        }
        
    Returns:
        Dictionary with portfolio readiness score and gaps
    """
    
    # Initialize evidence checklist
    evidence_present = []
    evidence_missing = []
    
    # Check GitHub
    if portfolio_data.get("github_link"):
        evidence_present.append("GitHub Repository")
    else:
        evidence_missing.append("GitHub Repository")
    
    # Check Deployed Demo
    if portfolio_data.get("deployed_demo"):
        evidence_present.append("Deployed Demo")
    else:
        evidence_missing.append("Deployed Demo")
    
    # Check README/Project Explanation
    if portfolio_data.get("project_explanation"):
        evidence_present.append("Project Explanation/README")
    else:
        evidence_missing.append("Project Explanation/README")
    
    # Check LinkedIn
    if portfolio_data.get("linkedin_profile"):
        evidence_present.append("LinkedIn Profile")
    else:
        evidence_missing.append("LinkedIn Profile")
    
    # Calculate portfolio readiness score (0-100)
    # Each evidence type = 25 points
    total_possible = 4  # GitHub, Demo, README, LinkedIn
    present_count = len(evidence_present)
    portfolio_score = int((present_count / total_possible) * 100)
    
    # Determine readiness level
    if portfolio_score >= 75:
        readiness = "High - Interview ready"
    elif portfolio_score >= 50:
        readiness = "Medium - Some gaps"
    elif portfolio_score >= 25:
        readiness = "Low - Major gaps"
    else:
        readiness = "Very Low - Incomplete portfolio"
    
    return {
        "portfolio_score": portfolio_score,
        "evidence_present": evidence_present,
        "evidence_missing": evidence_missing,
        "total_evidence": len(evidence_present),
        "evidence_needed": len(evidence_missing),
        "readiness_level": readiness,
        "portfolio_analysis": f"{present_count} of {total_possible} portfolio evidence items present"
    }


def validate_portfolio_result(result):
    """
    Validates that portfolio readiness result is complete.
    
    Args:
        result: The output from portfolio_readiness_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "portfolio_score", "evidence_present", "evidence_missing",
        "readiness_level", "portfolio_analysis"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Portfolio readiness analysis is valid and complete"
    }