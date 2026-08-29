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
    pool_pre_ping=True,        # ← tests connection before using it
    pool_recycle=300,          # ← recycles connections every 5 minutes
    pool_size=5,               # ← max 5 connections
    max_overflow=10            # ← allow 10 extra connections under load
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
    print("Database tables created successfully!")

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Index
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


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=True)
    job_title = Column(String)           # ← FIXED: was 'title'
    company_name = Column(String)        # ← FIXED: was 'company'
    location = Column(String, index=True)
    required_skills = Column(Text)       # ← FIXED: was 'skills_required'
    preferred_skills = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    min_cgpa = Column(Float, default=0)
    min_readiness = Column(Integer, default=0)
    experience_level = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    posted_date = Column(String, nullable=True)


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
    job_id = Column(String)
    status = Column(String, default="applied")
    fit_score = Column(Float, default=0)
    applied_date = Column(DateTime, default=datetime.utcnow)
    shortlisted_date = Column(DateTime, nullable=True)
    interviewed_date = Column(DateTime, nullable=True)
    offer_date = Column(DateTime, nullable=True)
    recruiter_notes = Column(Text, nullable=True)


class JobDescriptionCacheModel(Base):
    __tablename__ = "job_description_cache"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=True)          # ← FIXED: added
    company = Column(String, nullable=True)        # ← FIXED: added
    description = Column(Text)
    skills_extracted = Column(Text)               # ← FIXED: was 'skills'
    cached_at = Column(DateTime, default=datetime.utcnow)


class JobSkillsCacheModel(Base):
    __tablename__ = "job_skills_cache"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True)
    skill = Column(String)
    cached_at = Column(DateTime, default=datetime.utcnow)


class MarketSkillCacheModel(Base):
    __tablename__ = "market_skill_cache"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, default="india", index=True)
    target_role = Column(String, index=True)
    skill_name = Column(String, index=True)
    demand_weight = Column(Integer, default=0)
    postings_requiring_it = Column(Integer, default=0)
    cached_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_loc_role_skill', 'location', 'target_role', 'skill_name', unique=True),
    )


class RoleCacheMetadataModel(Base):
    __tablename__ = "role_cache_metadata"

    id = Column(Integer, primary_key=True, index=True)
    last_cache_update = Column(DateTime, default=datetime.utcnow)
    cache_version = Column(Integer, default=1)


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