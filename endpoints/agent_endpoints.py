from fastapi import APIRouter, HTTPException
from schemas import TaskRequest, TaskResponse, MetadataRequest, MetadataResponseWrapper
from agents import run_multi_agent_system, extract_metadata
import os

router = APIRouter(prefix="/agent", tags=["agents"])

@router.post("/execute", response_model=TaskResponse)
async def execute_agent_task(request: TaskRequest):
    """Execute a task using the multi-agent system"""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Please set it in .env file"
            )
        
        result = run_multi_agent_system(request.task)
        return TaskResponse(result=result, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata", response_model=MetadataResponseWrapper)
async def extract_metadata_endpoint(request: MetadataRequest):
    """Extract metadata from content using Metadata Extractor Agent"""
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not configured. Please set it in .env file"
            )
        
        metadata = extract_metadata(request.content)
        return MetadataResponseWrapper(
            status="success",
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
