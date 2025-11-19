from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SimpleAnalysisRequest(BaseModel):
    owner: str = Field(..., min_length=1, description="GitHub repository owner")
    repo: str = Field(..., min_length=1, description="GitHub repository name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "owner": "facebook",
                "repo": "react"
            }
        }

class SimpleAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether the workflow completed successfully")
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    workflow: str = Field(..., description="Workflow name")
    steps_completed: List[str] = Field(..., description="List of completed workflow steps")
    readme_content: Dict[str, Any] = Field(..., description="README content information")
    metadata: Dict[str, Any] = Field(..., description="Extracted metadata")
    candidate_tags: Optional[Dict[str, Any]] = Field(None, description="Generated candidate tags")
    similarity_analysis: Optional[Dict[str, Any]] = Field(None, description="Cosine similarity analysis")
    tag_critic: Optional[Dict[str, Any]] = Field(None, description="Tag critic agent output")
    summary: Dict[str, Any] = Field(..., description="Summary of the analysis")
    error: Optional[str] = Field(None, description="Error message if workflow failed")
    failed_at_step: Optional[str] = Field(None, description="Step where workflow failed")
