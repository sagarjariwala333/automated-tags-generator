import requests
from typing import Dict
from tool.base64_to_html_plain import decode_base64_to_text, markdown_to_html, html_to_plain_text

def fetch_github_readme(owner: str, repo: str) -> Dict[str, any]:
    """
    Data Collection Agent - Fetches README content from GitHub repository
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
    
    Returns:
        Dictionary containing README content in various formats
    """
    
    # GitHub API endpoint for README
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    try:
        # Fetch README metadata
        response = requests.get(api_url, headers={
            "Accept": "application/vnd.github.v3+json"
        })
        
        if response.status_code == 404:
            return {
                "success": False,
                "error": "Repository or README not found",
                "owner": owner,
                "repo": repo
            }
        
        response.raise_for_status()
        readme_data = response.json()
        
        # Extract base64 content
        base64_content = readme_data.get("content", "")
        
        # Decode base64 to plain text
        plain_text = decode_base64_to_text(base64_content)
        
        # Get HTML content from GitHub API
        html_url = readme_data.get("html_url", "")
        download_url = readme_data.get("download_url", "")
        
        # Fetch raw HTML if available
        html_content = None
        if download_url:
            html_response = requests.get(download_url)
            if html_response.status_code == 200:
                raw_content = html_response.text
                # Convert markdown to HTML-like structure (basic)
                html_content = markdown_to_html(raw_content)
        
        # Convert HTML to plain text
        plain_from_html = html_to_plain_text(html_content) if html_content else plain_text
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "name": readme_data.get("name", ""),
            "path": readme_data.get("path", ""),
            "size": readme_data.get("size", 0),
            "url": readme_data.get("url", ""),
            "html_url": html_url,
            "download_url": download_url,
            "content": {
                "base64": base64_content[:100] + "..." if len(base64_content) > 100 else base64_content,
                "plain_text": plain_text,
                "html": html_content,
                "plain_from_html": plain_from_html,
                "word_count": len(plain_text.split()),
                "char_count": len(plain_text)
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}",
            "owner": owner,
            "repo": repo
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "owner": owner,
            "repo": repo
        }