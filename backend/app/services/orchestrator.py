"""
CPIP Orchestrator
Runs every deterministic agent for ONE student from REAL data and returns
one shared context (the "shared workflow memory" from the CPIP architecture).

- No hardcoded scores, skills or roles.
- A section with no data is None ("not assessed"), never a fake 0.
- Jobs and role requirements come only from recruiter postings.
- run_full_pipeline() also explains the result, saves an audit record and
  stores a readiness snapshot.
"""

from app.data import seed_data
from app.agents.candidate_profile_agent import candidate_profile_agent
from app.agents.skill_gap_agent import skill_gap_agent
from app.agents.portfolio_readiness_agent import portfolio_readiness_agent
from app.agents.resume_readiness_agent import resume_readiness_agent
from app.agents.interview_readiness_agent import interview_readiness_agent
from app.agents.role_matching_agent import role_matching_agent
from app.agents.job_opportunity_agent import job_opportunity_agent
from app.agents.training_recommendation_agent import training_recommendation_agent
from app.agents.placement_workflow_agent import normalise_stage
from app.agents.explanation_agent import explanation_agent
from app.agents.audit_agent import audit_agent
from app.services.recruiter_matching_agent import MATCHING_RULES


def _portfolio_evidence(student, resume):
    # Imported here to avoid a circular import (route module imports seed_data)
    from app.routes.portfolio_readiness import _resolve_portfolio_evidence
    return _resolve_portfolio_evidence(student, resume)


# ---------------------------------------------------------------------------
# STEP FUNCTIONS — each takes the shared context and returns ONLY the keys it
# adds. The plain orchestrator runs them in order; LangGraph wraps each one
# as a graph node. One implementation, two runners -> identical results.
# ---------------------------------------------------------------------------

def step_load_context(ctx):
    student = seed_data.get_student(ctx["student_id"])
    if not student:
        return {"student": None}
    target_role = ctx.get("role") or student.get("target_role")
    role_data = seed_data.get_role_requirements(target_role) if target_role else None
    return {
        "student": student,
        "target_role": target_role,
        "resume_data": seed_data.get_resume(ctx["student_id"]),
        "role_requirements": role_data,
    }


def step_candidate_profile(ctx):
    return {"candidate_profile": candidate_profile_agent(ctx["student"])}


def step_skill_gap(ctx):
    role_data = ctx.get("role_requirements")
    if not role_data:
        return {"skill_gap": {"score": None, "matched_skills": [], "missing_skills": [], "postings_analyzed": 0}}
    gap = skill_gap_agent(ctx["student"].get("skills", []), role_data["required_skills"])
    demand = {k.lower(): v for k, v in role_data["skill_demand"].items()}
    display = {k.lower(): k for k in role_data["required_skills"]}
    postings = role_data["job_postings_analyzed"]
    return {"skill_gap": {
        "score": gap["gap_score"],
        "matched_skills": [display.get(s, s) for s in gap["matched_skills"]],
        "missing_skills": [
            {"skill": display.get(s, s), "jobs_requiring": demand.get(s),
             "demand_weight": round(demand[s] / postings * 100) if s in demand else None}
            for s in gap["missing_skills"]
        ],
        "postings_analyzed": postings,
    }}


def step_portfolio(ctx):
    portfolio_data, evidence_sources = _portfolio_evidence(ctx["student"], ctx.get("resume_data"))
    return {"portfolio": {**portfolio_readiness_agent(portfolio_data), "evidence_sources": evidence_sources}}


def step_resume(ctx):
    resume = ctx.get("resume_data")
    role_data = ctx.get("role_requirements")
    required = role_data["required_skills"] if role_data else None
    return {"resume": resume_readiness_agent(resume, required_skills=required) if resume else None}


def step_interview(ctx):
    scores, evidence = seed_data.get_latest_interview_scores(ctx["student_id"])
    return {"interview": {**interview_readiness_agent(scores), "evidence": evidence}}


def step_role_match(ctx):
    return {"role_match": role_matching_agent(
        {"candidate_id": ctx["student_id"], "skills": ctx["student"].get("skills", []),
         "target_role": ctx.get("target_role")},
        role_requirements=seed_data.get_all_target_roles(),
    )}


def step_job_match(ctx):
    return {"job_match": job_opportunity_agent(
        {"candidate_id": ctx["student_id"], "skills": ctx["student"].get("skills", [])},
        job_opportunities=seed_data.get_all_jobs(),
    )}


def step_training(ctx):
    resume = ctx.get("resume")
    interview = ctx["interview"]
    return {"training": training_recommendation_agent({
        "skill_gap": ctx["skill_gap"],
        "portfolio": {"score": ctx["portfolio"]["portfolio_score"],
                      "evidence_missing": ctx["portfolio"]["evidence_missing"]},
        "resume": ({"score": resume["resume_score"], "improvement_tips": resume["improvement_tips"]}
                   if resume else {"score": None, "improvement_tips": []}),
        "interview": {"score": interview["interview_readiness_score"],
                      "weak_dimensions": interview["weak_dimensions"],
                      "not_assessed_dimensions": interview["not_assessed_dimensions"]},
        "target_role": ctx.get("target_role"),
    })}


def step_applications(ctx):
    return {"applications": seed_data.get_applications_for_student(ctx["student_id"])}


def step_scores(ctx):
    resume = ctx.get("resume")
    return {"scores": {
        "skill_gap_score": ctx["skill_gap"]["score"],
        "portfolio_score": ctx["portfolio"]["portfolio_score"],
        "resume_score": resume["resume_score"] if resume else None,
        "interview_readiness_score": ctx["interview"]["interview_readiness_score"],
    }}


# Order matters: later steps read what earlier steps wrote.
AGENT_STEPS = [
    ("candidate_profile", step_candidate_profile),
    ("skill_gap", step_skill_gap),
    ("portfolio_readiness", step_portfolio),
    ("resume_readiness", step_resume),
    ("interview_readiness", step_interview),
    ("role_matching", step_role_match),
    ("job_opportunity_matching", step_job_match),
    ("training_recommendation", step_training),
    ("placement_workflow", step_applications),
    ("aggregate_scores", step_scores),
]


def collect_agent_outputs(student_id, role=None):
    """Run all readiness agents for one student. Returns None if student not found."""
    ctx = {"student_id": student_id, "role": role}
    ctx.update(step_load_context(ctx))
    if not ctx["student"]:
        return None
    for _, step in AGENT_STEPS:
        ctx.update(step(ctx))
    return ctx


def explain(ctx):
    """Build the explanation from a collect_agent_outputs() context."""
    top = (ctx["role_match"].get("recommended_roles") or [None])[0]
    actions = ctx["training"]["training_actions"]
    return explanation_agent({
        "candidate_id": ctx["student_id"],
        "target_role": ctx["target_role"],
        "skill_gap": ctx["skill_gap"],
        "portfolio": {"score": ctx["portfolio"]["portfolio_score"],
                      "evidence_present": ctx["portfolio"]["evidence_present"],
                      "evidence_missing": ctx["portfolio"]["evidence_missing"]},
        "resume": ({"score": ctx["resume"]["resume_score"],
                    "sections_missing": ctx["resume"]["sections_missing"]} if ctx["resume"] else {}),
        "interview": {"score": ctx["interview"]["interview_readiness_score"],
                      "weak_dimensions": ctx["interview"]["weak_dimensions"],
                      "not_assessed_dimensions": ctx["interview"]["not_assessed_dimensions"]},
        "role_match": {"top_role": top["role"], "fit_score": top["fit_score"]} if top else {},
        "job_match": {"count": ctx["job_match"]["recommendation_count"]},
        "training": {"count": len(actions), "first_action": actions[0]["action"] if actions else None},
        "workflow": {"applications": len(ctx["applications"]),
                     "stages": [normalise_stage(a.get("status")) for a in ctx["applications"]]},
    })


def explain_and_audit(ctx, event_type):
    """Explanation + saved audit record + readiness snapshot for a finished context."""
    explanation = explain(ctx)
    scores = {**ctx["scores"], "overall_readiness": explanation["overall_readiness_score"]}

    record = audit_agent({
        "candidate_id": ctx["student_id"],
        "event_type": event_type,
        "scores": scores,
        "agent_outputs": {
            "skill_gap": ctx["skill_gap"],
            "portfolio_evidence_missing": ctx["portfolio"]["evidence_missing"],
            "resume_sections_missing": ctx["resume"]["sections_missing"] if ctx["resume"] else None,
            "interview_dimensions_assessed": ctx["interview"]["dimensions_assessed"],
            "top_roles": [(r["role"], r["fit_score"]) for r in ctx["role_match"]["recommended_roles"]],
            "job_matches": [(j["job_id"], j["fit_score"]) for j in ctx["job_match"]["all_matches"]],
            "training_actions": len(ctx["training"]["training_actions"]),
        },
        "recommendation": explanation["readiness_band"],
        "decision_reason": explanation["full_explanation"],
        "rules_version": MATCHING_RULES["version"],
    })
    saved = seed_data.save_audit_record(record)
    seed_data.update_readiness_scores(ctx["student_id"], scores)
    return {
        "explanation": explanation,
        "audit": {"audit_id": saved["audit_id"], "audit_status": saved["audit_status"]},
        "final_scores": scores,
    }


def run_full_pipeline(student_id: int, event_type: str = "FullPipelineEvaluated"):
    """Run every agent, explain, save an audit record and a readiness snapshot."""
    ctx = collect_agent_outputs(student_id)
    if ctx is None:
        return {"error": "Student not found"}

    done = explain_and_audit(ctx, event_type)
    return {
        "student_id": student_id,
        "context": {k: v for k, v in ctx.items() if k not in ("student", "resume_data")},
        "explanation": done["explanation"],
        "audit": done["audit"],
        "scores": done["final_scores"],
    }
