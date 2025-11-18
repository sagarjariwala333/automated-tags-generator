from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

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
