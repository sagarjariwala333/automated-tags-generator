import requests
from typing import Dict, Optional
from tool.base64_to_html_plain import decode_base64_to_text, markdown_to_html, html_to_plain_text


def fetch_readme_content(owner: str, repo: str) -> Dict[str, any]:
    """
    Fetches README content from a GitHub repository and processes it into multiple formats.
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
        
    Returns:
        Dictionary containing:
            - success: bool
            - plain_text: str (decoded plain text from README)
            - html: str (HTML version of README)
            - plain_from_html: str (plain text extracted from HTML)
            - metadata: dict (README file metadata)
            - error: str (only if success is False)
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    try:
        # Fetch README metadata
        response = requests.get(api_url, headers={
            "Accept": "application/vnd.github.v3+json"
        })
        
        if response.status_code == 404:
            return {
                "success": False,
                "error": "Repository or README not found"
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
            "plain_text": plain_text,
            "html": html_content,
            "plain_from_html": plain_from_html,
            "metadata": {
                "name": readme_data.get("name", ""),
                "path": readme_data.get("path", ""),
                "size": readme_data.get("size", 0),
                "url": readme_data.get("url", ""),
                "html_url": html_url,
                "download_url": download_url
            }
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
