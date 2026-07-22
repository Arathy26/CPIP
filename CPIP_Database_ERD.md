┌─────────────────────────┐
│      STUDENT            │
├─────────────────────────┤
│ id (PK)                 │
│ name                    │
│ email                   │
│ degree                  │
│ cgpa                    │
│ location                │
│ target_role             │
│ github_link             │
│ linkedin_id             │
│ resume                  │
│ salary_expected         │
└──────────┬──────────────┘
           │ (1)
           │
           ├─────────────── (Many) ┌──────────────────────┐
           │                       │  STUDENT_SKILL       │
           │                       ├──────────────────────┤
           │                       │ id (PK)              │
           │                       │ student_id (FK)  ◄───┤─── STUDENT
           │                       │ skill_id (FK)    ◄───┤─── SKILL
           │                       │ proficiency_level│
           │                       └──────────────────────┘
           │
           │
    ┌──────▼──────────────┐
    │      SKILL          │
    ├─────────────────────┤
    │ id (PK)             │
    │ skill_name          │
    │ category            │
    │ difficulty_level    │
    │ description         │
    └──────────────────────┘


┌──────────────────────────┐
│        JOB               │
├──────────────────────────┤
│ id (PK)                  │
│ job_title                │
│ company_name             │
│ location                 │
│ salary_range             │
│ job_description          │
│ job_type                 │
│ experience_level         │
│ application_deadline     │
│ application_link         │
└──────────┬───────────────┘
           │ (1)
           │
           ├─────────────── (Many) ┌──────────────────────┐
           │                       │  JOB_REQUIREMENT     │
           │                       ├──────────────────────┤
           │                       │ id (PK)              │
           │                       │ job_id (FK)      ◄───┤─── JOB
           │                       │ skill_id (FK)    ◄───┤─── SKILL
           │                       │ is_mandatory         │
           │                       │ years_of_experience  │
           │                       └──────────────────────┘
           │
           │
    ┌──────▼──────────────┐
    │      SKILL          │
    ├─────────────────────┤
    │ id (PK)             │
    │ skill_name          │
    │ category            │
    │ difficulty_level    │
    │ description         │
    └──────────────────────┘


┌─────────────────────────────────┐
│      ASSESSMENT                 │
├─────────────────────────────────┤
│ id (PK)                         │
│ student_id (FK) ◄───────────────┤─── STUDENT
│ skill_gap_score                 │
│ portfolio_readiness_score       │
│ resume_readiness_score          │
│ interview_readiness_score       │
│ assessment_date                 │
└─────────────────────────────────┘


Legend:
PK = Primary Key (unique ID)
FK = Foreign Key (links to another table)
(1) = One
(Many) = Many