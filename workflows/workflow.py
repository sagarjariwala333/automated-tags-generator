from langgraph.graph import StateGraph, END
from .state import SimpleAnalysisState
from .nodes import data_collector_node, metadata_extractor_node, tag_candidate_node, similarity_node, tag_critic_node

def create_simple_analysis_workflow():
    """Create and return a simple analysis workflow with 5 agents (added tag_critic)"""
    workflow = StateGraph(SimpleAnalysisState)
    workflow.add_node("collector", data_collector_node)
    workflow.add_node("metadata", metadata_extractor_node)
    workflow.add_node("candidate", tag_candidate_node)
    workflow.add_node("similarity", similarity_node)
    workflow.add_node("tag_critic", tag_critic_node)
    workflow.add_edge("collector", "metadata")
    workflow.add_edge("metadata", "candidate")
    workflow.add_edge("candidate", "similarity")
    workflow.add_edge("similarity", "tag_critic")
    workflow.add_edge("tag_critic", END)
    workflow.set_entry_point("collector")
    return workflow.compile()

def run_simple_analysis_workflow(owner: str, repo: str):
    print("Workflow starting....")
    app = create_simple_analysis_workflow()
    initial_state = {
        "owner": owner,
        "repo": repo,
        "readme_content": "",
        "metadata": {},
        "candidate_tags": {},
        "similarity_analysis": {},
        "tag_critic": {},  # Ensure tag_critic is initialized
        "error": "",
        "current_step": "start"
    }
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
        tag_critic_data = final_state.get('tag_critic', {})
        all_candidates = []
        if candidate_tags_data.get('success'):
            candidates = candidate_tags_data.get('candidates', {})
            all_candidates = candidates.get('all_candidates', [])
        recommended_tags = similarity_data.get('recommended_tags', all_candidates[:10])
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "workflow": "simple_analysis",
            "steps_completed": ["collector", "metadata", "candidate", "similarity", "tag_critic"],
            "readme_content": {
                "text": final_state.get('readme_content', '')[:500] + "...",
                "length": len(final_state.get('readme_content', ''))
            },
            "metadata": final_state.get('metadata', {}),
            "candidate_tags": final_state.get('candidate_tags', {}),
            "similarity_analysis": similarity_data,
            "tag_critic": tag_critic_data,
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
