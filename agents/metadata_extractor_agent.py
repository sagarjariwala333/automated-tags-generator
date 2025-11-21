from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from .prompts import metadata_extractor_prompt

load_dotenv()

# Initialize LLM with Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class MetadataExtractorResponse(BaseModel):
    title: Optional[str]
    keywords: Optional[List[str]]
    category: Optional[str]
    summary: Optional[str]
    entities: Optional[List[str]]
    sentiment: Optional[str]
    language: Optional[str]
    word_count: Optional[int]


def extract_metadata(content: str) -> dict:
    """Metadata Extractor Agent - Extracts structured metadata from content"""
    # Input validation
    if not content or not isinstance(content, str):
        return {
            "error": "Invalid content parameter: must be a non-empty string",
            "agent": "metadata_extractor_agent"
        }
    
    if not content.strip():
        return {
            "error": "Content is empty after stripping whitespace",
            "agent": "metadata_extractor_agent"
        }
    
    # Check content length and truncate if necessary (LLM token limits)
    MAX_CONTENT_LENGTH = 50000  # Reasonable limit for most LLMs
    truncated = False
    
    if len(content) > MAX_CONTENT_LENGTH:
        print(f"[metadata_extractor_agent] Warning: Content length {len(content)} exceeds max {MAX_CONTENT_LENGTH}, truncating")
        content = content[:MAX_CONTENT_LENGTH]
        truncated = True
    
    prompt = metadata_extractor_prompt.format(content=content)
    
    try:
        structured_llm = llm.with_structured_output(MetadataExtractorResponse)
        metadata = structured_llm.invoke(prompt)
        
        if not metadata:
            return {
                "error": "LLM returned empty metadata",
                "agent": "metadata_extractor_agent"
            }
        
        result = metadata.dict()
        result["agent"] = "metadata_extractor_agent"
        
        if truncated:
            result["warning"] = "Content was truncated due to length"
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to extract metadata: {str(e)}",
            "agent": "metadata_extractor_agent"
        }
