"""
Explanation Agent
Turns the REAL outputs of the other agents into plain-language reasons.

Pure function. Every sentence is built from values in the input:
scores, missing skills, missing evidence, weak/unassessed interview
dimensions, top role, job matches, training actions, workflow stage.
A section with no data says "not assessed yet" — it is never shown as 0%.

Overall readiness = average of the scores that exist (missing ones excluded).
Readiness bands (same as the interview agent): >=80 High, >=70 Good, >=60 Fair, <60 Early.
Wording follows CPIP safe-language rules: readiness support, never a guarantee.
"""


def _num(v):
    return v if isinstance(v, (int, float)) else None


def _band(score):
    if score is None:
        return "Not enough data yet"
    if score >= 80:
        return "High readiness - human review recommended before applying"
    if score >= 70:
        return "Good readiness - minor preparation needed"
    if score >= 60:
        return "Fair readiness - moderate preparation recommended"
    return "Early stage - significant preparation needed"


def _join(items, limit=5):
    items = [str(i) for i in items if i]
    if len(items) > limit:
        return ", ".join(items[:limit]) + f" and {len(items) - limit} more"
    return ", ".join(items)


def explanation_agent(agent_outputs):
    """
    Args (all sections optional):
        {
          "candidate_id", "target_role",
          "skill_gap":  {"score", "matched_skills", "missing_skills", "postings_analyzed"},
          "portfolio":  {"score", "evidence_present", "evidence_missing"},
          "resume":     {"score", "sections_missing"},
          "interview":  {"score", "weak_dimensions", "not_assessed_dimensions"},
          "role_match": {"top_role", "fit_score"},
          "job_match":  {"count"},
          "training":   {"count", "first_action"},
          "workflow":   {"applications", "stages"}
        }
    """
    a = agent_outputs or {}
    role = a.get("target_role") or "your target role"
    lines = []
    area_lines = {}   # area -> the sentence that explains its score

    sg = a.get("skill_gap") or {}
    sg_score = _num(sg.get("score"))
    if sg_score is None:
        lines.append(f"Skills: Not assessed yet - no recruiter has posted a job for {role}.")
        area_lines["skill_gap"] = lines[-1]
    else:
        missing = [m["skill"] if isinstance(m, dict) else m for m in (sg.get("missing_skills") or [])]
        text = (f"Skills: You have {len(sg.get('matched_skills') or [])} of "
                f"{len(sg.get('matched_skills') or []) + len(missing)} skills recruiters ask for in {role} "
                f"({sg_score}%, based on {sg.get('postings_analyzed') or 0} posting(s)).")
        if missing:
            text += f" Missing: {_join(missing)}."
        lines.append(text)
        area_lines["skill_gap"] = text

    pf = a.get("portfolio") or {}
    pf_score = _num(pf.get("score"))
    if pf_score is not None:
        text = f"Portfolio: {pf_score}%."
        if pf.get("evidence_present"):
            text += f" Present: {_join(pf['evidence_present'])}."
        if pf.get("evidence_missing"):
            text += f" Missing: {_join(pf['evidence_missing'])}."
        lines.append(text)
        area_lines["portfolio"] = text

    rs = a.get("resume") or {}
    rs_score = _num(rs.get("score"))
    if rs_score is None:
        lines.append("Resume: Not assessed yet - no resume uploaded.")
        area_lines["resume"] = lines[-1]
    else:
        text = f"Resume: {rs_score}%."
        if rs.get("sections_missing"):
            text += f" Needs work: {_join(rs['sections_missing'])}."
        lines.append(text)
        area_lines["resume"] = text

    iv = a.get("interview") or {}
    iv_score = _num(iv.get("score"))
    if iv_score is None:
        lines.append("Interview: Not assessed yet - no mock interview has been recorded by a mentor.")
        area_lines["interview"] = lines[-1]
    else:
        text = f"Interview: {iv_score}% from mentor mock-interview scores."
        if iv.get("weak_dimensions"):
            text += f" Needs work: {_join(d.replace('_', ' ') for d in iv['weak_dimensions'])}."
        if iv.get("not_assessed_dimensions"):
            text += f" Not yet assessed: {_join(d.replace('_', ' ') for d in iv['not_assessed_dimensions'])}."
        lines.append(text)
        area_lines["interview"] = text

    rm = a.get("role_match") or {}
    if rm.get("top_role"):
        lines.append(f"Best-fitting posted role: {rm['top_role']} (skill fit {rm.get('fit_score')}%).")

    jm = a.get("job_match") or {}
    if jm.get("count") is not None:
        lines.append(
            f"Job matches: {jm['count']} open posting(s) match your skills." if jm["count"]
            else "Job matches: No open posting matches your skills yet."
        )

    tr = a.get("training") or {}
    if tr.get("count"):
        lines.append(f"Next step: {tr.get('first_action')} ({tr['count']} action(s) in your plan).")

    wf = a.get("workflow") or {}
    if wf.get("applications"):
        lines.append(f"Applications: {wf['applications']} - stages: {_join(wf.get('stages') or [])}.")

    scores = {"skill_gap": sg_score, "portfolio": pf_score, "resume": rs_score, "interview": iv_score}
    used = {k: v for k, v in scores.items() if v is not None}
    overall = int(round(sum(used.values()) / len(used))) if used else None
    band = _band(overall)
    not_used = [k for k, v in scores.items() if v is None]

    overall_line = (f"Overall readiness: {overall}% from {_join(used.keys())}. {band}."
                    if overall is not None else "Overall readiness: not enough data yet.")
    if not_used and overall is not None:
        overall_line += f" Not included (no data yet): {_join(not_used)}."
    lines.append(overall_line)

    labels = {"skill_gap": "Skills", "portfolio": "Portfolio", "resume": "Resume", "interview": "Interview"}
    breakdown = [
        {"area": k, "label": labels[k], "score": scores[k], "included": scores[k] is not None,
         "basis": area_lines.get(k, "Not assessed yet.")}
        for k in labels
    ]
    formula = (
        f"({' + '.join(str(int(round(v))) for v in used.values())}) / {len(used)} = {overall}%"
        if used else None
    )

    return {
        "candidate_id": a.get("candidate_id"),
        "overall_readiness_score": overall,
        "breakdown": breakdown,
        "formula": formula,
        "method": "Average of the areas that have real data. Areas with no data are left out, not counted as 0.",
        "readiness_band": band,
        "scores_used": used,
        "scores_missing": not_used,
        "explanations": lines,
        "full_explanation": "\n".join(lines),
        "summary": overall_line,
        "disclaimer": "Readiness support only. Final hiring decisions are made by employers.",
    }


def validate_explanation_result(result):
    """Validates explanation result."""
    required_fields = ["candidate_id", "explanations", "full_explanation"]
    missing_fields = [field for field in required_fields if field not in result]
    if missing_fields:
        return {"valid": False, "errors": f"Missing fields: {missing_fields}"}
    return {"valid": True, "message": "Explanation is valid and complete"}
