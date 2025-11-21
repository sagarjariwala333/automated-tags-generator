import requests
from typing import Dict
from tool.github_readme import fetch_readme_content
from tool.github_technologies import fetch_github_technologies
from tool.github_topics import fetch_github_topics

def fetch_github_readme(owner: str, repo: str) -> Dict[str, any]:
    """
    Data Collection Agent - Fetches README content from GitHub repository
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
    
    Returns:
        Dictionary containing README content in various formats
    """
    # Input validation
    if not owner or not isinstance(owner, str):
        return {
            "success": False,
            "error": "Invalid owner parameter: must be a non-empty string",
            "owner": owner,
            "repo": repo
        }
    
    if not repo or not isinstance(repo, str):
        return {
            "success": False,
            "error": "Invalid repo parameter: must be a non-empty string",
            "owner": owner,
            "repo": repo
        }
    
    try:
        # Fetch README content using the tool
        readme_result = fetch_readme_content(owner, repo)
        
        if not readme_result or not isinstance(readme_result, dict):
            return {
                "success": False,
                "error": "Invalid response from README fetch tool",
                "owner": owner,
                "repo": repo
            }
        
        if not readme_result.get("success", False):
            return {
                "success": False,
                "error": readme_result.get("error", "Unknown error fetching README"),
                "owner": owner,
                "repo": repo
            }
        
        # Fetch additional repository metadata (these can fail without breaking the whole operation)
        technologies = []
        topics = []
        
        try:
            technologies = fetch_github_technologies(owner, repo)
        except Exception as e:
            print(f"[data_collection_agent] Warning: Failed to fetch technologies: {str(e)}")
        
        try:
            topics = fetch_github_topics(owner, repo)
        except Exception as e:
            print(f"[data_collection_agent] Warning: Failed to fetch topics: {str(e)}")
        
        # Extract data from readme_result with validation
        plain_text = readme_result.get("plain_text", "")
        html_content = readme_result.get("html", "")
        plain_from_html = readme_result.get("plain_from_html", plain_text)
        metadata = readme_result.get("metadata", {})
        
        # Validate metadata structure
        if not isinstance(metadata, dict):
            metadata = {}
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "name": metadata.get("name", ""),
            "path": metadata.get("path", ""),
            "size": metadata.get("size", 0),
            "url": metadata.get("url", ""),
            "html_url": metadata.get("html_url", ""),
            "download_url": metadata.get("download_url", ""),
            "technologies": technologies if isinstance(technologies, list) else [],
            "topics": topics if isinstance(topics, list) else [],
            "content": {
                "plain_text": plain_text,
                "html": html_content,
                "plain_from_html": plain_from_html,
                "word_count": len(plain_text.split()) if plain_text else 0,
                "char_count": len(plain_text) if plain_text else 0
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error in data collection agent: {str(e)}",
            "owner": owner,
            "repo": repo
        }