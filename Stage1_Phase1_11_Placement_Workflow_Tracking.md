# Stage 1 Phase 1.11 — Placement Workflow Tracking

## Objective
The Placement Workflow Agent tracks candidate progress through placement stages: application submitted → screening → shortlisted → interview rounds → selected/rejected → offer. It maintains workflow state and recommends next actions based on current stage.

## Why This Phase Matters
Placement is a journey with multiple stages. Students need clarity on where they are in the process and what action comes next. The Placement Workflow Agent provides this visibility and guidance throughout the placement pipeline.

## Career/Placement Domain Learning
In placement, workflow management is critical. A candidate may be waiting for interview feedback, preparing for technical round, or negotiating offer. Each stage requires different preparation. The Placement Workflow Agent guides students through this journey.

## Agentic AI Learning
In agentic AI, agents can maintain state and recommend next actions based on current state. The Placement Workflow Agent demonstrates stateful decision-making: it knows where the candidate is and what action to take next.

## Agents Created/Enhanced
Placement Workflow Agent - tracks placement stages and recommends next actions

## Mandatory Inputs
- Student ID and profile
- Job applied for
- Current workflow stage
- Interview results (if applicable)
- Offer status

## Feeder Documents Required
- CPIP_Product_Vision_Statement.md
- Stage1_Phase1_10_Job_Opportunity_Matching.md
- CPIP_Interview_and_Placement_Workflow_Guide.md

## Implementation Tasks
- [ ] Create placement_workflow_agent.py
- [ ] Implement workflow stages
- [ ] Define stage transitions
- [ ] Recommend next actions
- [ ] Create API endpoint /placement-workflow
- [ ] Test with sample data

## Deliverables
- Placement Workflow Agent code
- Working API endpoint
- Test results
- Learning Story HTML
- Repomix snapshot

## AI Execution Prompt
"Build a Placement Workflow Agent that tracks placement stages. Input: candidate ID, job, current stage (applied, screening, shortlisted, round1, round2, selected, rejected, offer). Output: current status, next recommended action, timeline estimate. Create FastAPI routes. Test with sample data."

## Validation Steps
- [ ] Agent code runs without errors
- [ ] Stage transitions work correctly
- [ ] Next actions recommended appropriately
- [ ] API returns 200 OK
- [ ] Works with all sample students

## Evidence Required
- curl output from GET /placement-workflow/1 (200 OK)
- Workflow status for all 3 students
- Code files: placement_workflow_agent.py
- Learning Story HTML
- Repomix snapshot

## Completion Template
- [ ] Agent code written and tested
- [ ] API endpoint tested (200 OK)
- [ ] Learning Story created
- [ ] Repomix created
- [ ] All mandatory sections completed

## Do-Not-Change Warnings
⚠️ Do NOT skip workflow stages
⚠️ Do NOT claim workflow predicts outcome
⚠️ Do NOT modify stage definitions without documenting

## Next Phase Readiness
Proceed to Phase 1.12 when Placement Workflow Agent is tested and tracking all stages correctly.