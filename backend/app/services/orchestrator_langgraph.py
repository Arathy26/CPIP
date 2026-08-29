
from langgraph.graph import StateGraph, END
from typing import TypedDict, Any, Optional, List
from datetime import datetime

from app.agents.candidate_profile_agent import candidate_profile_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.agents.portfolio_readiness_agent import portfolio_readiness_agent
from app.agents.resume_readiness_agent import resume_readiness_agent
from app.agents.interview_readiness_agent import interview_readiness_agent
from app.agents.role_matching_agent import role_matching_agent
from app.agents.training_recommendation_agent import training_recommendation_agent
from app.agents.job_opportunity_agent import job_opportunity_agent
from app.agents.placement_workflow_agent import placement_workflow_agent
from app.agents.explanation_agent import explanation_agent
from app.agents.audit_agent import audit_agent

from app.data import seed_data

class CPIPState(TypedDict):
    student_id: int
    candidate_profile: Optional[dict]
    resume_data: Optional[dict]
    target_role: str
    normalized_profile: Optional[dict]
    skill_gap_result: Optional[dict]
    portfolio_readiness_result: Optional[dict]
    resume_readiness_result: Optional[dict]
    interview_readiness_result: Optional[dict]
    readiness_scores: dict
    role_match_result: Optional[dict]
    training_result: Optional[dict]
    job_match_result: Optional[dict]
    workflow_result: Optional[dict]
    explanation_result: Optional[dict]
    audit_result: Optional[dict]
    execution_errors: List[str]
    workflow_stage: str
    timestamp: str

def node_initialize_context(state: CPIPState) -> CPIPState:
    try:
        student = seed_data.get_student(state["student_id"])
        resume = seed_data.get_resume(state["student_id"])
        if not student:
            state["execution_errors"].append(f"Student not found")
            state["workflow_stage"] = "error"
            return state
        state["candidate_profile"] = student
        state["resume_data"] = resume or {}
        state["target_role"] = student.get("target_role", "")
        state["workflow_stage"] = "context_initialized"
    except Exception as e:
        state["execution_errors"].append(f"Error: {str(e)}")
    return state

def node_candidate_profile(state: CPIPState) -> CPIPState:
    try:
        if state["candidate_profile"]:
            profile = candidate_profile_agent(state["candidate_profile"])
            state["normalized_profile"] = profile
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_skill_gap(state: CPIPState) -> CPIPState:
    try:
        if state["normalized_profile"]:
            candidate_skills = state["normalized_profile"].get("skills", [])
            required_skills = ["Python", "Git"]
            gap_result = skill_gap_agent(candidate_skills, required_skills)
            state["skill_gap_result"] = gap_result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_portfolio_readiness(state: CPIPState) -> CPIPState:
    try:
        portfolio_data = {
            "github_link": state["candidate_profile"].get("github_link"),
            "deployed_demo": state["resume_data"].get("deployed_demo"),
            "readme_quality": state["resume_data"].get("readme_quality"),
            "project_explanation": state["resume_data"].get("project_explanation", False),
            "linkedin_profile": state["candidate_profile"].get("linkedin_id"),
        }
        result = portfolio_readiness_agent(portfolio_data)
        state["portfolio_readiness_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_resume_readiness(state: CPIPState) -> CPIPState:
    try:
        resume_data = {
            "name": state["candidate_profile"].get("name"),
            "email": state["candidate_profile"].get("email"),
            "skills": state["candidate_profile"].get("skills", []),
        }
        result = resume_readiness_agent(resume_data)
        state["resume_readiness_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_interview_readiness(state: CPIPState) -> CPIPState:
    try:
        interview_scores = {
            "aptitude_score": 65,
            "technical_score": 70,
            "communication_score": 75,
            "project_explanation_score": 70,
        }
        result = interview_readiness_agent(interview_scores)
        state["interview_readiness_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_aggregate_scores(state: CPIPState) -> CPIPState:
    try:
        scores = {
            "skill_gap_score": state.get("skill_gap_result", {}).get("gap_score", 0),
            "portfolio_score": state.get("portfolio_readiness_result", {}).get("portfolio_score", 0),
            "resume_score": state.get("resume_readiness_result", {}).get("resume_readiness_score", 0),
            "interview_readiness_score": state.get("interview_readiness_result", {}).get("interview_readiness_score", 0),
        }
        state["readiness_scores"] = scores
        seed_data.update_readiness_scores(state["student_id"], scores)
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_role_matching(state: CPIPState) -> CPIPState:
    try:
        profile = {
            "candidate_id": state["student_id"],
            "skills": state["candidate_profile"].get("skills", []),
            "target_role": state["target_role"],
        }
        result = role_matching_agent(profile, state["readiness_scores"])
        state["role_match_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_training_recommendation(state: CPIPState) -> CPIPState:
    try:
        assessments = {
            "skill_gap": state.get("skill_gap_result", {}),
            "portfolio": state.get("portfolio_readiness_result", {}),
            "resume": state.get("resume_readiness_result", {}),
            "interview": state.get("interview_readiness_result", {}),
            "target_role": state["target_role"],
        }
        result = training_recommendation_agent(assessments)
        state["training_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_job_opportunity_matching(state: CPIPState) -> CPIPState:
    try:
        candidate_profile_for_match = {
            "candidate_id": state["student_id"],
            "skills": state["candidate_profile"].get("skills", []),
            "readiness": state["readiness_scores"],
        }
        result = job_opportunity_agent(candidate_profile_for_match)
        state["job_match_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_placement_workflow(state: CPIPState) -> CPIPState:
    try:
        workflow_input = {
            "candidate_id": state["student_id"],
            "current_stage": "profile_evaluation",
            "recommended_jobs": state.get("job_match_result", {}).get("matches", []),
            "readiness_scores": state["readiness_scores"],
        }
        result = placement_workflow_agent(workflow_input)
        state["workflow_result"] = result
        state["workflow_stage"] = "workflow_tracked"
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_explanation(state: CPIPState) -> CPIPState:
    try:
        agent_outputs = {
            "candidate_id": state["student_id"],
            "skill_gap_score": state["readiness_scores"].get("skill_gap_score", 0),
            "portfolio_score": state["readiness_scores"].get("portfolio_score", 0),
            "resume_score": state["readiness_scores"].get("resume_score", 0),
            "interview_score": state["readiness_scores"].get("interview_readiness_score", 0),
        }
        result = explanation_agent(agent_outputs)
        state["explanation_result"] = result
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def node_audit(state: CPIPState) -> CPIPState:
    try:
        audit_input = {
            "candidate_id": state["student_id"],
            "event_type": "full_workflow_evaluation",
            "scores": state["readiness_scores"],
            "timestamp": state["timestamp"],
        }
        result = audit_agent(audit_input)
        state["audit_result"] = result
        state["workflow_stage"] = "workflow_complete"
    except Exception as e:
        state["execution_errors"].append(str(e))
    return state

def build_cpip_workflow():
    workflow = StateGraph(CPIPState)
    workflow.add_node("initialize", node_initialize_context)
    workflow.add_node("candidate_profile", node_candidate_profile)
    workflow.add_node("skill_gap", node_skill_gap)
    workflow.add_node("portfolio_readiness", node_portfolio_readiness)
    workflow.add_node("resume_readiness", node_resume_readiness)
    workflow.add_node("interview_readiness", node_interview_readiness)
    workflow.add_node("aggregate_scores", node_aggregate_scores)
    workflow.add_node("role_matching", node_role_matching)
    workflow.add_node("training_recommendation", node_training_recommendation)
    workflow.add_node("job_opportunity_matching", node_job_opportunity_matching)
    workflow.add_node("placement_workflow", node_placement_workflow)
    workflow.add_node("explanation", node_explanation)
    workflow.add_node("audit", node_audit)
    
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "candidate_profile")
    workflow.add_edge("candidate_profile", "skill_gap")
    workflow.add_edge("candidate_profile", "portfolio_readiness")
    workflow.add_edge("candidate_profile", "resume_readiness")
    workflow.add_edge("candidate_profile", "interview_readiness")
    workflow.add_edge("skill_gap", "aggregate_scores")
    workflow.add_edge("portfolio_readiness", "aggregate_scores")
    workflow.add_edge("resume_readiness", "aggregate_scores")
    workflow.add_edge("interview_readiness", "aggregate_scores")
    workflow.add_edge("aggregate_scores", "role_matching")
    workflow.add_edge("role_matching", "training_recommendation")
    workflow.add_edge("training_recommendation", "job_opportunity_matching")
    workflow.add_edge("job_opportunity_matching", "placement_workflow")
    workflow.add_edge("placement_workflow", "explanation")
    workflow.add_edge("explanation", "audit")
    workflow.add_edge("audit", END)
    return workflow.compile()

def run_cpip_workflow(student_id: int) -> dict:
    compiled_workflow = build_cpip_workflow()
    initial_state: CPIPState = {
        "student_id": student_id,
        "candidate_profile": None,
        "resume_data": None,
        "target_role": "",
        "normalized_profile": None,
        "skill_gap_result": None,
        "portfolio_readiness_result": None,
        "resume_readiness_result": None,
        "interview_readiness_result": None,
        "readiness_scores": {},
        "role_match_result": None,
        "training_result": None,
        "job_match_result": None,
        "workflow_result": None,
        "explanation_result": None,
        "audit_result": None,
        "execution_errors": [],
        "workflow_stage": "initialized",
        "timestamp": datetime.now().isoformat(),
    }
    try:
        final_state = compiled_workflow.invoke(initial_state)
        return {
            "success": True,
            "student_id": student_id,
            "workflow_stage": final_state["workflow_stage"],
            "readiness_scores": final_state["readiness_scores"],
            "role_match": final_state.get("role_match_result"),
            "job_matches": final_state.get("job_match_result"),
            "training_plan": final_state.get("training_result"),
            "explanation": final_state.get("explanation_result"),
            "audit": final_state.get("audit_result"),
            "errors": final_state.get("execution_errors", []),
            "timestamp": final_state["timestamp"],
        }
    except Exception as e:
        return {
            "success": False,
            "student_id": student_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
