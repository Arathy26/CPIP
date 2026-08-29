"""
CPIP LangGraph Workflow Routes
Exposes the LangGraph orchestrator as FastAPI endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.data.database import get_db
from app.services.orchestrator_langgraph import run_cpip_workflow

router = APIRouter(prefix="/api/langgraph", tags=["langgraph"])


# ════════════════════════════════════════════════════════════════════════════════
# WORKFLOW EXECUTION ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/evaluate")
async def evaluate_student_langgraph(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Execute complete LangGraph workflow for a student.
    
    Runs all 11 agents in optimized parallel + sequential order:
    - Parallel: Skill Gap, Portfolio, Resume, Interview (2-5)
    - Sequential: Role Matching → Training → Jobs → Workflow → Explanation → Audit (6-11)
    
    Args:
        student_id: The student to evaluate
        
    Returns:
        {
            "success": bool,
            "student_id": int,
            "workflow_stage": str,
            "readiness_scores": {...},
            "role_match": {...},
            "job_matches": {...},
            "training_plan": {...},
            "explanation": {...},
            "audit": {...},
            "errors": [str],
            "timestamp": str
        }
    """
    try:
        result = run_cpip_workflow(student_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Workflow failed: {result.get('error')}"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution error: {str(e)}"
        )


@router.get("/evaluate/{student_id}")
async def get_student_evaluation(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve cached evaluation result for a student.
    
    Args:
        student_id: The student ID
        
    Returns:
        Last workflow execution result or status
    """
    try:
        from app.data.database import ReadinessScoreModel
        
        scores = db.query(ReadinessScoreModel).filter(
            ReadinessScoreModel.student_id == student_id
        ).first()
        
        if not scores:
            raise HTTPException(
                status_code=404,
                detail=f"No evaluation found for student {student_id}"
            )
        
        return {
            "student_id": student_id,
            "readiness_scores": {
                "skill_gap_score": scores.skill_gap_score,
                "portfolio_score": scores.portfolio_score,
                "resume_score": scores.resume_score,
                "interview_readiness_score": scores.interview_readiness_score,
            },
            "overall_readiness": (
                scores.skill_gap_score + 
                scores.portfolio_score + 
                scores.resume_score + 
                scores.interview_readiness_score
            ) / 4,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving evaluation: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/health")
async def langgraph_health():
    """
    Check LangGraph orchestrator health.
    """
    return {
        "status": "ok",
        "service": "langgraph_orchestrator",
        "agents_available": 11,
        "flow_type": "parallel_sequential_hybrid",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/info")
async def langgraph_info():
    """
    Get information about LangGraph workflow architecture.
    """
    return {
        "workflow_architecture": "Parallel + Sequential Hybrid",
        "parallel_agents": [
            "Skill Gap Agent",
            "Portfolio Readiness Agent",
            "Resume Readiness Agent",
            "Interview Readiness Agent"
        ],
        "sequential_agents": [
            "Candidate Profile Agent",
            "Role Matching Agent",
            "Training Recommendation Agent",
            "Job Opportunity Matching Agent",
            "Placement Workflow Agent",
            "Explanation Agent",
            "Audit Agent"
        ],
        "total_agents": 11,
        "key_features": [
            "Deterministic scoring (rules-based, not LLM)",
            "Shared workflow context (CPIPState)",
            "Parallel execution where possible",
            "Audit trail for all decisions",
            "Human-in-the-loop ready",
        ]
    }