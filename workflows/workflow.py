from langgraph.graph import StateGraph, END
from .state import SimpleAnalysisState
from .nodes import data_collector_node, tag_candidate_node, similarity_node, tag_rule_node, tag_critic_node

def create_simple_analysis_workflow():
    """Create and return a simple analysis workflow with rule and critic agents"""
    workflow = StateGraph(SimpleAnalysisState)
    
    # Add nodes
    workflow.add_node("collector", data_collector_node)
    workflow.add_node("candidate", tag_candidate_node)
    workflow.add_node("similarity", similarity_node)
    workflow.add_node("tag_critic", tag_critic_node)
    workflow.add_node("tag_rule", tag_rule_node)
    
    # Define workflow edges (removed metadata extractor)
    workflow.add_edge("collector", "candidate")
    workflow.add_edge("candidate", "similarity")
    workflow.add_edge("similarity", "tag_critic")
    workflow.add_edge("tag_critic", "tag_rule")
    workflow.add_edge("tag_rule", END)
    
    workflow.set_entry_point("collector")
    return workflow.compile()

def run_simple_analysis_workflow(owner: str, repo: str):
    app = create_simple_analysis_workflow()
    initial_state = {
        "owner": owner,
        "repo": repo,
        "readme_content": "",
        "technologies": [],
        "topics": [],
        "candidate_tags": [],  # Now a simple list
        "similarity_analysis": {},
        "tag_critic": {},
        "tag_rule": {},
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
        
        # Extract data from final state
        similarity_data = final_state.get('similarity_analysis', {})
        candidate_tags = final_state.get('candidate_tags', [])
        tag_critic_data = final_state.get('tag_critic', {})
        tag_rule_data = final_state.get('tag_rule', {})
        technologies = final_state.get('technologies', [])
        topics = final_state.get('topics', [])
        
        # Get recommended tags from similarity analysis
        recommended_tags = similarity_data.get('recommended_tags', candidate_tags[:10])
        
        return {
            "success": True,
            "owner": owner,
            "repo": repo,
            "workflow": "simple_analysis",
            "steps_completed": ["collector", "candidate", "similarity", "tag_critic", "tag_rule"],
            "readme_content": {
                "text": final_state.get('readme_content', '')[:500] + "...",
                "length": len(final_state.get('readme_content', ''))
            },
            "technologies": technologies,
            "topics": topics,
            "candidate_tags": candidate_tags,
            "similarity_analysis": similarity_data,
            "tag_critic": tag_critic_data,
            "tag_rule": tag_rule_data,
            "summary": {
                "repository": f"{owner}/{repo}",
                "technologies": technologies,
                "topics": topics,
                "recommended_tags": recommended_tags,
                "similarity_stats": similarity_data.get('statistics', {})
            }
        }
    except Exception as e:
        print(f"Exception in workflow: {e}")
        return {
            "success": False,
            "error": f"Workflow execution failed: {str(e)}",
            "owner": owner,
            "repo": repo
        }
