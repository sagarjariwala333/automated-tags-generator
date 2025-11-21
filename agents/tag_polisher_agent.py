from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def polish_tags(tags: list, critique: str = "") -> dict:
    """Tag Polisher Agent - Refines tags"""
    # Input validation
    if not tags or not isinstance(tags, list):
        return {
            "polished_tags": [],
            "error": "Invalid tags parameter: must be a non-empty list",
            "agent": "tag_polisher_agent"
        }
    
    # Filter and validate tags
    valid_tags = [tag for tag in tags if isinstance(tag, str) and tag.strip()]
    
    if not valid_tags:
        return {
            "polished_tags": [],
            "error": "No valid string tags found in input",
            "agent": "tag_polisher_agent"
        }
    
    tags_str = ", ".join(valid_tags)
    
    prompt = f"""Polish these tags: {tags_str}
Critique: {critique}

Return JSON: {{"polished_tags": ["tag1", "tag2"]}}"""
    
    try:
        response = llm.invoke(prompt)
        
        if not response or not hasattr(response, 'content'):
            return {
                "polished_tags": valid_tags,
                "error": "Empty or invalid LLM response",
                "agent": "tag_polisher_agent"
            }
        
        # Try to parse JSON response
        try:
            result = json.loads(response.content)
            
            # Validate result structure
            if not isinstance(result, dict) or "polished_tags" not in result:
                return {
                    "polished_tags": valid_tags,
                    "raw_response": response.content,
                    "error": "Invalid JSON structure: missing 'polished_tags' key",
                    "agent": "tag_polisher_agent"
                }
            
            # Validate polished_tags is a list
            if not isinstance(result["polished_tags"], list):
                return {
                    "polished_tags": valid_tags,
                    "raw_response": response.content,
                    "error": "Invalid JSON structure: 'polished_tags' must be a list",
                    "agent": "tag_polisher_agent"
                }
            
            # Filter out non-string items
            polished = [tag for tag in result["polished_tags"] if isinstance(tag, str) and tag.strip()]
            
            result["polished_tags"] = polished if polished else valid_tags
            result["agent"] = "tag_polisher_agent"
            return result
            
        except json.JSONDecodeError as e:
            return {
                "polished_tags": valid_tags,
                "raw_response": response.content,
                "error": f"Failed to parse JSON: {str(e)}",
                "agent": "tag_polisher_agent"
            }
            
    except Exception as e:
        return {
            "polished_tags": valid_tags,
            "error": f"Tag polishing failed: {str(e)}",
            "agent": "tag_polisher_agent"
        }
