"""
Training Recommendation Route
Uses the orchestrator's shared context (real outputs of every readiness
agent). No external APIs. No hardcoded skills.
"""

from fastapi import APIRouter, HTTPException
from app.agents.training_recommendation_agent import validate_training_result
from app.services.orchestrator import collect_agent_outputs

router = APIRouter()


@router.get("/training-plan/{student_id}")
def get_training_plan(student_id: int, role: str = None):
    ctx = collect_agent_outputs(student_id, role=role)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Student not found")

    role_data = ctx["role_requirements"]
    plan = ctx["training"]
    return {
        "student_id": student_id,
        "training_plan": plan,
        "role_requirements_source": (
            f"{role_data['job_postings_analyzed']} recruiter posting(s)" if role_data
            else "No recruiter postings for this role yet"
        ),
        "validation": validate_training_result(plan),
    }
