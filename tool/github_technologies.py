import requests
import time
import re
from typing import List


def _validate_github_identifier(identifier: str, name: str) -> bool:
    """Validate GitHub owner/repo identifier format"""
    if not identifier or not isinstance(identifier, str):
        return False
    if not re.match(r'^[a-zA-Z0-9._-]+$', identifier.strip()):
        return False
    return True


def fetch_github_technologies(owner: str, repo: str, max_retries: int = 3, timeout: int = 10) -> List[str]:
    """
    Fetches the programming languages/technologies used in a GitHub repository.
    
    Uses the GitHub API languages endpoint which returns languages detected in the repository
    based on file extensions and content analysis.
    
    Args:
        owner: GitHub repository owner/organization name
        repo: Repository name
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 10)
        
    Returns:
        List of technology/language names (e.g., ["Python", "JavaScript", "HTML"])
        Returns empty list if request fails or no languages detected
        
    Example:
        >>> technologies = fetch_github_technologies("facebook", "react")
        >>> print(technologies)
        ['JavaScript', 'HTML', 'CSS']
    """
    # Input validation
    if not _validate_github_identifier(owner, "owner"):
        print(f"[github_technologies] Invalid owner format: {owner}")
        return []
    
    if not _validate_github_identifier(repo, "repo"):
        print(f"[github_technologies] Invalid repo format: {repo}")
        return []
    
    owner = owner.strip()
    repo = repo.strip()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.get(
                api_url, 
                headers={
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Auto-Tags-Generator-AI"
                },
                timeout=timeout
            )
            
            # Handle rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if rate_limit_remaining == '0':
                    print(f"[github_technologies] GitHub API rate limit exceeded")
                    return []
            
            # Return empty list if repo not found
            if response.status_code == 404:
                print(f"[github_technologies] Repository '{owner}/{repo}' not found")
                return []
            
            # Return empty list for other errors
            if response.status_code != 200:
                print(f"[github_technologies] API returned status {response.status_code}")
                return []
            
            # GitHub returns a dict like: {"Python": 12345, "JavaScript": 6789}
            # where the values are bytes of code
            languages_data = response.json()
            
            # Validate response is a dictionary
            if not isinstance(languages_data, dict):
                print(f"[github_technologies] Invalid response format")
                return []
            
            # Extract just the language names
            technologies = list(languages_data.keys())
            
            return technologies
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            print(f"[github_technologies] Request timeout after {max_retries} attempts")
            return []
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            print(f"[github_technologies] Connection error after {max_retries} attempts")
            return []
            
        except Exception as e:
            print(f"[github_technologies] Unexpected error: {str(e)}")
            return []
    
    # Should not reach here
    print(f"[github_technologies] Maximum retries exceeded")
    return []

