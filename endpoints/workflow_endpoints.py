from fastapi import APIRouter, HTTPException
from schemas.simple_workflow_schemas import SimpleAnalysisRequest, SimpleAnalysisResponse
from workflows import run_simple_analysis_workflow
import os
from tool.json_response import JsonResponse

router = APIRouter(prefix="/workflow", tags=["workflows"])

@router.post("/simple/analyze", response_model=SimpleAnalysisResponse)
async def simple_analysis_workflow(request: SimpleAnalysisRequest):
    """
    Simple Analysis Workflow (LangGraph - 4 Agents)
    
    This workflow demonstrates LangGraph with 4 connected agents:
    1. Data Collector Agent (collector) - Fetches README from GitHub
    2. Metadata Extractor Agent (metadata) - Extracts metadata from content
    3. Tag Candidate Agent (candidate) - Generates candidate tags
    4. Tag Similarity Agent (similarity) - Calculates cosine similarity using embeddings
    
    Workflow Graph:
    collector -> metadata -> candidate -> similarity -> END
    
    Example:
    ```json
    {
        "owner": "facebook",
        "repo": "react"
    }
    ```
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Please set it in .env file"
            )
        
        result = run_simple_analysis_workflow(request.owner, request.repo)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Workflow failed")
            )
        
        return SimpleAnalysisResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simple/analyze/{owner}/{repo}", response_model=SimpleAnalysisResponse)
async def simple_analysis_workflow_path(owner: str, repo: str):
    """
    Simple Analysis Workflow (GET method with path parameters)
    
    Alternative endpoint using path parameters instead of request body.
    
    Workflow Graph:
    collector -> metadata -> candidate -> similarity -> END
    
    Example: GET /workflow/simple/analyze/facebook/react
    """
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Please set it in .env file"
            )
        
        result = run_simple_analysis_workflow(owner, repo)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Workflow failed")
            )
        
        response = JsonResponse.success_response(data=result.get("tag_critic", {}).get("tags", []))
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
