import requests
from typing import List


def fetch_github_technologies(owner: str, repo: str) -> List[str]:
    """
    Fetches the programming languages/technologies used in a GitHub repository.
    
    Uses the GitHub API languages endpoint which returns languages detected in the repository
    based on file extensions and content analysis.
    
    Args:
        owner: GitHub repository owner/organization name
        repo: Repository name
        
    Returns:
        List of technology/language names (e.g., ["Python", "JavaScript", "HTML"])
        Returns empty list if request fails or no languages detected
        
    Example:
        >>> technologies = fetch_github_technologies("facebook", "react")
        >>> print(technologies)
        ['JavaScript', 'HTML', 'CSS']
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    try:
        response = requests.get(api_url, headers={
            "Accept": "application/vnd.github.v3+json"
        })
        
        # Return empty list if repo not found or other errors
        if response.status_code != 200:
            return []
        
        # GitHub returns a dict like: {"Python": 12345, "JavaScript": 6789}
        # where the values are bytes of code
        languages_data = response.json()
        
        # Extract just the language names
        technologies = list(languages_data.keys())
        
        return technologies
        
    except Exception as e:
        # Return empty list on any error
        return []

