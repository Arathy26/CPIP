"""
Portfolio Readiness Routes
API endpoints for portfolio readiness evaluation
"""

from fastapi import APIRouter, HTTPException
from app.agents.portfolio_readiness_agent import portfolio_readiness_agent, validate_portfolio_result

router = APIRouter()

# Sample portfolio data (from CPIP_Seed_Data.json)
STUDENT_PORTFOLIOS = {
    1: {  # Arathy
        "github_link": "https://github.com/arathy/cpip-project",
        "deployed_demo": None,  # Missing
        "readme_quality": "good",
        "project_explanation": True,
        "linkedin_profile": None  # Missing
    },
    2: {  # Archana
        "github_link": "https://github.com/archana/backend-api",
        "deployed_demo": "https://archana-api.herokuapp.com",
        "readme_quality": "good",
        "project_explanation": True,
        "linkedin_profile": "https://linkedin.com/in/archana"
    },
    3: {  # Anamika
        "github_link": "https://github.com/anamika/fullstack-app",
        "deployed_demo": "https://anamika-app.vercel.app",
        "readme_quality": "average",
        "project_explanation": True,
        "linkedin_profile": None  # Missing
    }
}


@router.get("/portfolio-readiness/{student_id}")
def get_portfolio_readiness(student_id: int):
    """
    Get portfolio readiness analysis for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Portfolio readiness analysis with score and missing evidence
    """
    
    # Check if student exists
    if student_id not in STUDENT_PORTFOLIOS:
        raise HTTPException(
            status_code=404,
            detail=f"Student {student_id} not found"
        )
    
    # Get student portfolio data
    portfolio_data = STUDENT_PORTFOLIOS[student_id]
    
    # Run Portfolio Readiness Agent
    portfolio_result = portfolio_readiness_agent(portfolio_data)
    
    # Validate result
    validation = validate_portfolio_result(portfolio_result)
    
    # Return portfolio analysis with validation
    return {
        "student_id": student_id,
        "portfolio_analysis": portfolio_result,
        "validation": validation,
        "message": "Portfolio readiness analysis completed successfully"
    }


@router.get("/portfolio-readiness")
def list_all_portfolio_readiness():
    """
    Get portfolio readiness analysis for all students.
    
    Returns:
        List of all student portfolio readiness scores
    """
    
    results = []
    
    for student_id in STUDENT_PORTFOLIOS:
        portfolio_data = STUDENT_PORTFOLIOS[student_id]
        
        portfolio_result = portfolio_readiness_agent(portfolio_data)
        
        results.append({
            "student_id": student_id,
            "portfolio_score": portfolio_result["portfolio_score"],
            "readiness_level": portfolio_result["readiness_level"],
            "evidence_present": len(portfolio_result["evidence_present"]),
            "evidence_missing": len(portfolio_result["evidence_missing"])
        })
    
    return {
        "total_students": len(results),
        "portfolio_readiness": results,
        "message": "All portfolio readiness scores retrieved"
    }