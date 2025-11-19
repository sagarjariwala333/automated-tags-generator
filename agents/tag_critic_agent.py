from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import json
import re
from .prompts import tag_critic_eval_prompt, tag_critic_revise_prompt
from tool.tag_critic_rubric import TagCriticResponse, TagEvaluation, RevisionModel, IterationLog

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def critique_tags(tags: list, context: str = "", threshold: float = 0.7, max_iterations: int = 3) -> dict:
    """Tag Critic Agent - Evaluates tag quality and attempts improvement"""
    try:
        model_result = evaluate_tags_rubric(
            tags,
            context=context,
            threshold=threshold,
            max_iterations=max_iterations,
            llm=llm,
            tag_critic_eval_prompt=tag_critic_eval_prompt,
            tag_critic_revise_prompt=tag_critic_revise_prompt
        )
        print("model result...", model_result)
        return model_result.dict()
    except Exception as e:
        return {
            "original_tags": tags,
            "final_tags": [],
            "error": str(e),
            "agent": "tag_critic_agent"
        }