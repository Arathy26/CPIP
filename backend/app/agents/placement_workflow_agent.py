"""
Placement Workflow Agent
Tracks ONE application (student + job) through the placement workflow.

Stages and order come from the CPIP Interview & Placement Workflow Guide.
Humans (placement officer / recruiter) move stages. This agent only:
  1. validates that a requested move is allowed (TRANSITIONS)
  2. describes the current stage and the next best action
Pure function: no database, no LLM, no invented timelines.
"""

# Main path, in order
MAIN_PATH = [
    "recommended", "under_review", "applied", "shortlisted",
    "round_1_scheduled", "round_1_completed", "technical_round",
    "hr_round", "selected", "offered", "joined",
]
SIDE_STAGES = ["rejected", "on_hold"]
ALL_STAGES = MAIN_PATH + SIDE_STAGES
TERMINAL = {"rejected", "joined"}

STAGE_LABELS = {
    "recommended": "Recommended", "under_review": "Under Review", "applied": "Applied",
    "shortlisted": "Shortlisted", "round_1_scheduled": "Round 1 Scheduled",
    "round_1_completed": "Round 1 Completed", "technical_round": "Technical Round",
    "hr_round": "HR Round", "selected": "Selected", "offered": "Offered",
    "joined": "Joined", "rejected": "Rejected", "on_hold": "On Hold",
}

_EXIT = ["rejected", "on_hold"]

# Allowed moves (documented rule). Companies differ, so some rounds can be skipped.
TRANSITIONS = {
    "recommended":       ["under_review", "applied"] + _EXIT,
    "under_review":      ["applied"] + _EXIT,
    "applied":           ["shortlisted"] + _EXIT,
    "shortlisted":       ["round_1_scheduled", "technical_round", "hr_round"] + _EXIT,
    "round_1_scheduled": ["round_1_completed"] + _EXIT,
    "round_1_completed": ["technical_round", "hr_round", "selected"] + _EXIT,
    "technical_round":   ["hr_round", "selected"] + _EXIT,
    "hr_round":          ["selected"] + _EXIT,
    "selected":          ["offered"] + _EXIT,
    "offered":           ["joined"] + _EXIT,
    # On hold can resume at any active stage after the application exists
    "on_hold":           ["applied", "shortlisted", "round_1_scheduled", "round_1_completed",
                          "technical_round", "hr_round", "selected", "offered", "rejected"],
    "rejected":          [],
    "joined":            [],
}


def normalise_stage(stage):
    """'Round 1 Scheduled' / 'round-1-scheduled' -> 'round_1_scheduled'."""
    if not stage:
        return None
    return str(stage).strip().lower().replace("-", "_").replace(" ", "_")


def validate_transition(current_stage, new_stage):
    current = normalise_stage(current_stage)
    new = normalise_stage(new_stage)
    if new not in ALL_STAGES:
        return False, f"Unknown stage '{new_stage}'. Valid stages: {', '.join(ALL_STAGES)}"
    if current not in TRANSITIONS:
        return False, f"Current stage '{current_stage}' is not a valid stage"
    if current in TERMINAL:
        return False, f"Application is already {STAGE_LABELS[current]}; no further moves allowed"
    if new not in TRANSITIONS[current]:
        allowed = ", ".join(TRANSITIONS[current])
        return False, f"Cannot move from {STAGE_LABELS[current]} to {STAGE_LABELS[new]}. Allowed: {allowed}"
    return True, "Allowed"


def _next_action(stage, missing_skills):
    gap = f" Focus on missing required skills: {', '.join(missing_skills)}." if missing_skills else ""
    actions = {
        "recommended": "Review this recommendation with a mentor and decide whether to apply." + gap,
        "under_review": "Placement officer is reviewing. Keep resume and portfolio links up to date.",
        "applied": "Wait for the recruiter's screening decision." + gap,
        "shortlisted": "Prepare for interview rounds: practise explaining your projects." + gap,
        "round_1_scheduled": "Prepare for Round 1 (aptitude/screening).",
        "round_1_completed": "Await the Round 1 result; prepare for the technical round." + gap,
        "technical_round": "Prepare for the technical interview." + gap,
        "hr_round": "Prepare for the HR round: communication, motivation, role awareness.",
        "selected": "Await the offer from the employer.",
        "offered": "Review the offer with your placement officer before accepting.",
        "joined": "Placement complete.",
        "rejected": "Review feedback with a mentor and apply to other matching roles." + gap,
        "on_hold": "Decision pending with the employer. Continue applying to other roles.",
    }
    return actions[stage]


def placement_workflow_agent(workflow_data):
    """
    Args:
        workflow_data: {"student_id", "application_id", "job_id", "job_title",
                        "current_stage", "missing_required_skills": [...]}
                       current_stage None/empty = student has not applied.
    Returns:
        Dictionary describing the stage and next action.
    """
    data = workflow_data or {}
    stage = normalise_stage(data.get("current_stage"))
    base = {
        "student_id": data.get("student_id"),
        "application_id": data.get("application_id"),
        "job_id": data.get("job_id"),
        "job_title": data.get("job_title"),
    }

    if not stage:
        return {**base, "current_stage": None, "stage_label": "Not Applied",
                "step": None, "is_terminal": False, "allowed_next_stages": [],
                "next_action": "Apply to a job that matches your skills.",
                "recommendation": "No application yet."}

    if stage not in ALL_STAGES:
        return {**base, "current_stage": stage, "stage_label": "Unknown stage",
                "step": None, "is_terminal": False, "allowed_next_stages": [],
                "next_action": "Stage is not recognised. A placement officer must correct it.",
                "recommendation": f"Unrecognised stage '{stage}'."}

    step = (f"Step {MAIN_PATH.index(stage) + 1} of {len(MAIN_PATH)}"
            if stage in MAIN_PATH else None)
    next_action = _next_action(stage, data.get("missing_required_skills") or [])

    return {
        **base,
        "current_stage": stage,
        "stage_label": STAGE_LABELS[stage],
        "step": step,
        "is_terminal": stage in TERMINAL,
        "allowed_next_stages": TRANSITIONS[stage],
        "next_action": next_action,
        "recommendation": f"Current: {STAGE_LABELS[stage]}. Next: {next_action}",
    }


def validate_workflow_result(result):
    """Validates workflow tracking result."""
    required_fields = ["student_id", "current_stage", "next_action"]
    missing_fields = [field for field in required_fields if field not in result]

    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}

    return {"valid": True, "message": "Placement workflow tracking is valid and complete"}
