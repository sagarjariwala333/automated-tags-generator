from fastapi import APIRouter
from schemas import HealthResponse
import os

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Check system health and configuration"""
    return HealthResponse(
        status="healthy",
        gemini_configured=bool(os.getenv("GOOGLE_API_KEY")),
        available_endpoints=[
            "GET /",
            "POST /agent/execute",
            "POST /agent/metadata",
            "POST /data/github/readme",
            "GET /data/github/readme/{owner}/{repo}",
            "POST /workflow/github/analyze",
            "GET /workflow/github/analyze/{owner}/{repo}",
            "POST /test",
            "GET /health"
        ]
    )

@router.get("/")
def hello_world():
    """Root endpoint"""
    return {"message": "Hello World - Multi-Agent System"}
