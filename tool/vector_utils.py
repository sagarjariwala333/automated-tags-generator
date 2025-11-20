import numpy as np
from typing import List, Dict, Any


def list_to_vector(float_list: List[float]) -> np.ndarray:
    """
    Convert a list of floats to a numpy vector.
    
    Args:
        float_list: List of float values
        
    Returns:
        numpy.ndarray: Vector representation
        
    Example:
        >>> vec = list_to_vector([0.1, 0.2, 0.3])
        >>> print(vec)
        [0.1 0.2 0.3]
    """
    return np.array(float_list)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector (numpy array)
        vec2: Second vector (numpy array)
        
    Returns:
        float: Cosine similarity score between -1 and 1
            1.0 = identical direction
            0.0 = orthogonal (no similarity)
           -1.0 = opposite direction
           
    Example:
        >>> v1 = np.array([1, 0, 0])
        >>> v2 = np.array([1, 0, 0])
        >>> similarity = cosine_similarity(v1, v2)
        >>> print(similarity)
        1.0
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    # Handle zero vectors
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


def rank_by_score(items: List[Dict[str, Any]], score_key: str = "score") -> List[Dict[str, Any]]:
    """
    Sort a list of dictionaries by score in descending order (non-increasing).
    Each dictionary should contain at minimum: a string identifier and a score.
    
    Args:
        items: List of dictionaries containing at least a score field
        score_key: Key name for the score field (default: "score")
        
    Returns:
        List[Dict]: Sorted list in descending order by score (highest first)
        
    Example:
        >>> data = [
        ...     {"tag": "python", "vector": [0.1, 0.2], "score": 0.85},
        ...     {"tag": "javascript", "vector": [0.3, 0.4], "score": 0.92},
        ...     {"tag": "java", "vector": [0.5, 0.6], "score": 0.78}
        ... ]
        >>> ranked = rank_by_score(data)
        >>> print([item["tag"] for item in ranked])
        ['javascript', 'python', 'java']
    """
    if not items:
        return []
    
    # Sort by score in descending order (reverse=True for non-increasing)
    sorted_items = sorted(items, key=lambda x: x.get(score_key, 0), reverse=True)
    
    return sorted_items


def batch_cosine_similarity(
    query_vector: np.ndarray, 
    vectors: List[np.ndarray]
) -> List[float]:
    """
    Calculate cosine similarity between a query vector and multiple vectors efficiently.
    
    Args:
        query_vector: Single query vector
        vectors: List of vectors to compare against
        
    Returns:
        List of similarity scores
        
    Example:
        >>> query = np.array([1, 0, 0])
        >>> vecs = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([1, 1, 0])]
        >>> similarities = batch_cosine_similarity(query, vecs)
        >>> print(similarities)
        [1.0, 0.0, 0.7071067811865475]
    """
    similarities = []
    for vec in vectors:
        sim = cosine_similarity(query_vector, vec)
        similarities.append(sim)
    
    return similarities


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Normalize a vector to unit length (L2 normalization).
    
    Args:
        vector: Input vector
        
    Returns:
        Normalized vector with unit length
        
    Example:
        >>> vec = np.array([3, 4])
        >>> normalized = normalize_vector(vec)
        >>> print(normalized)
        [0.6 0.8]
        >>> print(np.linalg.norm(normalized))
        1.0
    """
    norm = np.linalg.norm(vector)
    
    if norm == 0:
        return vector
    
    return vector / norm


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        float: Euclidean distance
        
    Example:
        >>> v1 = np.array([0, 0])
        >>> v2 = np.array([3, 4])
        >>> dist = euclidean_distance(v1, v2)
        >>> print(dist)
        5.0
    """
    return float(np.linalg.norm(vec1 - vec2))


def dot_product(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate dot product of two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        float: Dot product value
        
    Example:
        >>> v1 = np.array([1, 2, 3])
        >>> v2 = np.array([4, 5, 6])
        >>> result = dot_product(v1, v2)
        >>> print(result)
        32.0
    """
    return float(np.dot(vec1, vec2))
