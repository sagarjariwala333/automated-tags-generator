import numpy as np
from typing import List, Dict, Any, Tuple
from tool.vector_utils import cosine_similarity


def _validate_tag_data(tag_data: List[Dict[str, Any]]) -> bool:
    """Validate tag data structure"""
    if not isinstance(tag_data, list):
        return False
    for item in tag_data:
        if not isinstance(item, dict):
            return False
        if "tag" not in item or "vector" not in item:
            return False
        if not isinstance(item["tag"], str):
            return False
        if not isinstance(item["vector"], np.ndarray):
            return False
    return True


def _validate_chunk_data(chunk_data: List[Dict[str, Any]]) -> bool:
    """Validate chunk data structure"""
    if not isinstance(chunk_data, list):
        return False
    for item in chunk_data:
        if not isinstance(item, dict):
            return False
        if "chunk" not in item or "vector" not in item:
            return False
        if not isinstance(item["vector"], np.ndarray):
            return False
    return True


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
    # Input validation
    if not tag_data:
        print("[similarity_calculator] Warning: tag_data is empty")
        return []
    
    if not readme_chunk_data:
        print("[similarity_calculator] Warning: readme_chunk_data is empty")
        return []
    
    # Validate data structures
    if not _validate_tag_data(tag_data):
        raise ValueError("Invalid tag_data structure. Each item must have 'tag' (str) and 'vector' (np.ndarray)")
    
    if not _validate_chunk_data(readme_chunk_data):
        raise ValueError("Invalid readme_chunk_data structure. Each item must have 'chunk' and 'vector' (np.ndarray)")
    
    # Validate vector dimensions are consistent
    if tag_data and readme_chunk_data:
        tag_dim = tag_data[0]["vector"].shape[0]
        chunk_dim = readme_chunk_data[0]["vector"].shape[0]
        
        if tag_dim != chunk_dim:
            raise ValueError(
                f"Vector dimension mismatch: tag vectors have dimension {tag_dim}, "
                f"but chunk vectors have dimension {chunk_dim}"
            )
    
    
    results = []
    
    # For each tag, calculate similarity with all README chunks
    for tag_item in tag_data:
        tag_name = tag_item["tag"]
        tag_vector = tag_item["vector"]
        
        max_similarity = -1.0
        
        # Calculate similarity with each chunk and find maximum
        for chunk_item in readme_chunk_data:
            chunk_vector = chunk_item["vector"]
            
            try:
                similarity = cosine_similarity(tag_vector, chunk_vector)
                
                # Handle NaN or Inf values
                if np.isnan(similarity) or np.isinf(similarity):
                    print(f"[similarity_calculator] Warning: Invalid similarity score for tag '{tag_name}', skipping")
                    continue
                
                if similarity > max_similarity:
                    max_similarity = similarity
            except Exception as e:
                print(f"[similarity_calculator] Error calculating similarity for tag '{tag_name}': {str(e)}")
                continue
        
        results.append((tag_name, float(max_similarity)))
    
    # Sort by similarity score in descending order (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results
