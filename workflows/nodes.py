from agents.data_collection_agent import fetch_github_readme
from agents.metadata_extractor_agent import extract_metadata
from agents.tag_candidate_agent import generate_tag_candidates
from agents.tag_similarity_agent import calculate_tag_similarity
from agents.tag_critic_agent import critique_tags
from agents.tag_rule_agent import rule_based_tag_filter
from .state import SimpleAnalysisState

# Node functions
def data_collector_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
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
    print(f"[Workflow] Generating tag candidates...")
    content = state.get('readme_content', '')
    metadata = state.get('metadata', {})
    if not content:
        state['error'] = "No content available for tag generation"
        state['current_step'] = "tag_candidate"
        return state
    candidates = generate_tag_candidates(metadata, content)
    state['candidate_tags'] = candidates
    state['current_step'] = "tag_candidate_complete"
    return state

def similarity_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    print(f"[Workflow] Calculating tag similarity using embeddings...")
    content = state.get('readme_content', '')
    candidate_tags_data = state.get('candidate_tags', {})
    if not content:
        state['error'] = "No content available for similarity calculation"
        state['current_step'] = "similarity"
        return state
    all_tags = []
    if candidate_tags_data.get('success'):
        candidates = candidate_tags_data.get('candidates', {})
        all_tags = candidates.get('all_candidates', [])
    if not all_tags:
        if 'candidates' in candidate_tags_data:
            candidates = candidate_tags_data['candidates']
            if isinstance(candidates, dict):
                all_tags = candidates.get('all_candidates', [])
                if not all_tags:
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
    similarity_result = calculate_tag_similarity(content, all_tags)
    if not similarity_result.get('success'):
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

def tag_critic_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Tag Critic Node - Evaluates and refines recommended tags using rubric"""
    print(f"[Workflow] Critiquing tags with rubric evaluator...")
    candidate_tags_data = state.get('candidate_tags', {})
    content = state.get('readme_content', '')
    all_tags = []

    if candidate_tags_data.get('success'):
        candidates = candidate_tags_data.get('candidates', {})
        all_tags = candidates.get('all_candidates', [])

    if not all_tags:
        if 'candidates' in candidate_tags_data:
            candidates = candidate_tags_data['candidates']
            if isinstance(candidates, dict):
                all_tags = candidates.get('all_candidates', [])
                if not all_tags:
                    all_tags = (
                        candidates.get('primary_tags', []) +
                        candidates.get('technology_tags', []) +
                        candidates.get('domain_tags', []) +
                        candidates.get('feature_tags', [])
                    )

    if not all_tags:
        state['error'] = f"No candidate tags available for tag critic. Data structure: {candidate_tags_data}"
        state['current_step'] = "tag_critic"
        return state

    critic_result = critique_tags(all_tags, context=content)
    state['tag_critic'] = critic_result
    state['current_step'] = "tag_critic_complete"
    return state

def tag_rule_node(state: SimpleAnalysisState) -> SimpleAnalysisState:
    """Tag Rule Node - Filters tags based on rule-based agent"""
    # Use candidate tags as input
    candidate_tags_data = state.get('candidate_tags', {})
    all_tags = []
    if candidate_tags_data.get('success'):
        candidates = candidate_tags_data.get('candidates', {})
        all_tags = candidates.get('all_candidates', [])
    if not all_tags and 'candidates' in candidate_tags_data:
        candidates = candidate_tags_data['candidates']
        if isinstance(candidates, dict):
            all_tags = candidates.get('all_candidates', [])
            if not all_tags:
                all_tags = (
                    candidates.get('primary_tags', []) +
                    candidates.get('technology_tags', []) +
                    candidates.get('domain_tags', []) +
                    candidates.get('feature_tags', [])
                )
    if not all_tags:
        state['error'] = f"No candidate tags available for tag rule agent. Data structure: {candidate_tags_data}"
        state['current_step'] = "tag_rule"
        return state
    rule_result = rule_based_tag_filter(all_tags)
    state['tag_rule'] = rule_result
    state['current_step'] = "tag_rule_complete"
    return state
