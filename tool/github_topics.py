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


def fetch_github_topics(owner: str, repo: str, max_retries: int = 3, timeout: int = 10) -> List[str]:
    """
    Fetches the topics/tags assigned to a GitHub repository.
    
    Topics are keywords that repository owners can add to categorize their projects.
    These are displayed on the repository's main page.
    
    Args:
        owner: GitHub repository owner/organization name
        repo: Repository name
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 10)
        
    Returns:
        List of topic strings (e.g., ["python", "machine-learning", "api"])
        Returns empty list if request fails or no topics assigned
        
    Example:
        >>> topics = fetch_github_topics("facebook", "react")
        >>> print(topics)
        ['javascript', 'react', 'frontend', 'ui']
    """
    # Input validation
    if not _validate_github_identifier(owner, "owner"):
        print(f"[github_topics] Invalid owner format: {owner}")
        return []
    
    if not _validate_github_identifier(repo, "repo"):
        print(f"[github_topics] Invalid repo format: {repo}")
        return []
    
    owner = owner.strip()
    repo = repo.strip()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.get(
                api_url, 
                headers={
                    "Accept": "application/vnd.github.mercy-preview+json",  # Required for topics API
                    "User-Agent": "Auto-Tags-Generator-AI"
                },
                timeout=timeout
            )
            
            # Handle rate limiting
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if rate_limit_remaining == '0':
                    print(f"[github_topics] GitHub API rate limit exceeded")
                    return []
            
            # Return empty list if repo not found
            if response.status_code == 404:
                print(f"[github_topics] Repository '{owner}/{repo}' not found")
                return []
            
            # Return empty list for other errors
            if response.status_code != 200:
                print(f"[github_topics] API returned status {response.status_code}")
                return []
            
            # GitHub returns: {"names": ["python", "machine-learning", ...]}
            topics_data = response.json()
            
            # Validate response is a dictionary
            if not isinstance(topics_data, dict):
                print(f"[github_topics] Invalid response format")
                return []
            
            # Extract the topics array
            topics = topics_data.get("names", [])
            
            # Validate topics is a list
            if not isinstance(topics, list):
                print(f"[github_topics] Topics data is not a list")
                return []
            
            return topics
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            print(f"[github_topics] Request timeout after {max_retries} attempts")
            return []
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            print(f"[github_topics] Connection error after {max_retries} attempts")
            return []
            
        except Exception as e:
            print(f"[github_topics] Unexpected error: {str(e)}")
            return []
    
    # Should not reach here
    print(f"[github_topics] Maximum retries exceeded")
    return []
