from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def critique_tags(tags: list, context: str = "") -> dict:
    """Tag Critic Agent - Evaluates tag quality"""
    
    tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
    
    prompt = f"""Critique these tags: {tags_str}
Context: {context}

Evaluate relevance, clarity, and quality."""
    
    response = llm.invoke(prompt)
    
    return {
        "original_tags": tags,
        "critique": response.content,
        "agent": "tag_critic_agent"
    }
