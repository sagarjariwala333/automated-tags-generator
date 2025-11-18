from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

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
    
    prompt = f"""You are a Tag Candidate Generator Agent. Based on the provided metadata and content, generate relevant tags.

Metadata:
{json.dumps(metadata, indent=2)}

Content Preview:
{readme_content[:1000]}...

Generate 15-20 candidate tags that:
1. Represent the main topics and technologies
2. Include programming languages, frameworks, and tools
3. Cover use cases and application domains
4. Are specific and relevant
5. Follow standard tagging conventions (lowercase, hyphenated)

Return ONLY a JSON object with this structure:
{{
  "primary_tags": ["tag1", "tag2", "tag3"],
  "technology_tags": ["tech1", "tech2"],
  "domain_tags": ["domain1", "domain2"],
  "feature_tags": ["feature1", "feature2"],
  "all_candidates": ["all", "tags", "here"]
}}"""
    
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
