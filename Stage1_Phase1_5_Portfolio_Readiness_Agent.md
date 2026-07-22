## Agentic AI Learning
In agentic AI, agents can evaluate data and classify results based on rules. The Portfolio Readiness Agent checks what evidence is present and what is missing. This classification helps downstream agents understand portfolio quality without re-analyzing the same data.

## Agents Created/Enhanced
Portfolio Readiness Agent - evaluates portfolio evidence completeness and readiness

## Mandatory Inputs
- Candidate portfolio information (GitHub, deployed demo, project explanation)
- Portfolio evidence checklist
- Readiness scoring criteria
- Sample student data
- Python framework
- Requirements.txt

## Feeder Documents Required
- CPIP_Product_Vision_Statement.md
- Stage1_Phase1_4_Skill_Gap_Agent.md
- CPIP_Database_ERD.md

## Implementation Tasks
- [ ] Create portfolio_readiness_agent.py
- [ ] Implement evidence evaluation logic
- [ ] Calculate portfolio readiness score
- [ ] Create API endpoint /portfolio-readiness
- [ ] Test with sample data

## Deliverables
- Portfolio Readiness Agent code
- Working API endpoint
- Test results
- Learning Story HTML
- Repomix snapshot

## AI Execution Prompt
"Build a Portfolio Readiness Agent that evaluates student portfolio evidence. Check for GitHub presence, deployed demo link, project explanation/README, and LinkedIn profile. Calculate a portfolio readiness score (0-100) based on what's present. Identify missing evidence. Create FastAPI routes to expose the agent as HTTP endpoints. Test with sample data."

## Validation Steps
- [ ] Agent code runs without errors
- [ ] Correctly identifies present evidence
- [ ] Correctly identifies missing evidence
- [ ] Portfolio score is accurate
- [ ] API returns 200 OK
- [ ] Works with all sample students

## Evidence Required
- curl output from GET /portfolio-readiness/1 (200 OK)
- Portfolio scores for all 3 students
- Code files: portfolio_readiness_agent.py
- Learning Story HTML
- Repomix snapshot

## Completion Template
- [ ] Agent code written and tested
- [ ] API endpoint tested
- [ ] Learning Story created
- [ ] Repomix created
- [ ] All mandatory sections completed

## Do-Not-Change Warnings
⚠️ Do NOT modify portfolio score format
⚠️ Do NOT skip evidence classification
⚠️ Do NOT hardcode more than 3 students
⚠️ Do NOT claim this guarantees interview success

## Next Phase Readiness
Proceed to Phase 1.6 when Portfolio Readiness Agent is tested and producing valid scores.