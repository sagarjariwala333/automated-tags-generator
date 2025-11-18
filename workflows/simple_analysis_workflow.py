from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from agents.data_collection_agent import fetch_github_readme
from agents.metadata_extractor_agent import extract_metadata
from agents.tag_candidate_agent import generate_tag_candidates
from agents.tag_similarity_agent import calculate_tag_similarity

# Define the state structure
class SimpleAnalysisState(TypedDict):
    owner: str
    repo: str
    readme_content: str
    metadata: Dict[str, Any]
    candidate_tags: Dict[str, Any]
    similarity_analysis: Dict[str, Any]
    error: str
    current_step: str

# Node functions
def data_collector_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Data Collector Node - Fetches README from GitHub"""
    print(f"[Workflow] Collecting data from {state['owner']}/{state['repo']}...")
    
    github_data = fetch_github_readme(state['owner'], state['repo'])
    
    if not github_data.get("success"):
        state['error'] = github_data.get("error", "Failed to fetch GitHub data")
        state['current_step'] = "data_collector"
        return state
    
    state['readme_content'] = github_data.get("content", {}).get("plain_text", "")
    state['current_step'] = "data_collector_complete"
    return state

def metadata_extractor_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Metadata Extractor Node - Extracts metadata from README"""
    print(f"[Workflow] Extracting metadata...")
    
    if not state.get('readme_content'):
        state['error'] = "No README content available"
        state['current_step'] = "metadata_extractor"
        return state
    
    metadata = extract_metadata(state['readme_content'])
    state['metadata'] = metadata
    state['current_step'] = "metadata_extractor_complete"
    return state

def tag_candidate_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Tag Candidate Node - Generates candidate tags"""
    print(f"[Workflow] Generating tag candidates...")
    
    content = state.get('readme_content', '')
    metadata = state.get('metadata', {})
    
    if not content:
        state['error'] = "No content available for tag generation"
        state['current_step'] = "tag_candidate"
        return state
    
    # Call with correct parameter order: metadata first, then content
    candidates = generate_tag_candidates(metadata, content)
    state['candidate_tags'] = candidates
    state['current_step'] = "tag_candidate_complete"
    return state

def similarity_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Similarity Node - Calculates cosine similarity between README and tags"""
    print(f"[Workflow] Calculating tag similarity using embeddings...")
    
    content = state.get('readme_content', '')
    candidate_tags_data = state.get('candidate_tags', {})
    
    if not content:
        state['error'] = "No content available for similarity calculation"
        state['current_step'] = "similarity"
        return state
    
    # Debug: Print candidate_tags_data structure
    print(f"[Debug] candidate_tags_data keys: {candidate_tags_data.keys()}")
    print(f"[Debug] candidate_tags_data: {candidate_tags_data}")
    
    # Extract all candidate tags - handle different structures
    all_tags = []
    
    if candidate_tags_data.get('success'):
        candidates = candidate_tags_data.get('candidates', {})
        all_tags = candidates.get('all_candidates', [])
    
    # Fallback: try to extract from raw_response or other fields
    if not all_tags:
        # Try to get from any available field
        if 'candidates' in candidate_tags_data:
            candidates = candidate_tags_data['candidates']
            if isinstance(candidates, dict):
                all_tags = candidates.get('all_candidates', [])
                if not all_tags:
                    # Collect all tags from different categories
                    all_tags = (
                        candidates.get('primary_tags', []) +
                        candidates.get('technology_tags', []) +
                        candidates.get('domain_tags', []) +
                        candidates.get('feature_tags', [])
                    )
    
    if not all_tags:
        state['error'] = f"No candidate tags available. Data structure: {candidate_tags_data}"
        state['current_step'] = "similarity"
        return state
    
    print(f"[Workflow] Found {len(all_tags)} tags for similarity calculation")
    
    # Calculate similarity
    similarity_result = calculate_tag_similarity(content, all_tags)
    
    # If similarity calculation failed due to quota, continue workflow with warning
    if not similarity_result.get('success'):
        print(f"[Workflow Warning] Similarity calculation failed: {similarity_result.get('error', 'Unknown error')}")
        state['similarity_analysis'] = {
            "success": False,
            "error": "Similarity calculation skipped due to API quota limits",
            "note": "Using candidate tags without similarity scoring",
            "agent": "tag_similarity_agent"
        }
    else:
        state['similarity_analysis'] = similarity_result
    
    state['current_step'] = "similarity_complete"
    return state

# Build the workflow
def create_simple_analysis_workflow():
    """Create and return a simple analysis workflow with 4 agents"""
    
    workflow = StateGraph(SimpleAnalysisState)
    
    # Add nodes
    workflow.add_node("collector", data_collector_node)
    workflow.add_node("metadata", metadata_extractor_node)
    workflow.add_node("candidate", tag_candidate_node)
    workflow.add_node("similarity", similarity_node)
    
    # Add edges
    workflow.add_edge("collector", "metadata")
    workflow.add_edge("metadata", "candidate")
    workflow.add_edge("candidate", "similarity")
    workflow.add_edge("similarity", END)
    
    # Set entry point
    workflow.set_entry_point("collector")
    
    return workflow.compile()

def run_simple_analysis_workflow(owner: str, repo: str) -> Dict[str, Any]:
    """
    Run the simple analysis workflow (collector -> metadata)
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
    
    Returns:
        Dictionary with workflow results
    """
    
    # Create workflow
    app = create_simple_analysis_workflow()
    
    # Initial state
    initial_state = {
        "owner": owner,
        "repo": repo,
        "readme_content": "",
        "metadata": {},
        "candidate_tags": {},
        "similarity_analysis": {},
        "error": "",
        "current_step": "start"
    }
    
    # Run workflow
    try:
        final_state = app.invoke(initial_state)
        
        if final_state.get('error'):
            return {
                "success": False,
                "error": final_state['error'],
                "failed_at_step": final_state.get('current_step'),
                "owner": owner,
                "repo": repo
            }
        
        similarity_data = final_state.get('similarity_analysis', {})
        candidate_tags_data = final_state.get('candidate_tags', {})
        
        # Get all candidate tags as fallback for recommended tags
        all_candidates = []
        if candidate_tags_data.get('success'):
            candidates = candidate_tags_data.get('candidates', {})
            all_candidates = candidates.get('all_candidates', [])
        
        # Use similarity recommended tags if available, otherwise use all candidates
        recommended_tags = similarity_data.get('recommended_tags', all_candidates[:10])
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "workflow": "simple_analysis",
            "steps_completed": ["collector", "metadata", "candidate", "similarity"],
            "readme_content": {
                "text": final_state.get('readme_content', '')[:500] + "...",
                "length": len(final_state.get('readme_content', ''))
            },
            "metadata": final_state.get('metadata', {}),
            "candidate_tags": final_state.get('candidate_tags', {}),
            "similarity_analysis": similarity_data,
            "summary": {
                "repository": f"{owner}/{repo}",
                "title": final_state.get('metadata', {}).get('title', 'N/A'),
                "category": final_state.get('metadata', {}).get('category', 'N/A'),
                "keywords": final_state.get('metadata', {}).get('keywords', []),
                "sentiment": final_state.get('metadata', {}).get('sentiment', 'N/A'),
                "recommended_tags": recommended_tags,
                "similarity_stats": similarity_data.get('statistics', {}),
                "note": "Similarity scoring unavailable due to API quota" if not similarity_data.get('success') else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Workflow execution failed: {str(e)}",
            "owner": owner,
            "repo": repo
        }
