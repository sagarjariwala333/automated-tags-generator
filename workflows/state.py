from typing import Dict, Any, TypedDict

class SimpleAnalysisState(TypedDict):
    owner: str
    repo: str
    readme_content: str
    metadata: Dict[str, Any]
    candidate_tags: Dict[str, Any]
    similarity_analysis: Dict[str, Any]
    error: str
    current_step: str
