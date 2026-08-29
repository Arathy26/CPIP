"""
Placement Workflow Routes
API endpoints for placement workflow tracking
"""

from fastapi import APIRouter, HTTPException
from app.agents.placement_workflow_agent import placement_workflow_agent, validate_workflow_result
from app.data import seed_data

router = APIRouter()

# In-memory workflow store
_WORKFLOWS = {}


def _get_default_workflow(student):
    return {
        "student_id": student["id"],
        "job_applied": student.get("target_role", "Not specified"),
        "current_stage": "not_applied",
        "interview_rounds_completed": 0,
        "application_date": None,
        "last_update": None,
    }


@router.get("/placement-workflow/{student_id}")
def get_placement_workflow(student_id: int):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    workflow_data = _WORKFLOWS.get(student_id, _get_default_workflow(student))
    workflow_result = placement_workflow_agent(workflow_data)
    validation = validate_workflow_result(workflow_result)

    return {
        "student_id": student_id,
        "placement_workflow": workflow_result,
        "validation": validation,
        "message": "Placement workflow status retrieved"
    }


@router.get("/placement-workflow")
def list_all_placement_workflows():
    results = []

    for student in seed_data.get_all_students():
        student_id = student["id"]
        workflow_data = _WORKFLOWS.get(student_id, _get_default_workflow(student))
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


@router.post("/placement-workflow/{student_id}/update")
def update_placement_workflow(student_id: int, stage: str, job_applied: str = None):
    student = seed_data.get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")

    existing = _WORKFLOWS.get(student_id, _get_default_workflow(student))
    existing["current_stage"] = stage
    if job_applied:
        existing["job_applied"] = job_applied
    _WORKFLOWS[student_id] = existing

    workflow_result = placement_workflow_agent(existing)

    return {
        "student_id": student_id,
        "updated_workflow": workflow_result,
        "message": f"Workflow updated to stage: {stage}"
    }