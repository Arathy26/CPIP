"""
Training Recommendation Routes
API endpoints for training plan recommendations
"""

from fastapi import APIRouter, HTTPException
from app.agents.training_recommendation_agent import training_recommendation_agent, validate_training_result

router = APIRouter()

# Aggregate all assessments for students (from all previous agents)
STUDENT_ASSESSMENTS = {
    1: {  # Arathy
        "skill_gap": {"score": 65, "missing_skills": ["Machine Learning", "TensorFlow"]},
        "portfolio": {"score": 50, "evidence_missing": ["Deployed Demo"]},
        "resume": {"score": 100, "sections_missing": []},
        "interview": {"score": 70, "weak_dimensions": ["Communication", "Project Explanation"]},
        "target_role": "Full Stack Developer"
    },
    2: {  # Archana
        "skill_gap": {"score": 85, "missing_skills": []},
        "portfolio": {"score": 100, "evidence_missing": []},
        "resume": {"score": 100, "sections_missing": []},
        "interview": {"score": 80, "weak_dimensions": []},
        "target_role": "Backend Developer"
    },
    3: {  # Anamika
        "skill_gap": {"score": 75, "missing_skills": ["Docker"]},
        "portfolio": {"score": 75, "evidence_missing": []},
        "resume": {"score": 80, "sections_missing": []},
        "interview": {"score": 70, "weak_dimensions": ["Technical"]},
        "target_role": "Full Stack Developer"
    }
}


@router.get("/training-plan/{student_id}")
def get_training_plan(student_id: int):
    """
    Get personalized training plan for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Training plan with prioritized actions
    """
    
    if student_id not in STUDENT_ASSESSMENTS:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    assessments = STUDENT_ASSESSMENTS[student_id]
    
    # Run Training Recommendation Agent
    training_result = training_recommendation_agent(assessments)
    
    # Validate result
    validation = validate_training_result(training_result)
    
    return {
        "student_id": student_id,
        "training_plan": training_result,
        "validation": validation,
        "message": "Training plan created successfully"
    }


@router.get("/training-plan")
def list_all_training_plans():
    """
    Get training plans for all students.
    
    Returns:
        Training plans for all students
    """
    
    results = []
    
    for student_id in STUDENT_ASSESSMENTS:
        assessments = STUDENT_ASSESSMENTS[student_id]
        training_result = training_recommendation_agent(assessments)
        
        results.append({
            "student_id": student_id,
            "target_role": training_result["target_role"],
            "overall_readiness": training_result["current_overall_readiness"],
            "total_weeks": training_result["total_estimated_weeks"],
            "action_count": len(training_result["training_actions"])
        })
    
    return {
        "total_students": len(results),
        "training_plans": results,
        "message": "All training plans retrieved"
    }