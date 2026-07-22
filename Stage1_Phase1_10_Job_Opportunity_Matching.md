# Stage 1 Phase 1.10 — Job Opportunity Matching

## Objective
The Job Opportunity Agent matches students to suitable job openings by comparing student profiles (skills, readiness scores, target role) with job requirements (required skills, preferred skills, eligibility). It produces job fit scores and eligibility assessments.

## Why This Phase Matters
Students know their readiness but don't know which actual job openings are suitable. The Job Opportunity Agent bridges readiness assessment and real job matching, helping students apply strategically.

## Career/Placement Domain Learning
In placement, job matching is not only keyword matching. A student may have some skills but be ineligible due to academic criteria. The Job Opportunity Agent evaluates skill fit AND eligibility to determine if a job is realistic.

## Agentic AI Learning
In agentic AI, agents can match complex entities by evaluating multiple criteria. The Job Opportunity Agent compares student profiles with job requirements across skill match, eligibility, and readiness thresholds.

## Agents Created/Enhanced
Job Opportunity Agent - matches students to job openings based on fit and eligibility

## Mandatory Inputs
- Candidate profile and readiness scores
- Job openings with requirements
- Required skills and preferred skills
- Eligibility criteria (CGPA, degree, etc.)
- Job fit thresholds

## Feeder Documents Required
- CPIP_Product_Vision_Statement.md
- Stage1_Phase1_9_Training_Recommendation_Agent.md
- CPIP_Employer_and_Job_Demand_Guide.md

## Implementation Tasks
- [ ] Create job_opportunity_agent.py
- [ ] Implement skill matching logic
- [ ] Check eligibility criteria
- [ ] Calculate fit scores
- [ ] Create API endpoint /job-match
- [ ] Test with sample jobs

## Deliverables
- Job Opportunity Agent code
- Working API endpoint
- Test results
- Learning Story HTML
- Repomix snapshot

## AI Execution Prompt
"Build a Job Opportunity Agent that matches students to jobs. Input: candidate skills, readiness scores, job requirements (required skills, preferred, eligibility). Output: matching jobs with fit scores, eligibility status, skill gaps. Logic: match required skills, bonus for preferred, check eligibility. Create FastAPI routes. Test with sample data."

## Validation Steps
- [ ] Agent code runs without errors
- [ ] Correctly matches skills to jobs
- [ ] Evaluates eligibility accurately
- [ ] API returns 200 OK
- [ ] Works with all sample students

## Evidence Required
- curl output from GET /job-match/1 (200 OK)
- Job matches for all 3 students
- Code files: job_opportunity_agent.py
- Learning Story HTML
- Repomix snapshot

## Completion Template
- [ ] Agent code written and tested
- [ ] API endpoint tested (200 OK)
- [ ] Learning Story created
- [ ] Repomix created
- [ ] All mandatory sections completed

## Do-Not-Change Warnings
⚠️ Do NOT modify fit calculation without documenting
⚠️ Do NOT skip eligibility checks
⚠️ Do NOT claim job guarantee

## Next Phase Readiness
Proceed to Phase 1.11 when Job Opportunity Agent is tested and producing valid job matches.