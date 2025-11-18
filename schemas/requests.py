from pydantic import BaseModel, Field
from typing import Literal

class TaskRequest(BaseModel):
    task: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Task to be processed by the multi-agent system"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task": "Research AI trends in 2024, write a summary, and review it"
            }
        }

class MetadataRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Content to extract metadata from"
    )
    
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

class GitHubReadmeRequest(BaseModel):
    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="GitHub repository owner or organization name"
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
                "owner": "openai",
                "repo": "gpt-3"
            }
        }

class Base64ConvertRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        description="Content to convert (base64 or plain text)"
    )
    operation: Literal["encode", "decode"] = Field(
        ...,
        description="Operation to perform: encode (text to base64) or decode (base64 to text)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello World",
                "operation": "encode"
            }
        }

class HtmlConvertRequest(BaseModel):
    html_content: str = Field(
        ...,
        min_length=1,
        description="HTML content to convert to plain text"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "html_content": "<html><body><h1>Hello World</h1><p>This is a test.</p></body></html>"
            }
        }
