from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import re
from .prompts import tag_critic_eval_prompt, tag_critic_revise_prompt
from tool.tag_critic_rubric import TagCriticResponse, TagEvaluation, RevisionModel, IterationLog, evaluate_tags_rubric

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def critique_tags(tags: list, context: str = "", threshold: float = 0.7, max_iterations: int = 3) -> dict:
    """Tag Critic Agent - Evaluates tag quality and attempts improvement"""
    # Input validation
    if not tags or not isinstance(tags, list):
        return {
            "original_tags": tags if isinstance(tags, list) else [],
            "final_tags": [],
            "error": "Invalid tags parameter: must be a non-empty list",
            "agent": "tag_critic_agent"
        }
    
    # Filter out non-string tags
    valid_tags = [tag for tag in tags if isinstance(tag, str) and tag.strip()]
    
    if not valid_tags:
        return {
            "original_tags": tags,
            "final_tags": [],
            "error": "No valid string tags found in input",
            "agent": "tag_critic_agent"
        }
    
    # Validate threshold
    if not (0.0 <= threshold <= 1.0):
        print(f"[tag_critic_agent] Warning: Invalid threshold {threshold}, using default 0.7")
        threshold = 0.7
    
    # Validate max_iterations
    if not isinstance(max_iterations, int) or max_iterations < 1:
        print(f"[tag_critic_agent] Warning: Invalid max_iterations {max_iterations}, using default 3")
        max_iterations = 3
    
    try:
        model_result = evaluate_tags_rubric(
            valid_tags,
            context=context,
            threshold=threshold,
            max_iterations=max_iterations,
            llm=llm,
            tag_critic_eval_prompt=tag_critic_eval_prompt,
            tag_critic_revise_prompt=tag_critic_revise_prompt
        )
        
        if not model_result:
            return {
                "original_tags": valid_tags,
                "final_tags": valid_tags,
                "error": "Rubric evaluation returned empty result",
                "agent": "tag_critic_agent"
            }
        
        print("model result...", model_result)
        return model_result.dict()
        
    except Exception as e:
        return {
            "original_tags": valid_tags,
            "final_tags": valid_tags,  # Return original tags on error
            "error": f"Tag critique failed: {str(e)}",
            "agent": "tag_critic_agent"
        }