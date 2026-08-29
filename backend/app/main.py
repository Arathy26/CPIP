"""
CPIP FastAPI Application
Career & Placement Intelligence Platform
Complete Production Setup
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all routers
from app.routes.resume_management import router as resume_management_router
# from app.routes.student_analysis_endpoints import router as student_analysis_router  # FIXED
from app.routes.health import router as health_router
from app.routes.candidates import router as candidates_router
from app.routes.skill_gap import router as skill_gap_router
from app.routes.portfolio_readiness import router as portfolio_readiness_router
from app.routes.resume_readiness import router as resume_readiness_router
from app.routes.role_matching import router as role_matching_router
from app.routes.interview_readiness import router as interview_readiness_router
from app.routes.training_recommendation import router as training_recommendation_router
from app.routes.admin_market import router as admin_market_router  # Commented temporarily
from app.routes.job_opportunity import router as job_opportunity_router
from app.routes.placement_workflow import router as placement_workflow_router
from app.routes.explanation_audit import router as explanation_audit_router
from app.routes.langgraph_workflow import router as langgraph_router

# Create FastAPI app
app = FastAPI(
    title="CPIP - Career & Placement Intelligence Platform",
    description="Deterministic Agentic AI for student placement readiness",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers with /api prefix
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(candidates_router, prefix="/api", tags=["Candidates"])
app.include_router(skill_gap_router, prefix="/api", tags=["Skill Gap"])
app.include_router(portfolio_readiness_router, prefix="/api", tags=["Portfolio"])
app.include_router(resume_readiness_router, prefix="/api", tags=["Resume"])
app.include_router(role_matching_router, prefix="/api", tags=["Role Matching"])
app.include_router(interview_readiness_router, prefix="/api", tags=["Interview"])
app.include_router(training_recommendation_router, prefix="/api", tags=["Training"])
app.include_router(job_opportunity_router, prefix="/api", tags=["Jobs"])
app.include_router(placement_workflow_router, prefix="/api", tags=["Workflow"])
app.include_router(explanation_audit_router, prefix="/api", tags=["Audit"])
app.include_router(admin_market_router, prefix="/api", tags=["Admin Market"])
app.include_router(resume_management_router, prefix="/api", tags=["Resume Management"])
app.include_router(langgraph_router)
# app.include_router(student_analysis_router, prefix="/api", tags=["Student Analysis"])

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to CPIP — Career & Placement Intelligence Platform",
        "version": "1.0.0",
        "status": "running"
    }

# Health endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "service": "cpip-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)