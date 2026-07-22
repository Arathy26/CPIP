"""
Explanation and Audit Routes
API endpoints for explanations and audit trails
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.agents.explanation_agent import explanation_agent, validate_explanation_result
from app.agents.audit_agent import audit_agent, validate_audit_result

router = APIRouter()

# Complete agent outputs for each student
COMPLETE_AGENT_OUTPUTS = {
    1: {
        "candidate_id": 1,
        "skill_gap_score": 65,
        "portfolio_score": 50,
        "resume_score": 100,
        "interview_score": 70,
        "role_recommendation": "Junior Full Stack Developer",
        "job_matches": 2,
        "training_actions": 3,
        "workflow_stage": "shortlisted"
    },
    2: {
        "candidate_id": 2,
        "skill_gap_score": 85,
        "portfolio_score": 100,
        "resume_score": 100,
        "interview_score": 80,
        "role_recommendation": "Junior Backend Developer",
        "job_matches": 3,
        "training_actions": 1,
        "workflow_stage": "technical_round"
    },
    3: {
        "candidate_id": 3,
        "skill_gap_score": 75,
        "portfolio_score": 75,
        "resume_score": 80,
        "interview_score": 70,
        "role_recommendation": "Junior Full Stack Developer",
        "job_matches": 2,
        "training_actions": 2,
        "workflow_stage": "applied"
    }
}


@router.get("/explanation/{student_id}")
def get_explanation(student_id: int):
    """
    Get human-readable explanation of readiness.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Clear explanation of readiness and recommendations
    """
    
    if student_id not in COMPLETE_AGENT_OUTPUTS:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    agent_outputs = COMPLETE_AGENT_OUTPUTS[student_id]
    
    # Run Explanation Agent
    explanation_result = explanation_agent(agent_outputs)
    
    # Validate result
    validation = validate_explanation_result(explanation_result)
    
    return {
        "student_id": student_id,
        "explanation": explanation_result,
        "validation": validation,
        "message": "Explanation generated successfully"
    }


@router.get("/explanation")
def list_all_explanations():
    """
    Get explanations for all students.
    
    Returns:
        Explanations for all students
    """
    
    results = []
    
    for student_id in COMPLETE_AGENT_OUTPUTS:
        agent_outputs = COMPLETE_AGENT_OUTPUTS[student_id]
        explanation_result = explanation_agent(agent_outputs)
        
        results.append({
            "student_id": student_id,
            "overall_readiness": explanation_result["overall_readiness_score"],
            "summary": explanation_result["summary"]
        })
    
    return {
        "total_students": len(results),
        "explanations": results,
        "message": "All explanations retrieved"
    }


@router.get("/audit/{student_id}")
def get_audit_trail(student_id: int):
    """
    Get audit trail for a student's decisions.
    
    Args:
        student_id: ID of the student
        
    Returns:
        Audit trail showing decision history
    """
    
    if student_id not in COMPLETE_AGENT_OUTPUTS:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    agent_outputs = COMPLETE_AGENT_OUTPUTS[student_id]
    
    # Create audit entry
    audit_input = {
        "candidate_id": student_id,
        "event_type": "readiness_evaluation",
        "scores": {
            "skill_gap": agent_outputs["skill_gap_score"],
            "portfolio": agent_outputs["portfolio_score"],
            "resume": agent_outputs["resume_score"],
            "interview": agent_outputs["interview_score"]
        },
        "recommendation": agent_outputs["role_recommendation"],
        "decision_reason": f"Based on skill alignment ({agent_outputs['skill_gap_score']}%), portfolio quality ({agent_outputs['portfolio_score']}%), and interview readiness ({agent_outputs['interview_score']}%)",
        "timestamp": datetime.now().isoformat()
    }
    
    # Run Audit Agent
    audit_result = audit_agent(audit_input)
    
    # Validate result
    validation = validate_audit_result(audit_result)
    
    return {
        "student_id": student_id,
        "audit_trail": audit_result,
        "validation": validation,
        "message": "Audit trail recorded"
    }


@router.get("/audit")
def list_all_audit_trails():
    """
    Get audit trails for all students.
    
    Returns:
        Audit trails for all decisions
    """
    
    results = []
    
    for student_id in COMPLETE_AGENT_OUTPUTS:
        agent_outputs = COMPLETE_AGENT_OUTPUTS[student_id]
        
        audit_input = {
            "candidate_id": student_id,
            "event_type": "readiness_evaluation",
            "scores": {
                "skill_gap": agent_outputs["skill_gap_score"],
                "portfolio": agent_outputs["portfolio_score"],
                "resume": agent_outputs["resume_score"],
                "interview": agent_outputs["interview_score"]
            },
            "recommendation": agent_outputs["role_recommendation"],
            "decision_reason": "Based on multi-dimensional readiness assessment",
            "timestamp": datetime.now().isoformat()
        }
        
        audit_result = audit_agent(audit_input)
        
        results.append({
            "student_id": student_id,
            "audit_id": audit_result["audit_id"],
            "event_type": audit_result["event_type"],
            "decision": audit_result["decision"],
            "timestamp": audit_result["timestamp"]
        })
    
    return {
        "total_students": len(results),
        "audit_trails": results,
        "message": "All audit trails retrieved"
    }