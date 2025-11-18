from fastapi import APIRouter, HTTPException
from schemas.data_collection_schemas import GitHubRepoRequest, GitHubRepoResponse
from agents.data_collection_agent import fetch_github_readme

router = APIRouter(prefix="/data", tags=["data-collection"])

@router.post("/github/readme", response_model=GitHubRepoResponse)
async def get_github_readme(request: GitHubRepoRequest):
    """
    Fetch README content from a GitHub repository
    
    This endpoint:
    - Fetches README from GitHub API
    - Decodes base64 content to plain text
    - Converts to HTML format
    - Extracts plain text from HTML
    - Returns content in multiple formats
    """
    try:
        result = fetch_github_readme(request.owner, request.repo)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Unknown error occurred")
            )
        
        return GitHubRepoResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/github/readme/{owner}/{repo}", response_model=GitHubRepoResponse)
async def get_github_readme_path(owner: str, repo: str):
    """
    Fetch README content from a GitHub repository (GET method with path parameters)
    
    Alternative endpoint using path parameters instead of request body.
    """
    try:
        result = fetch_github_readme(owner, repo)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=404 if "not found" in result.get("error", "").lower() else 500,
                detail=result.get("error", "Unknown error occurred")
            )
        
        return GitHubRepoResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
