import numpy as np
from typing import List, Dict, Any, Tuple
from tool.vector_utils import cosine_similarity


def calculate_tag_chunk_similarity(
    tag_data: List[Dict[str, np.ndarray]],
    readme_chunk_data: List[Dict[str, np.ndarray]]
) -> List[Tuple[str, np.ndarray]]:
    """
    Calculate cosine similarity between tag embeddings and chunked README embeddings.
    For each tag, computes similarity with all README chunks and uses the maximum similarity.
    Returns ranked list of tags by semantic similarity score.
    
    Args:
        tag_data: List of dictionaries, each containing:
            - "tag": str (tag name)
            - "vector": np.ndarray (embedding vector)
        readme_chunk_data: List of dictionaries, each containing:
            - "chunk": str (text chunk)
            - "vector": np.ndarray (embedding vector)
        
    Returns:
        List of tuples (tag, score) sorted by score in descending order
        
    Example:
        >>> tags = [
        ...     {"tag": "python", "vector": np.array([0.1, 0.2])},
        ...     {"tag": "javascript", "vector": np.array([0.3, 0.4])}
        ... ]
        >>> chunks = [
        ...     {"chunk": "Python is great", "vector": np.array([0.15, 0.25])},
        ...     {"chunk": "JS is cool", "vector": np.array([0.35, 0.45])}
        ... ]
        >>> result = calculate_tag_chunk_similarity(tags, chunks)
        >>> print(result)
        [("javascript", 0.95), ("python", 0.92)]
    """
    if not tag_data:
        return []
    
    if not readme_chunk_data:
        return []
    
    results = []
    
    # For each tag, calculate similarity with all README chunks
    for tag_item in tag_data:
        tag_name = tag_item["tag"]
        tag_vector = tag_item["vector"]
        
        max_similarity = -1.0
        
        # Calculate similarity with each chunk and find maximum
        for chunk_item in readme_chunk_data:
            chunk_vector = chunk_item["vector"]
            similarity = cosine_similarity(tag_vector, chunk_vector)
            
            if similarity > max_similarity:
                max_similarity = similarity
        
        results.append((tag_name, float(max_similarity)))
    
    # Sort by similarity score in descending order (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results
