"""
Placement Workflow Routes
API endpoints for placement workflow tracking
"""

from fastapi import APIRouter, HTTPException
from app.agents.placement_workflow_agent import placement_workflow_agent, validate_workflow_result

router = APIRouter()

# Placement workflow data for students
PLACEMENT_WORKFLOW_DATA = {
    1: {
        "student_id": 1,
        "job_applied": "Junior Full Stack Developer",
        "current_stage": "shortlisted",
        "interview_rounds_completed": 0,
        "application_date": "2026-07-15",
        "last_update": "2026-07-18"
    },
    2: {
        "student_id": 2,
        "job_applied": "Junior Backend Developer",
        "current_stage": "technical_round",
        "interview_rounds_completed": 0,
        "application_date": "2026-07-10",
        "last_update": "2026-07-19"
    },
    3: {
        "student_id": 3,
        "job_applied": "Junior Full Stack Developer",
        "current_stage": "applied",
        "interview_rounds_completed": 0,
        "application_date": "2026-07-16",
        "last_update": "2026-07-18"
    }
}


@router.get("/placement-workflow/{student_id}")
def get_placement_workflow(student_id: int):
    """
    Get placement workflow status for a student.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Current workflow status and next action
    """
    
    if student_id not in PLACEMENT_WORKFLOW_DATA:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    workflow_data = PLACEMENT_WORKFLOW_DATA[student_id]
    
    # Run Placement Workflow Agent
    workflow_result = placement_workflow_agent(workflow_data)
    
    # Validate result
    validation = validate_workflow_result(workflow_result)
    
    return {
        "student_id": student_id,
        "placement_workflow": workflow_result,
        "validation": validation,
        "message": "Placement workflow status retrieved"
    }


@router.get("/placement-workflow")
def list_all_placement_workflows():
    """
    Get placement workflow status for all students.
    
    Returns:
        Workflow status summary for all students
    """
    
    results = []
    
    for student_id in PLACEMENT_WORKFLOW_DATA:
        workflow_data = PLACEMENT_WORKFLOW_DATA[student_id]
        workflow_result = placement_workflow_agent(workflow_data)
        
        results.append({
            "student_id": student_id,
            "job_applied": workflow_result["job_applied"],
            "current_stage": workflow_result["current_stage"],
            "stage_status": workflow_result["stage_status"],
            "next_action": workflow_result["next_action"]
        })
    
    return {
        "total_students": len(results),
        "placement_workflows": results,
        "message": "All placement workflows retrieved"
    }