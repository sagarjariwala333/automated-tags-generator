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
    
    try:
        # Fetch README content using the tool
        readme_result = fetch_readme_content(owner, repo)
        
        if not readme_result["success"]:
            return {
                "success": False,
                "error": readme_result.get("error", "Unknown error"),
                "owner": owner,
                "repo": repo
            }
        
        # Fetch additional repository metadata
        technologies = fetch_github_technologies(owner, repo)
        topics = fetch_github_topics(owner, repo)
        
        # Extract data from readme_result
        plain_text = readme_result["plain_text"]
        html_content = readme_result["html"]
        plain_from_html = readme_result["plain_from_html"]
        metadata = readme_result["metadata"]
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "name": metadata["name"],
            "path": metadata["path"],
            "size": metadata["size"],
            "url": metadata["url"],
            "html_url": metadata["html_url"],
            "download_url": metadata["download_url"],
            "technologies": technologies,
            "topics": topics,
            "content": {
                "plain_text": plain_text,
                "html": html_content,
                "plain_from_html": plain_from_html,
                "word_count": len(plain_text.split()),
                "char_count": len(plain_text)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "owner": owner,
            "repo": repo
        }