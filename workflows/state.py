from typing import Dict, Any, TypedDict, List

class SimpleAnalysisState(TypedDict):
    owner: str
    repo: str
    readme_content: str
    technologies: List[str]  # GitHub languages/technologies
    topics: List[str]  # GitHub topics
    candidate_tags: List[str]  # Simplified: now just array of strings
    similarity_analysis: Dict[str, Any]
    tag_rule: Dict[str, Any]  # Added for rule-based agent output
    tag_critic: Dict[str, Any]  # Added field for tag critic output
    error: str
    current_step: str
