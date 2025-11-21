from typing import List, Dict, Any
from tool.ollama_embeddings import get_ollama_embeddings, EMBED_MODEL

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text into overlapping chunks for better context preservation.
    
    Args:
        text: The input text to chunk
        chunk_size: Maximum characters per chunk (must be > 0)
        overlap: Number of characters to overlap between chunks (must be >= 0 and < chunk_size)
        
    Returns:
        List of text chunks
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Input validation
    if not isinstance(text, str):
        raise ValueError(f"Text must be a string, got {type(text)}")
    
    if not text or not text.strip():
        return []
    
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got {overlap}")
    
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size})")
    
    text = text.strip()
    text_length = len(text)
    
    # If text is smaller than chunk_size, return it as a single chunk
    if text_length <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < text_length:
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence or word boundary
        if end < text_length:
            # Look for sentence endings (., !, ?) within the last 100 chars
            last_period = text.rfind('.', start, end)
            last_exclaim = text.rfind('!', start, end)
            last_question = text.rfind('?', start, end)
            
            sentence_end = max(last_period, last_exclaim, last_question)
            
            if sentence_end > start + (chunk_size // 2):  # Only break if we're past halfway
                end = sentence_end + 1
            else:
                # Fall back to word boundary
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < text_length else text_length
        
        # Prevent infinite loop in edge cases
        if start <= 0 or (end >= text_length and start >= text_length):
            break
    
    return chunks
