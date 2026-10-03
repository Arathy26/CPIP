import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cpip_user:password@localhost:5432/cpip"
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    _add_missing_columns()
    print("Database tables created successfully!")


def _add_missing_columns():
    """
    create_all() creates NEW tables but never adds NEW columns to tables
    that already exist. This adds any column defined on a model but missing
    in the real database. Additive only: it never drops or alters data.
    """
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type = col.type.compile(dialect=engine.dialect)
                    conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {col.name} {col_type}'))
                    print(f"Added missing column {table.name}.{col.name}")

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from datetime import datetime


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)
    degree = Column(String, default="B.Tech CS")
    cgpa = Column(Float, default=0)
    location = Column(String, default="Remote", index=True)
    target_role = Column(String, nullable=True)
    github_link = Column(String, nullable=True)
    linkedin_id = Column(String, nullable=True)
    deployed_demo_link = Column(String, nullable=True)   # student-entered portfolio evidence
    project_readme_link = Column(String, nullable=True)  # student-entered portfolio evidence
    resume = Column(String, nullable=True)
    resume_json = Column(Text, nullable=True)
    salary_expected = Column(Float, default=0)
    skills = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)


class ReadinessScoreModel(Base):
    __tablename__ = "readiness_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    skill_gap_score = Column(Float, default=0)
    portfolio_score = Column(Float, default=0)
    resume_score = Column(Float, default=0)
    interview_readiness_score = Column(Float, default=0)
    overall_readiness = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobPostingModel(Base):
    """
    Recruiter-posted jobs — the single source of truth for job data in CPIP.
    No external APIs. Recruiters post directly (single form or bulk upload).
    """
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company_name = Column(String)
    location = Column(String, index=True)
    required_skills = Column(Text, nullable=True)   # JSON array
    preferred_skills = Column(Text, nullable=True)  # JSON array
    description = Column(Text, nullable=True)
    min_cgpa = Column(Float, default=0)
    experience_level = Column(String, default="Fresher")
    employment_type = Column(String, default="Full-Time")
    salary_range = Column(String, nullable=True)
    posted_by = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InterviewAssessmentModel(Base):
    """
    Mock-interview results recorded by a human assessor (mentor / trainer /
    placement officer). This is the ONLY source of interview scores in CPIP.
    A dimension left empty (NULL) means "not assessed in this session".
    """
    __tablename__ = "interview_assessments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True, nullable=False)
    aptitude_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    project_explanation_score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    assessed_by = Column(String, nullable=False)
    assessed_at = Column(DateTime, default=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    event_type = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobApplicationModel(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    job_id = Column(Integer, ForeignKey("job_postings.id"))
    status = Column(String, default="applied")
    fit_score = Column(Float, default=0)
    applied_date = Column(DateTime, default=datetime.utcnow)
    shortlisted_date = Column(DateTime, nullable=True)
    interviewed_date = Column(DateTime, nullable=True)
    offer_date = Column(DateTime, nullable=True)
    recruiter_notes = Column(Text, nullable=True)
    updated_by = Column(String, nullable=True)   # human who last moved the stage
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecruiterModel(Base):
    __tablename__ = "recruiters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    company = Column(String)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentRoleHistoryModel(Base):
    __tablename__ = "student_role_history"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    previous_role = Column(String, nullable=True)
    new_role = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)


class ResumeModel(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), index=True)
    file_path = Column(String)
    file_name = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    resume_json = Column(Text, nullable=True)
    extraction_status = Column(String, default="pending")
    extraction_error = Column(String, nullable=True)
    is_selected = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)