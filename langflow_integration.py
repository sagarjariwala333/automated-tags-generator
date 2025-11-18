from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Literal
from multi_agent_system import run_multi_agent_system, extract_metadata
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Multi-Agent System with Langflow",
    description="AI-powered multi-agent system using Google Gemini",
    version="1.0.0"
)

# Request Models
class TaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=5000, description="Task to be processed by the multi-agent system")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "Research AI trends in 2024, write a summary, and review it"
            }
        }

class MetadataRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Content to extract metadata from")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Artificial Intelligence is revolutionizing healthcare with predictive diagnostics and personalized treatment plans."
            }
        }

class TestRequest(BaseModel):
    test_type: Literal["basic", "metadata", "all", "custom"] = Field(
        default="basic",
        description="Type of test to run"
    )
    content: str = Field(
        default="AI and machine learning are transforming industries worldwide.",
        description="Custom content for testing"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_type": "all",
                "content": "AI and machine learning are transforming industries worldwide."
            }
        }

# Response Models
class TaskResponse(BaseModel):
    result: str = Field(..., description="Result from the multi-agent system")
    status: str = Field(..., description="Status of the operation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "result": "=== RESEARCH AGENT ===\n...",
                "status": "success"
            }
        }

class MetadataResponse(BaseModel):
    title: Optional[str] = Field(None, description="Main title or topic")
    keywords: Optional[List[str]] = Field(None, description="List of relevant keywords")
    category: Optional[str] = Field(None, description="Primary category")
    summary: Optional[str] = Field(None, description="Brief summary")
    entities: Optional[List[str]] = Field(None, description="Important entities")
    sentiment: Optional[str] = Field(None, description="Overall sentiment")
    language: Optional[str] = Field(None, description="Detected language")
    word_count: Optional[int] = Field(None, description="Approximate word count")
    raw_response: Optional[str] = Field(None, description="Raw response if JSON parsing fails")
    error: Optional[str] = Field(None, description="Error message if any")

class MetadataResponseWrapper(BaseModel):
    status: str = Field(..., description="Status of the operation")
    metadata: Dict[str, Any] = Field(..., description="Extracted metadata")

class TestResponse(BaseModel):
    status: str = Field(..., description="Status of the test")
    test_type: str = Field(..., description="Type of test executed")
    results: Dict[str, Any] = Field(..., description="Test results")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    gemini_configured: bool = Field(..., description="Whether Gemini API is configured")
    available_endpoints: List[str] = Field(..., description="List of available endpoints")

@app.get("/")
def hello_world():
    return {"message": "Hello World - Multi-Agent System"}

@app.post("/agent/execute", response_model=TaskResponse)
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

@app.post("/agent/metadata", response_model=MetadataResponseWrapper)
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

@app.post("/test", response_model=TestResponse)
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

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        gemini_configured=bool(os.getenv("GOOGLE_API_KEY")),
        available_endpoints=[
            "GET /",
            "POST /agent/execute",
            "POST /agent/metadata",
            "POST /test",
            "GET /health"
        ]
    )
