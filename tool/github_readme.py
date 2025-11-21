import requests
import time
import re
from typing import Dict, Optional
from tool.base64_to_html_plain import decode_base64_to_text, markdown_to_html, html_to_plain_text


def _validate_github_identifier(identifier: str, name: str) -> bool:
    """Validate GitHub owner/repo identifier format"""
    if not identifier or not isinstance(identifier, str):
        return False
    # GitHub allows alphanumeric, hyphens, underscores, and dots
    if not re.match(r'^[a-zA-Z0-9._-]+$', identifier.strip()):
        return False
    return True


def fetch_readme_content(owner: str, repo: str, max_retries: int = 3, timeout: int = 10) -> Dict[str, any]:
    """
    Fetches README content from a GitHub repository and processes it into multiple formats.
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
        max_retries: Maximum number of retry attempts for API calls (default: 3)
        timeout: Request timeout in seconds (default: 10)
        
    Returns:
        Dictionary containing:
            - success: bool
            - plain_text: str (decoded plain text from README)
            - html: str (HTML version of README)
            - plain_from_html: str (plain text extracted from HTML)
            - metadata: dict (README file metadata)
            - error: str (only if success is False)
    """
    # Input validation
    if not _validate_github_identifier(owner, "owner"):
        return {
            "success": False,
            "error": "Invalid owner format. Owner must contain only alphanumeric characters, hyphens, underscores, or dots."
        }
    
    if not _validate_github_identifier(repo, "repo"):
        return {
            "success": False,
            "error": "Invalid repo format. Repo must contain only alphanumeric characters, hyphens, underscores, or dots."
        }
    
    owner = owner.strip()
    repo = repo.strip()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            # Fetch README metadata with timeout and user-agent
            response = requests.get(
                api_url, 
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Auto-Tags-Generator-AI"
                },
                timeout=timeout
            )
            
            # Handle specific error cases
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Repository '{owner}/{repo}' or its README not found"
                }
            
            # Handle rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if rate_limit_remaining == '0':
                    reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
                    return {
                        "success": False,
                        "error": f"GitHub API rate limit exceeded. Resets at: {reset_time}"
                    }
            
            response.raise_for_status()
            readme_data = response.json()
            
            # Validate response structure
            if not isinstance(readme_data, dict):
                return {
                    "success": False,
                    "error": "Invalid response format from GitHub API"
                }
            
            # Extract base64 content
            base64_content = readme_data.get("content", "")
            if not base64_content:
                return {
                    "success": False,
                    "error": "README file is empty or content not available"
                }
            
            # Decode base64 to plain text
            plain_text = decode_base64_to_text(base64_content)
            
            # Check if decoding failed
            if plain_text.startswith("Error decoding base64:"):
                return {
                    "success": False,
                    "error": plain_text
                }
            
            # Validate decoded content is not empty
            if not plain_text or not plain_text.strip():
                return {
                    "success": False,
                    "error": "README file decoded but contains no content"
                }
            
            # Get HTML content from GitHub API
            html_url = readme_data.get("html_url", "")
            download_url = readme_data.get("download_url", "")
            
            # Fetch raw HTML if available
            html_content = None
            if download_url:
                try:
                    html_response = requests.get(download_url, timeout=timeout)
                    if html_response.status_code == 200:
                        raw_content = html_response.text
                        # Convert markdown to HTML-like structure (basic)
                        html_content = markdown_to_html(raw_content)
                except Exception:
                    # If HTML fetch fails, continue with plain text
                    html_content = markdown_to_html(plain_text)
            else:
                html_content = markdown_to_html(plain_text)
            
            # Convert HTML to plain text
            plain_from_html = html_to_plain_text(html_content) if html_content else plain_text
            
            # Check if HTML conversion failed
            if plain_from_html and plain_from_html.startswith("Error converting HTML to text:"):
                # Fall back to plain text if HTML conversion fails
                plain_from_html = plain_text
            
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
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            return {
                "success": False,
                "error": f"Request timeout after {max_retries} attempts. GitHub API may be slow or unreachable."
            }
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            return {
                "success": False,
                "error": f"Connection error after {max_retries} attempts. Please check your internet connection."
            }
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            return {
                "success": False,
                "error": f"Request failed after {max_retries} attempts: {str(e)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    # Should not reach here, but just in case
    return {
        "success": False,
        "error": "Maximum retries exceeded"
    }
