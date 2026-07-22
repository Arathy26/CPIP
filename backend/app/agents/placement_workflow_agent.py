"""
Placement Workflow Agent
Tracks candidate placement journey through different stages
"""

def placement_workflow_agent(workflow_data):
    """
    Tracks placement workflow and recommends next actions.
    
    Args:
        workflow_data: Dictionary with workflow info
        {
            "student_id": 1,
            "job_applied": "Junior Full Stack Developer",
            "current_stage": "shortlisted",
            "interview_rounds_completed": 0,
            "application_date": "2026-07-15",
            "last_update": "2026-07-18"
        }
        
    Returns:
        Dictionary with workflow status and next action
    """
    
    # Define workflow stages
    WORKFLOW_STAGES = [
        "not_applied",
        "applied",
        "screening",
        "shortlisted",
        "technical_round",
        "hr_round",
        "selected",
        "rejected",
        "offer_received"
    ]
    
    current_stage = workflow_data.get("current_stage", "not_applied")
    student_id = workflow_data.get("student_id")
    job_applied = workflow_data.get("job_applied", "Unknown")
    
    # Map stages to actions
    STAGE_ACTIONS = {
        "not_applied": {
            "status": "Not Started",
            "description": "No application submitted",
            "next_action": "Apply to job opening",
            "timeline": "Immediate"
        },
        "applied": {
            "status": "Under Review",
            "description": "Application submitted, waiting for screening",
            "next_action": "Wait for screening feedback (2-3 days)",
            "timeline": "2-3 days"
        },
        "screening": {
            "status": "In Screening",
            "description": "Resume under review by HR",
            "next_action": "Prepare for technical screening",
            "timeline": "1-2 days"
        },
        "shortlisted": {
            "status": "Shortlisted",
            "description": "Selected for interview rounds",
            "next_action": "Prepare for technical interview",
            "timeline": "Immediate - 3 days"
        },
        "technical_round": {
            "status": "Technical Interview Scheduled",
            "description": "Preparing for or attending technical round",
            "next_action": "Complete technical interview",
            "timeline": "1-2 days"
        },
        "hr_round": {
            "status": "HR Round Scheduled",
            "description": "Passed technical, HR round pending",
            "next_action": "Prepare HR round (communication, motivation)",
            "timeline": "1-2 days"
        },
        "selected": {
            "status": "Selected",
            "description": "Candidate selected, awaiting offer",
            "next_action": "Wait for offer letter",
            "timeline": "2-5 days"
        },
        "offer_received": {
            "status": "Offer Received",
            "description": "Offer received from employer",
            "next_action": "Review and accept/negotiate offer",
            "timeline": "3-5 days"
        },
        "rejected": {
            "status": "Not Selected",
            "description": "Application rejected at this stage",
            "next_action": "Apply to other opportunities",
            "timeline": "Immediate"
        }
    }
    
    # Get current stage details
    if current_stage in STAGE_ACTIONS:
        stage_info = STAGE_ACTIONS[current_stage]
    else:
        stage_info = STAGE_ACTIONS["not_applied"]
        current_stage = "not_applied"
    
    # Determine stage progress
    current_index = WORKFLOW_STAGES.index(current_stage) if current_stage in WORKFLOW_STAGES else 0
    total_stages = len(WORKFLOW_STAGES)
    progress_percentage = int((current_index / total_stages) * 100)
    
    return {
        "student_id": student_id,
        "job_applied": job_applied,
        "current_stage": current_stage,
        "stage_status": stage_info["status"],
        "stage_description": stage_info["description"],
        "next_action": stage_info["next_action"],
        "timeline_estimate": stage_info["timeline"],
        "overall_progress": f"{progress_percentage}% through placement workflow",
        "recommendation": f"Current: {stage_info['status']}. Action: {stage_info['next_action']}"
    }


def validate_workflow_result(result):
    """
    Validates workflow tracking result.
    
    Args:
        result: The output from placement_workflow_agent()
        
    Returns:
        Dictionary with validation status
    """
    
    required_fields = [
        "student_id", "current_stage", "next_action"
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        return {
            "valid": False,
            "errors": f"Missing fields: {missing_fields}"
        }
    
    return {
        "valid": True,
        "message": "Placement workflow tracking is valid and complete"
    }