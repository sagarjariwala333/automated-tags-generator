import requests
from typing import List


def fetch_github_topics(owner: str, repo: str) -> List[str]:
    """
    Fetches the topics/tags assigned to a GitHub repository.
    
    Topics are keywords that repository owners can add to categorize their projects.
    These are displayed on the repository's main page.
    
    Args:
        owner: GitHub repository owner/organization name
        repo: Repository name
        
    Returns:
        List of topic strings (e.g., ["python", "machine-learning", "api"])
        Returns empty list if request fails or no topics assigned
        
    Example:
        >>> topics = fetch_github_topics("facebook", "react")
        >>> print(topics)
        ['javascript', 'react', 'frontend', 'ui']
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    
    try:
        response = requests.get(api_url, headers={
            "Accept": "application/vnd.github.mercy-preview+json"  # Required for topics API
        })
        
        # Return empty list if repo not found or other errors
        if response.status_code != 200:
            return []
        
        # GitHub returns: {"names": ["python", "machine-learning", ...]}
        topics_data = response.json()
        
        # Extract the topics array
        topics = topics_data.get("names", [])
        
        return topics
        
    except Exception as e:
        # Return empty list on any error
        return []
