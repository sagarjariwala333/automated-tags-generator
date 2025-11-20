from typing import List, Dict, Any
from tool.ollama_embeddings import get_ollama_embeddings, EMBED_MODEL

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text into overlapping chunks for better context preservation.
    
    Args:
        text: The input text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
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
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks
