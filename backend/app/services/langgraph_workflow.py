from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from datetime import datetime


class CPIPState(TypedDict):
    student_id: int
    student_profile: dict
    resume_profile: dict
    candidate_skills: list
    required_skills: list
    portfolio_data: dict
    target_role: str
    
    skill_gap_result: Optional[dict]
    portfolio_result: Optional[dict]
    resume_result: Optional[dict]
    interview_result: Optional[dict]
    role_result: Optional[dict]
    training_result: Optional[dict]
    job_opportunity_result: Optional[dict]
    placement_workflow_result: Optional[dict]
    explanation_result: Optional[dict]
    audit_result: Optional[dict]
    
    timestamp: str
    error: Optional[str]


def skill_gap_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.skill_gap_agent import skill_gap_agent
        result = skill_gap_agent(
            candidate_skills=state["student_profile"].get("skills", []),
            required_skills=state["required_skills"]
        )
        state["skill_gap_result"] = result
    except Exception as e:
        state["error"] = f"Skill Gap Error: {str(e)}"
    return state


def portfolio_readiness_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.portfolio_readiness_agent import portfolio_readiness_agent
        portfolio_data = {
            "github_link": state["student_profile"].get("github_link"),
            "deployed_demo": state["resume_profile"].get("deployed_demo"),
            "project_explanation": bool(state["resume_profile"].get("project_explanation")),
            "linkedin_profile": state["student_profile"].get("linkedin_id"),
        }
        result = portfolio_readiness_agent(portfolio_data)
        state["portfolio_result"] = result
    except Exception as e:
        state["error"] = f"Portfolio Error: {str(e)}"
    return state


def resume_readiness_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.resume_readiness_agent import resume_readiness_agent
        resume_input = {
            "resume_sections": state["resume_profile"].get("sections", {}),
            "skills": state["student_profile"].get("skills", []),
            "target_role": state["student_profile"].get("target_role", ""),
        }
        result = resume_readiness_agent(resume_input)
        state["resume_result"] = result
    except Exception as e:
        state["error"] = f"Resume Error: {str(e)}"
    return state


def interview_readiness_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.interview_readiness_agent import interview_readiness_agent
        skills_count = len(state["student_profile"].get("skills", []))
        projects_count = len(state["resume_profile"].get("projects", []))
        has_github = bool(state["student_profile"].get("github_link"))
        has_linkedin = bool(state["student_profile"].get("linkedin_id"))
        
        interview_scores = {
            "aptitude_score": min(60 + (skills_count * 2), 100),
            "technical_score": min(50 + (skills_count * 3), 100) + (10 if has_github else 0),
            "communication_score": min(55 + (projects_count * 5), 100) + (10 if has_linkedin else 0),
            "project_explanation_score": min(40 + (projects_count * 10), 100),
        }
        result = interview_readiness_agent(interview_scores)
        state["interview_result"] = result
    except Exception as e:
        state["error"] = f"Interview Error: {str(e)}"
    return state


def role_matching_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.role_matching_agent import role_matching_agent
        profile = {
            "candidate_id": state["student_id"],
            "skills": state["student_profile"].get("skills", []),
            "target_role": state["student_profile"].get("target_role", ""),
        }
        scores = {
            "skill_gap_score": state["skill_gap_result"].get("gap_score", 0) if state["skill_gap_result"] else 0,
            "portfolio_score": state["portfolio_result"].get("portfolio_score", 0) if state["portfolio_result"] else 0,
            "resume_score": state["resume_result"].get("resume_score", 0) if state["resume_result"] else 0,
        }
        result = role_matching_agent(profile, scores)
        state["role_result"] = result
    except Exception as e:
        state["error"] = f"Role Matching Error: {str(e)}"
    return state


def training_recommendation_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.training_recommendation_agent import training_recommendation_agent
        assessments = {
            "skill_gap": {
                "score": state["skill_gap_result"].get("gap_score", 0) if state["skill_gap_result"] else 0,
                "missing_skills": state["skill_gap_result"].get("missing_skills", []) if state["skill_gap_result"] else []
            },
            "portfolio": {
                "score": state["portfolio_result"].get("portfolio_score", 0) if state["portfolio_result"] else 0,
                "evidence_missing": state["portfolio_result"].get("evidence_missing", []) if state["portfolio_result"] else []
            },
            "resume": {
                "score": state["resume_result"].get("resume_score", 0) if state["resume_result"] else 0,
                "sections_missing": state["resume_result"].get("missing_sections", []) if state["resume_result"] else []
            },
            "interview": {
                "score": state["interview_result"].get("interview_readiness_score", 0) if state["interview_result"] else 0,
                "weak_dimensions": state["interview_result"].get("weak_areas", []) if state["interview_result"] else []
            },
            "target_role": state["student_profile"].get("target_role", ""),
        }
        result = training_recommendation_agent(assessments)
        state["training_result"] = result
    except Exception as e:
        state["error"] = f"Training Error: {str(e)}"
    return state


def job_opportunity_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.job_opportunity_agent import job_opportunity_agent
        job_input = {
            "candidate_id": state["student_id"],
            "skills": state["student_profile"].get("skills", []),
            "target_role": state["student_profile"].get("target_role", ""),
            "role_match_score": state["role_result"].get("role_match_score", 0) if state["role_result"] else 0,
        }
        result = job_opportunity_agent(job_input)
        state["job_opportunity_result"] = result
    except Exception as e:
        state["error"] = f"Job Opportunity Error: {str(e)}"
    return state


def placement_workflow_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.placement_workflow_agent import placement_workflow_agent
        avg_readiness = (
            (state["skill_gap_result"].get("gap_score", 0) if state["skill_gap_result"] else 0) +
            (state["portfolio_result"].get("portfolio_score", 0) if state["portfolio_result"] else 0) +
            (state["interview_result"].get("interview_readiness_score", 0) if state["interview_result"] else 0)
        ) / 3
        workflow_input = {
            "candidate_id": state["student_id"],
            "target_role": state["student_profile"].get("target_role", ""),
            "readiness_score": avg_readiness,
            "matching_jobs": len(state["job_opportunity_result"].get("matching_jobs", [])) if state["job_opportunity_result"] else 0,
        }
        result = placement_workflow_agent(workflow_input)
        state["placement_workflow_result"] = result
    except Exception as e:
        state["error"] = f"Placement Workflow Error: {str(e)}"
    return state


def explanation_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.explanation_agent import explanation_agent
        agent_outputs = {
            "candidate_id": state["student_id"],
            "skill_gap_score": state["skill_gap_result"].get("gap_score", 0) if state["skill_gap_result"] else 0,
            "portfolio_score": state["portfolio_result"].get("portfolio_score", 0) if state["portfolio_result"] else 0,
            "resume_score": state["resume_result"].get("resume_score", 0) if state["resume_result"] else 0,
            "interview_score": state["interview_result"].get("interview_readiness_score", 0) if state["interview_result"] else 0,
            "role_recommendation": state["role_result"].get("recommended_role", state["student_profile"].get("target_role", "")) if state["role_result"] else state["student_profile"].get("target_role", ""),
            "job_matches": len(state["job_opportunity_result"].get("matching_jobs", [])) if state["job_opportunity_result"] else 0,
            "training_actions": len(state["training_result"].get("training_actions", [])) if state["training_result"] else 0,
            "workflow_stage": state["placement_workflow_result"].get("current_stage", "not_applied") if state["placement_workflow_result"] else "not_applied",
        }
        result = explanation_agent(agent_outputs)
        state["explanation_result"] = result
    except Exception as e:
        state["error"] = f"Explanation Error: {str(e)}"
    return state


def audit_node(state: CPIPState) -> CPIPState:
    try:
        from app.agents.audit_agent import audit_agent
        audit_input = {
            "candidate_id": state["student_id"],
            "event_type": "full_langgraph_pipeline_evaluation",
            "scores": {
                "skill_gap": state["skill_gap_result"].get("gap_score", 0) if state["skill_gap_result"] else 0,
                "portfolio": state["portfolio_result"].get("portfolio_score", 0) if state["portfolio_result"] else 0,
                "resume": state["resume_result"].get("resume_score", 0) if state["resume_result"] else 0,
                "interview": state["interview_result"].get("interview_readiness_score", 0) if state["interview_result"] else 0,
            },
            "recommendation": state["role_result"].get("recommended_role", state["student_profile"].get("target_role", "")) if state["role_result"] else state["student_profile"].get("target_role", ""),
            "decision_reason": state["explanation_result"].get("full_explanation", "") if state["explanation_result"] else "",
            "timestamp": state["timestamp"],
        }
        result = audit_agent(audit_input)
        state["audit_result"] = result
    except Exception as e:
        state["error"] = f"Audit Error: {str(e)}"
    return state


def build_cpip_workflow():
    workflow = StateGraph(CPIPState)
    
    workflow.add_node("skill_gap", skill_gap_node)
    workflow.add_node("portfolio", portfolio_readiness_node)
    workflow.add_node("resume", resume_readiness_node)
    workflow.add_node("interview", interview_readiness_node)
    workflow.add_node("role_match", role_matching_node)
    workflow.add_node("training", training_recommendation_node)
    workflow.add_node("job_opportunity", job_opportunity_node)
    workflow.add_node("placement_workflow", placement_workflow_node)
    workflow.add_node("explanation", explanation_node)
    workflow.add_node("audit", audit_node)
    
    workflow.add_edge("START", "skill_gap")
    workflow.add_edge("skill_gap", "portfolio")
    workflow.add_edge("portfolio", "resume")
    workflow.add_edge("resume", "interview")
    workflow.add_edge("interview", "role_match")
    workflow.add_edge("role_match", "training")
    workflow.add_edge("training", "job_opportunity")
    workflow.add_edge("job_opportunity", "placement_workflow")
    workflow.add_edge("placement_workflow", "explanation")
    workflow.add_edge("explanation", "audit")
    workflow.add_edge("audit", END)
    
    return workflow.compile()


def run_cpip_workflow(student_id: int, required_skills: list):
    from app.data import seed_data
    
    student_profile = seed_data.get_student(student_id)
    resume_profile = seed_data.get_resume(student_id)
    
    if not student_profile:
        return {"error": f"Student {student_id} not found"}
    
    compiled_graph = build_cpip_workflow()
    
    initial_state: CPIPState = {
        "student_id": student_id,
        "student_profile": student_profile,
        "resume_profile": resume_profile or {},
        "candidate_skills": student_profile.get("skills", []),
        "required_skills": required_skills,
        "portfolio_data": {
            "github_link": student_profile.get("github_link"),
            "deployed_demo": resume_profile.get("deployed_demo") if resume_profile else None,
            "linkedin_id": student_profile.get("linkedin_id"),
        },
        "target_role": student_profile.get("target_role", ""),
        "skill_gap_result": None,
        "portfolio_result": None,
        "resume_result": None,
        "interview_result": None,
        "role_result": None,
        "training_result": None,
        "job_opportunity_result": None,
        "placement_workflow_result": None,
        "explanation_result": None,
        "audit_result": None,
        "timestamp": datetime.now().isoformat(),
        "error": None,
    }
    
    final_state = compiled_graph.invoke(initial_state)
    return final_state