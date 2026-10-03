"""
CPIP LangGraph Orchestrator (Stage 3 — stateless)

Each node wraps ONE step function from app/services/orchestrator.py, so the
LangGraph run and the plain orchestrator give identical, deterministic
results. Nodes return only the keys they add (partial state updates).

Flow is sequential because langgraph==0.0.16 does not support fan-out
(one node with several outgoing edges). Every agent is a fast rule-based
function, so sequential order costs nothing meaningful.

initialize -> candidate_profile -> skill_gap  (each node named <step>_node) -> portfolio_readiness
-> resume_readiness -> interview_readiness -> role_matching
-> job_opportunity_matching -> training_recommendation -> placement_workflow
-> aggregate_scores -> explanation_audit -> END
"""

import operator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END

from app.services.orchestrator import (
    AGENT_STEPS, step_load_context, explain_and_audit,
)


class CPIPState(TypedDict, total=False):
    student_id: int
    role: Optional[str]
    student: Optional[dict]
    target_role: Optional[str]
    resume_data: Optional[dict]
    role_requirements: Optional[dict]
    candidate_profile: Optional[dict]
    skill_gap: Optional[dict]
    portfolio: Optional[dict]
    resume: Optional[dict]
    interview: Optional[dict]
    role_match: Optional[dict]
    job_match: Optional[dict]
    training: Optional[dict]
    applications: Optional[list]
    scores: Optional[dict]
    explanation: Optional[dict]
    audit: Optional[dict]
    final_scores: Optional[dict]
    completed_nodes: Annotated[List[str], operator.add]
    errors: Annotated[List[str], operator.add]


def _node(name, step):
    """Wrap a step: return its partial update, record success or the error."""
    def run(state: CPIPState) -> Dict[str, Any]:
        if state.get("errors"):
            return {}          # an earlier node failed; do not build on bad data
        try:
            update = step(state)
            return {**update, "completed_nodes": [name]}
        except Exception as exc:
            return {"errors": [f"{name}: {type(exc).__name__}: {exc}"]}
    return run


def _initialize(state: CPIPState) -> Dict[str, Any]:
    update = step_load_context(state)
    if not update.get("student"):
        return {"errors": [f"Student {state['student_id']} not found"]}
    return {**update, "completed_nodes": ["initialize"]}


def _explanation_audit(state: CPIPState) -> Dict[str, Any]:
    return explain_and_audit(state, event_type="LangGraphWorkflowEvaluated")


def build_cpip_workflow():
    # Node names get a "_node" suffix: LangGraph forbids a node having the
    # same name as a state key (e.g. "candidate_profile").
    graph = StateGraph(CPIPState)
    graph.add_node("initialize_node", _initialize)
    names = ["initialize_node"]
    for name, step in AGENT_STEPS:
        graph.add_node(f"{name}_node", _node(name, step))
        names.append(f"{name}_node")
    graph.add_node("explanation_audit_node", _node("explanation_audit", _explanation_audit))
    names.append("explanation_audit_node")

    graph.set_entry_point("initialize_node")
    for current, nxt in zip(names, names[1:]):
        graph.add_edge(current, nxt)
    graph.add_edge(names[-1], END)
    return graph.compile()


def run_cpip_workflow(student_id: int) -> dict:
    started = datetime.utcnow().isoformat()
    try:
        # langgraph 0.0.16 uses 2 internal steps per node (node + its edge),
        # so the limit is derived from the node count, not a magic number.
        node_count = len(AGENT_STEPS) + 2   # + initialize + explanation_audit
        final = build_cpip_workflow().invoke(
            {"student_id": student_id, "role": None, "completed_nodes": [], "errors": []},
            config={"recursion_limit": node_count * 2 + 2},
        )
    except Exception as exc:
        return {"success": False, "student_id": student_id,
                "error": f"{type(exc).__name__}: {exc}", "timestamp": started}

    errors = final.get("errors") or []
    return {
        "success": not errors,
        "student_id": student_id,
        "error": errors[0] if errors else None,
        "errors": errors,
        "completed_nodes": final.get("completed_nodes", []),
        "target_role": final.get("target_role"),
        "readiness_scores": final.get("final_scores") or final.get("scores"),
        "skill_gap": final.get("skill_gap"),
        "role_match": final.get("role_match"),
        "job_matches": final.get("job_match"),
        "training_plan": final.get("training"),
        "applications": final.get("applications"),
        "explanation": final.get("explanation"),
        "audit": final.get("audit"),
        "timestamp": started,
    }
