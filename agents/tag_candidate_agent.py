from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from tool.readme_chunking import chunk_text
from .prompts import chunk_tag_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
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
    # Input validation
    if not readme_content or not isinstance(readme_content, str):
        print("[tag_candidate_agent] Error: Invalid readme_content")
        return []
    
    if not readme_content.strip():
        print("[tag_candidate_agent] Error: README content is empty")
        return []
    
    try:
        # Step 1: Chunk the README content
        try:
            chunks = chunk_text(readme_content, chunk_size=1000, overlap=200)
        except Exception as e:
            print(f"[tag_candidate_agent] Error chunking text: {str(e)}")
            return []
        
        if not chunks:
            print("[tag_candidate_agent] Error: No chunks generated from README")
            return []
        
        # Create structured LLM (moved here to avoid re-creation in loop)
        structured_llm = llm.with_structured_output(TagCandidateResponse)
        
        all_tags = []
        failed_chunks = 0
        
        # Step 2: Analyze each chunk with LLM
        for i, chunk in enumerate(chunks):
            try:
                # Using the correct prompt variable as per the original code's import
                prompt = chunk_tag_prompt.format(chunk=chunk) 
                
                response = structured_llm.invoke(prompt)
                
                # Validate response
                if not response:
                    print(f"[tag_candidate_agent] Warning: Empty response for chunk {i+1}")
                    failed_chunks += 1
                    continue
                
                # Extract tags from response
                chunk_tags = response.tags if hasattr(response, 'tags') else []
                
                # Validate tags are strings
                valid_chunk_tags = [
                    tag for tag in chunk_tags 
                    if isinstance(tag, str) and tag.strip()
                ]
                
                all_tags.extend(valid_chunk_tags)
                
            except json.JSONDecodeError as e:
                print(f"[tag_candidate_agent] JSON parse error for chunk {i+1}: {str(e)}")
                failed_chunks += 1
                continue
            except Exception as e:
                print(f"[tag_candidate_agent] Error processing chunk {i+1}: {str(e)}")
                failed_chunks += 1
                continue
        
        # Log if many chunks failed
        if failed_chunks > len(chunks) / 2:
            print(f"[tag_candidate_agent] Warning: {failed_chunks}/{len(chunks)} chunks failed to process")
        
        # Step 3: Deduplicate tags (case-insensitive)
            if isinstance(tag, str):
                tag_lower = tag.lower().strip()
                if tag_lower and tag_lower not in seen_tags_lower:
                    seen_tags_lower.add(tag_lower)
                    unique_tags.append(tag_lower)
        
        return unique_tags
        
    except Exception as e:
        # Return empty list on error
        return []
