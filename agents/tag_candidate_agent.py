from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json
from .prompts import tag_candidate_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def generate_tag_candidates(metadata: dict, readme_content: str) -> dict:
    """
    Tag Candidate Agent - Generates potential tags based on metadata and content
    
    Args:
        metadata: Extracted metadata from previous step
        readme_content: Plain text content from README
    
    Returns:
        Dictionary containing candidate tags
    """
    prompt = tag_candidate_prompt.format(
        metadata=json.dumps(metadata, indent=2),
        content_preview=readme_content[:1000]
    )
    response = llm.invoke(prompt)
    
    try:
        # Clean the response - remove markdown code blocks if present
        content = response.content.strip()
        
        # Remove ```json and ``` markers
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        
        content = content.strip()
        
        # Parse JSON
        candidates = json.loads(content)
        return {
            "success": True,
            "candidates": candidates,
            "total_count": len(candidates.get("all_candidates", []))
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse tag candidates: {str(e)}",
            "raw_response": response.content
        }
