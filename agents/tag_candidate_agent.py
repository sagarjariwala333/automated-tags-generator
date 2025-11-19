from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import json
from .prompts import tag_candidate_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class TagCandidates(BaseModel):
    primary_tags: List[str]
    technology_tags: List[str]
    domain_tags: List[str]
    feature_tags: List[str]
    all_candidates: List[str]

def generate_tag_candidates(metadata: dict, readme_content: str) -> dict:
    """
    Tag Candidate Agent - Generates potential tags based on metadata and content
    Returns a structured Pydantic model.
    """
    prompt = tag_candidate_prompt.format(
        metadata=json.dumps(metadata, indent=2),
        content_preview=readme_content[:1000]
    )
    try:
        structured_llm = llm.with_structured_output(TagCandidates)
        candidates = structured_llm.invoke(prompt)
        return {
            "success": True,
            "candidates": candidates.dict(),
            "total_count": len(candidates.all_candidates)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse tag candidates: {str(e)}"
        }
