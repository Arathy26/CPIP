from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.candidates import router as candidates_router
from app.routes.skill_gap import router as skill_gap_router
from app.routes.portfolio_readiness import router as portfolio_readiness_router
from app.routes.resume_readiness import router as resume_readiness_router
from app.routes.role_matching import router as role_matching_router
from app.routes.interview_readiness import router as interview_readiness_router
from app.routes.training_recommendation import router as training_recommendation_router
from app.routes.job_opportunity import router as job_opportunity_router
from app.routes.placement_workflow import router as placement_workflow_router
from app.routes.explanation_audit import router as explanation_audit_router

app = FastAPI(title="CPIP", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(candidates_router)
app.include_router(skill_gap_router)
app.include_router(portfolio_readiness_router)
app.include_router(resume_readiness_router)
app.include_router(role_matching_router)
app.include_router(interview_readiness_router)
app.include_router(training_recommendation_router)
app.include_router(job_opportunity_router)
app.include_router(placement_workflow_router)
app.include_router(explanation_audit_router)

@app.get("/")
def root():
    return {"message": "Welcome to CPIP — Career & Placement Intelligence Platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)