# Stage 1 Phase 1.2 — Core Placement Data Model

## Objective
Design the database schema that stores student profiles, skills, jobs, and assessment results. This schema will enable agents to access the data they need to evaluate student readiness, identify skill gaps, and match students with suitable roles.

## Why This Phase Matters
If each agent stores data in its own way (Skill Gap Agent one way, Resume Agent another way), agents cannot work together and the system breaks down. A structured data model ensures all agents use the same data organization, so they can coordinate and build on each other's outputs.

## Career/Placement Domain Learning
In placement, student readiness depends on organizing their information: academic profile, skills, projects, and career goals. A data model structures this information so that CPIP can match student skills with job requirements and recommend suitable roles accurately.
## Agentic AI Learning
In agentic AI, agents need a common data structure so they can cooperate and coordinate. 
Without a proper schema, agents cannot work together because they won't understand each 
other's data formats.

## Agents Created/Enhanced
None yet. This phase designs the data structure that future agents will use.

## Implementation Tasks
- [ ] Design Student entity and fields
- [ ] Design Skill entity and relationships
- [ ] Design Job entity
- [ ] Design Assessment/Readiness entity
- [ ] Design relationship between Student-Skill-Job
- [ ] Create data model diagram
- [ ] Write example data (seed data)

## Deliverables
- Database schema design document
- Entity-relationship diagram
- Example seed data
- README with schema explanation

## Validation Steps
- [ ] Schema correctly represents all CPIP data
- [ ] Relationships between entities are clear
- [ ] Example data can be inserted without errors
- [ ] Schema supports agent data access patterns

## Evidence Required
- Database schema diagram
- Sample seed data output
- Entity-relationship diagram (ERD)

## Learning Story Requirement
After implementation, create: CPIP_Stage1_Phase1_2_Learning_Story.html

## Next Phase Readiness
Proceed to Phase 1.3 only when:
- Database schema is finalized
- Entity-relationship diagram is created
- Sample data is prepared