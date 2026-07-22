# Stage 1 Phase 1.7 — Role Matching Agent

## Objective
The Role Matching Agent analyzes a student's profile, skills, readiness scores, and career goals to recommend suitable job roles. It matches students to roles where they have strong skill alignment and readiness, helping them focus applications on realistic opportunities.

## Why This Phase Matters
Without role matching, students apply to unsuitable roles and waste time. The Role Matching Agent identifies which roles are realistic based on actual skill gaps and readiness, so students apply strategically to positions where they have genuine chances of success.

## Career/Placement Domain Learning
In placement, not all roles are suitable for every student. A student strong in frontend should apply for frontend roles, not backend roles. The Role Matching Agent ensures students pursue roles that match their strengths, experience, and readiness level. This increases interview success rates and placement outcomes.

## Agentic AI Learning
In agentic AI, agents can recommend outcomes based on multiple input scores. The Role Matching Agent takes skill gap scores, portfolio scores, resume scores, and interview readiness scores, then uses matching logic to recommend suitable roles. This shows how agents synthesize multiple agent outputs into higher-level recommendations.

## Agents Created/Enhanced
Role Matching Agent - recommends suitable job roles based on student profile and readiness scores

## Mandatory Inputs
- Candidate profile (from Phase 1.3)
- Skill gap scores (from Phase 1.4)
- Portfolio readiness score (from Phase 1.5)
- Resume readiness score (from Phase 1.6)
- Available job roles
- Role requirement criteria

## Feeder Documents Required
- CPIP_Product_Vision_Statement.md
- Stage1_Phase1_6_Resume_Readiness_Agent.md
- CPIP_Agent_Catalog.md

## Implementation Tasks
- [ ] Create role_matching_agent.py
- [ ] Implement role matching logic
- [ ] Calculate role fit scores
- [ ] Create API endpoint /role-match
- [ ] Test with sample data

## Deliverables
- Role Matching Agent code
- Working API endpoint
- Test results
- Learning Story HTML
- Repomix snapshot

## AI Execution Prompt
"Build a Role Matching Agent that recommends suitable job roles. Input: candidate skills, skill gap scores, portfolio score, resume score, and available roles with requirements. Output: recommended roles with fit scores and reasons. Use matching logic: if skill gap < 50, not suitable; if gap < 30, good fit; if all scores > 70, strong fit. Create FastAPI routes. Test with sample data."

## Validation Steps
- [ ] Agent code runs without errors
- [ ] Correctly matches skills to roles
- [ ] Calculates fit scores accurately
- [ ] API returns 200 OK
- [ ] Works with all sample students

## Evidence Required
- curl output from GET /role-match/1 (200 OK)
- Role recommendations for all 3 students
- Code files: role_matching_agent.py
- Learning Story HTML
- Repomix snapshot

## Completion Template
- [ ] Agent code written and tested
- [ ] API endpoint tested (200 OK)
- [ ] Learning Story created
- [ ] Repomix created
- [ ] All mandatory sections completed

## Do-Not-Change Warnings
⚠️ Do NOT modify role fit calculation without documenting changes
⚠️ Do NOT recommend unsuitable roles
⚠️ Do NOT claim this guarantees job offers

## Next Phase Readiness
Proceed to Phase 1.8 when Role Matching Agent is tested and producing valid role recommendations.