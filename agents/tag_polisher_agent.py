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
    
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    
    prompt = f"""Polish these tags: {tags_str}
Critique: {critique}

Return JSON: {{"polished_tags": ["tag1", "tag2"]}}"""
    
    response = llm.invoke(prompt)
    
    try:
        result = json.loads(response.content)
        result["agent"] = "tag_polisher_agent"
        return result
    except json.JSONDecodeError:
        return {
            "polished_tags": tags,
            "raw_response": response.content,
            "error": "Failed to parse JSON",
            "agent": "tag_polisher_agent"
        }
