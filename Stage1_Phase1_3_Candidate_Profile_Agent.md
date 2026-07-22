# Stage 1 Phase 1.3 — Candidate Profile Agent

## Objective
The Candidate Profile Agent reads student data from the STUDENT table 
and creates a structured profile. This structured data will be used by 
other agents to make decisions about student readiness and job matching.

## Why This Phase Matters
If other agents don't have a normalized profile, orchestration couldn't happen. 
Student raw data has more information scattered all over the database. The Candidate 
Profile Agent distinguishes and identifies the required data, normalizes it, and 
passes it to other agents.

## Career/Placement Domain Learning
In placement, data quality determines recommendation quality. If student data 
is scattered and unorganized, agents receive dirty data and produce unclear 
recommendations. A Candidate Profile Agent normalizes raw student data so 
that downstream agents can make accurate readiness and job-matching decisions.

## Agentic AI Learning
In agentic AI, each agent should have one specific responsibility. The Candidate 
Profile Agent's job is to normalize and filter raw student data. This is important 
because data must be cleaned and structured before passing to other agents, 
ensuring they receive consistent, usable input.

## Agents Created/Enhanced
Candidate Profile Agent - normalizes student data from STUDENT table

## Mandatory Inputs
- Candidate Profile Agent design (from Phase 1.2)
- Sample student data (from CPIP_Seed_Data.json)
- FastAPI framework installed
- Python 3.8+
- Requirements.txt with dependencies

## Feeder Documents Required
- CPIP_Product_Vision_Statement.md
- CPIP_Non_Scope_Table.md
- Stage1_Phase1_2_Core_Placement_Data_Model.md
- CPIP_Database_ERD.md
- CPIP_Agentic_AI_Architecture_Pack

## Implementation Tasks
- [x] Create candidate_profile_agent.py
- [x] Implement agent logic to read STUDENT table
- [x] Create API endpoint /candidates
- [x] Test agent with seed data
- [x] Validate normalized output

## Deliverables
- Candidate Profile Agent code (candidate_profile_agent.py)
- Working API endpoints (candidates.py with 2 routes)
- Test results with sample data (all 3 students working)
- Learning Story HTML
- Repomix snapshot

## AI Execution Prompt
"Build a Candidate Profile Agent that reads raw student data and returns a normalized, structured profile. The agent should group scattered fields into logical sections (contact, academics, career, portfolio). Include validation logic. Create FastAPI routes to expose the agent as HTTP endpoints. Test with sample data from CPIP_Seed_Data.json. Ensure all responses are JSON and include validation status."

## Validation Steps
- [x] Agent code runs without errors
- [x] candidate_profile_agent(student_data) transforms data correctly
- [x] Profile structure matches expected output format
- [x] validate_profile() checks all required fields
- [x] GET /candidates/1 returns 200 OK
- [x] GET /candidates returns all 3 candidates
- [x] Response JSON is valid and complete
- [x] Hardcoded sample data is clearly marked as MVP-only

## Evidence Required
- Backend running screenshot (uvicorn startup complete)
- curl output from GET /candidates/1 (200 OK response)
- curl output from GET /candidates (200 OK with all 3 candidates)
- Code files present: candidate_profile_agent.py, candidates.py, main.py updated
- Learning Story HTML file created
- Repomix snapshot created

## Completion Template
**Phase 1.3 Completion Checklist:**
- [x] Agent code written and tested
- [x] API endpoints created and registered in main.py
- [x] Both endpoints tested with curl (200 OK)
- [x] Sample data hardcoded for MVP (marked as temporary)
- [x] Data normalization verified
- [x] Profile validation working
- [x] Learning Story HTML generated
- [x] Repomix snapshot created
- [x] All mandatory sections completed
- [x] Intern can explain agent in 2 minutes

## Do-Not-Change Warnings
⚠️ **CRITICAL:**
- Do NOT modify agent output structure without updating all dependent agents
- Do NOT remove validation logic — it ensures data quality
- Do NOT connect to real database yet — MVP uses sample data intentionally
- Do NOT skip the structured output format — downstream agents depend on it
- Do NOT claim this guarantees placement — it only normalizes data
- Do NOT hardcode more than 3 sample students — test with real database later

## Next Phase Readiness
Proceed to Phase 1.4 when Candidate Profile Agent is tested and producing valid normalized profiles. This phase is COMPLETE and VALIDATED.