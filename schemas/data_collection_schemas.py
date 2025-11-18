from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class GitHubRepoRequest(BaseModel):
    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="GitHub repository owner/organization name"
    )
    repo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="GitHub repository name"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "owner": "facebook",
                "repo": "react"
            }
        }

class ReadmeContentResponse(BaseModel):
    base64: Optional[str] = Field(None, description="Base64 encoded content (truncated)")
    plain_text: Optional[str] = Field(None, description="Decoded plain text content")
    html: Optional[str] = Field(None, description="HTML formatted content")
    plain_from_html: Optional[str] = Field(None, description="Plain text extracted from HTML")
    word_count: Optional[int] = Field(None, description="Word count")
    char_count: Optional[int] = Field(None, description="Character count")

class GitHubRepoResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    name: Optional[str] = Field(None, description="README file name")
    path: Optional[str] = Field(None, description="README file path")
    size: Optional[int] = Field(None, description="File size in bytes")
    url: Optional[str] = Field(None, description="API URL")
    html_url: Optional[str] = Field(None, description="GitHub HTML URL")
    download_url: Optional[str] = Field(None, description="Raw download URL")
    content: Optional[Dict[str, Any]] = Field(None, description="README content in various formats")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "owner": "facebook",
                "repo": "react",
                "name": "README.md",
                "path": "README.md",
                "size": 15234,
                "content": {
                    "plain_text": "# React\n\nA JavaScript library...",
                    "word_count": 1500,
                    "char_count": 15234
                }
            }
        }
