from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from tool.readme_chunking import chunk_text
from .prompts import chunk_tag_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Pydantic model for structured output
class ChunkTags(BaseModel):
    tags: List[str]


def generate_tag_candidates(readme_content: str) -> List[str]:
    """
    Tag Candidate Agent - Generates potential tags by chunking README and analyzing each chunk.
    
    Args:
        readme_content: Full README text content
        
    Returns:
        List of unique tag strings
    """
    try:
        # Step 1: Chunk the README content
        chunks = chunk_text(readme_content, chunk_size=1000, overlap=200)
        
        if not chunks:
            return []
        
        # Create structured LLM
        structured_llm = llm.with_structured_output(ChunkTags)
        
        all_tags = []
        
        # Step 2: Generate tags from each chunk using structured output
        for chunk in chunks:
            try:
                prompt = chunk_tag_prompt.format(chunk=chunk)
                response = structured_llm.invoke(prompt)
                
                # Extract tags from structured response
                if response and hasattr(response, 'tags'):
                    all_tags.extend(response.tags)
                        
            except Exception as e:
                # Skip this chunk if parsing fails
                continue
        
        # Step 3: Deduplicate tags (case-insensitive)
        unique_tags = []
        seen_tags_lower = set()
        
        for tag in all_tags:
            if isinstance(tag, str):
                tag_lower = tag.lower().strip()
                if tag_lower and tag_lower not in seen_tags_lower:
                    seen_tags_lower.add(tag_lower)
                    unique_tags.append(tag_lower)
        
        return unique_tags
        
    except Exception as e:
        # Return empty list on error
        return []
