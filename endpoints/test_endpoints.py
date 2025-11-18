from fastapi import APIRouter, HTTPException
from schemas import TestRequest, TestResponse
from agents import run_multi_agent_system, extract_metadata
import os

router = APIRouter(prefix="/test", tags=["testing"])

@router.post("", response_model=TestResponse)
async def test_endpoint(request: TestRequest):
    """Testing endpoint for all agents"""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Please set it in .env file"
            )
        
        results = {}
        
        if request.test_type == "basic" or request.test_type == "all":
            # Test basic multi-agent system
            results["multi_agent"] = run_multi_agent_system(
                "Summarize the key benefits of AI in healthcare"
            )
        
        if request.test_type == "metadata" or request.test_type == "all":
            # Test metadata extractor
            results["metadata_extractor"] = extract_metadata(request.content)
        
        if request.test_type == "custom":
            # Test with custom content
            results["multi_agent"] = run_multi_agent_system(request.content)
            results["metadata_extractor"] = extract_metadata(request.content)
        
        return TestResponse(
            status="success",
            test_type=request.test_type,
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
