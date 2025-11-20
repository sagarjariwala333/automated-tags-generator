from agents.data_collection_agent import fetch_github_readme
from agents.tag_candidate_agent import generate_tag_candidates
from agents.tag_similarity_agent import calculate_tag_similarity
from agents.tag_critic_agent import critique_tags
from agents.tag_rule_agent import rule_based_tag_filter
from .state import SimpleAnalysisState

# Node functions
def data_collector_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Fetch README, technologies, and topics from GitHub"""
    github_data = fetch_github_readme(state['owner'], state['repo'])
    
    if not github_data.get("success"):
        state['error'] = github_data.get("error", "Failed to fetch GitHub data")
        state['current_step'] = "data_collector"
        return state
    
    # Extract README content
    state['readme_content'] = github_data.get("content", {}).get("plain_text", "")
    
    # Extract technologies and topics
    state['technologies'] = github_data.get("technologies", [])
    state['topics'] = github_data.get("topics", [])
    
    state['current_step'] = "data_collector_complete"
    return state

def tag_candidate_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Generate candidate tags from README content using chunking strategy"""
    content = state.get('readme_content', '')
    
    if not content:
        state['error'] = "No content available for tag generation"
        state['current_step'] = "tag_candidate"
        return state
    
    # New signature: just pass readme_content, returns List[str]
    candidate_tags = generate_tag_candidates(content)
    
    # Store as simple list
    state['candidate_tags'] = candidate_tags + state['technologies'] + state['topics']
    state['current_step'] = "tag_candidate_complete"
    return state

def similarity_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Calculate similarity between README and candidate tags"""
    content = state.get('readme_content', '')
    candidate_tags = state.get('candidate_tags', [])
    
    if not content:
        state['error'] = "No content available for similarity calculation"
        state['current_step'] = "similarity"
        return state
    
    if not candidate_tags:
        state['error'] = "No candidate tags available for similarity calculation"
        state['current_step'] = "similarity"
        return state
    
    # New signature: calculate_tag_similarity(readme_content, candidate_tags)
    similarity_result = calculate_tag_similarity(content, candidate_tags)
    
    if not similarity_result.get('success'):
        state['similarity_analysis'] = {
            "success": False,
            "error": similarity_result.get('error', 'Similarity calculation failed'),
            "agent": "tag_similarity_agent"
        }
    else:
        state['similarity_analysis'] = similarity_result
    
    state['current_step'] = "similarity_complete"
    return state

def tag_critic_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Evaluate and refine tags using rubric-based critique"""
    print(f"[Workflow] Critiquing tags with rubric evaluator...")
    
    content = state.get('readme_content', '')
    similarity_analysis = state.get('similarity_analysis', {})
    
    # Get recommended tags from similarity analysis
    recommended_tags = similarity_analysis.get('recommended_tags', [])
    
    if not recommended_tags:
        # Fallback to top candidate tags if similarity didn't produce recommendations
        candidate_tags = state.get('candidate_tags', [])
        recommended_tags = candidate_tags[:10] if candidate_tags else []
    
    if not recommended_tags:
        state['error'] = "No tags available for critique"
        state['current_step'] = "tag_critic"
        return state
    
    # Critique the recommended tags
    critic_result = critique_tags(recommended_tags, context=content)
    state['tag_critic'] = critic_result
    state['current_step'] = "tag_critic_complete"
    return state

def tag_rule_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Filter tags using rule-based validation"""
    
    # Get tags from tag_critic output (refined tags)
    tag_critic_data = state.get('tag_critic', {})
    
    # Try to get refined/passing tags from critic
    tags_to_filter = []
    
    if tag_critic_data.get('success'):
        # Use passing tags from critic if available
        passing_tags = tag_critic_data.get('passing_tags', [])
        if passing_tags:
            tags_to_filter = passing_tags
        else:
            # Fallback to all evaluated tags
            evaluated_tags = tag_critic_data.get('evaluated_tags', [])
            tags_to_filter = [t.get('tag', '') for t in evaluated_tags if t.get('tag')]
    
    # If no tags from critic, use candidate tags
    if not tags_to_filter:
        tags_to_filter = state.get('candidate_tags', [])
    
    if not tags_to_filter:
        state['error'] = "No tags available for rule-based filtering"
        state['current_step'] = "tag_rule"
        return state
    
    # Apply rule-based filter
    rule_result = rule_based_tag_filter(tags_to_filter)
    state['tag_rule'] = rule_result
    state['current_step'] = "tag_rule_complete"
    return state
