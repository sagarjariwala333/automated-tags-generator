import numpy as np
from typing import List, Dict, Any
from tool.vector_utils import cosine_similarity


def deduplicate_tags_semantically(
    tag_data: List[Dict[str, Any]], 
    similarity_threshold: float = 0.95
) -> List[str]:
    """
    Semantically deduplicate tags by comparing their embeddings.
    Removes tags that are semantically identical (very high cosine similarity).
    
    Args:
        tag_data: List of dictionaries, each containing:
            - "tag": str (tag name)
            - "vector": np.ndarray (embedding vector)
        similarity_threshold: Cosine similarity threshold above which tags are considered duplicates
                            (default: 0.95 means 95% similar or more)
        
    Returns:
        List of unique tag strings (deduplicated)
        
    Example:
        >>> tags = [
        ...     {"tag": "javascript", "vector": np.array([0.1, 0.2, 0.3])},
        ...     {"tag": "js", "vector": np.array([0.11, 0.21, 0.31])},  # Very similar to javascript
        ...     {"tag": "python", "vector": np.array([0.9, 0.8, 0.7])}
        ... ]
        >>> result = deduplicate_tags_semantically(tags, similarity_threshold=0.95)
        >>> print(result)
        ['javascript', 'python']  # 'js' removed as duplicate of 'javascript'
    """
    # Input validation
    if not tag_data:
        return []
    
    if not isinstance(tag_data, list):
        raise ValueError(f"tag_data must be a list, got {type(tag_data)}")
    
    if not (0.0 <= similarity_threshold <= 1.0):
        raise ValueError(f"similarity_threshold must be between 0 and 1, got {similarity_threshold}")
    
    # Validate data structure
    for i, item in enumerate(tag_data):
        if not isinstance(item, dict):
            raise ValueError(f"tag_data[{i}] must be a dictionary")
        if "tag" not in item or "vector" not in item:
            raise ValueError(f"tag_data[{i}] must have 'tag' and 'vector' keys")
        if not isinstance(item["vector"], np.ndarray):
            raise ValueError(f"tag_data[{i}]['vector'] must be a numpy array")
    
    # Track which tags to keep
    unique_tags = []
    seen_indices = set()
    
    for i, tag_item in enumerate(tag_data):
        if i in seen_indices:
            continue
        
        # Keep this tag
        tag_name = tag_item["tag"]
        tag_vector = tag_item["vector"]
        unique_tags.append(tag_name)
        seen_indices.add(i)
        
        # Compare with all remaining tags
        for j in range(i + 1, len(tag_data)):
            if j in seen_indices:
                continue
            
            other_vector = tag_data[j]["vector"]
            
            try:
                similarity = cosine_similarity(tag_vector, other_vector)
                
                # Handle NaN values
                if np.isnan(similarity) or np.isinf(similarity):
                    print(f"[semantic_deduplication] Warning: Invalid similarity between '{tag_name}' and '{tag_data[j]["tag"]}', skipping")
                    continue
                
                # If very similar, mark as duplicate (don't keep)
                if similarity >= similarity_threshold:
                    seen_indices.add(j)
            except Exception as e:
                print(f"[semantic_deduplication] Error comparing tags: {str(e)}")
                continue
    
    return unique_tags


def deduplicate_tags_with_priority(
    tag_data: List[Dict[str, Any]], 
    similarity_threshold: float = 0.95,
    priority_key: str = "score"
) -> List[str]:
    """
    Semantically deduplicate tags with priority based on a score.
    When duplicates are found, keeps the one with the highest score.
    
    Args:
        tag_data: List of dictionaries, each containing:
            - "tag": str (tag name)
            - "vector": np.ndarray (embedding vector)
            - priority_key: float (score/priority value, optional)
        similarity_threshold: Cosine similarity threshold for duplicates
        priority_key: Key name for the priority score (default: "score")
        
    Returns:
        List of unique tag strings (deduplicated, keeping highest priority)
        
    Example:
        >>> tags = [
        ...     {"tag": "javascript", "vector": np.array([0.1, 0.2]), "score": 0.8},
        ...     {"tag": "js", "vector": np.array([0.11, 0.21]), "score": 0.6},
        ...     {"tag": "python", "vector": np.array([0.9, 0.8]), "score": 0.9}
        ... ]
        >>> result = deduplicate_tags_with_priority(tags)
        >>> print(result)
        ['javascript', 'python']  # Kept 'javascript' over 'js' due to higher score
    """
    # Input validation
    if not tag_data:
        return []
    
    if not isinstance(tag_data, list):
        raise ValueError(f"tag_data must be a list, got {type(tag_data)}")
    
    if not (0.0 <= similarity_threshold <= 1.0):
        raise ValueError(f"similarity_threshold must be between 0 and 1, got {similarity_threshold}")
    
    # Validate data structure
    for i, item in enumerate(tag_data):
        if not isinstance(item, dict):
            raise ValueError(f"tag_data[{i}] must be a dictionary")
        if "tag" not in item or "vector" not in item:
            raise ValueError(f"tag_data[{i}] must have 'tag' and 'vector' keys")
    
    # Sort by priority (highest first) if priority key exists
    sorted_tags = sorted(
        tag_data, 
        key=lambda x: x.get(priority_key, 0), 
        reverse=True
    )
    
    unique_tags = []
    seen_indices = set()
    
    for i, tag_item in enumerate(sorted_tags):
        if i in seen_indices:
            continue
        
        tag_name = tag_item["tag"]
        tag_vector = tag_item["vector"]
        unique_tags.append(tag_name)
        seen_indices.add(i)
        
        # Mark similar tags as duplicates
        for j in range(i + 1, len(sorted_tags)):
            if j in seen_indices:
                continue
            
            other_vector = sorted_tags[j]["vector"]
            
            try:
                similarity = cosine_similarity(tag_vector, other_vector)
                
                # Handle NaN values
                if np.isnan(similarity) or np.isinf(similarity):
                    continue
                
                if similarity >= similarity_threshold:
                    seen_indices.add(j)
            except Exception as e:
                print(f"[semantic_deduplication] Error in priority deduplication: {str(e)}")
                continue
    
    return unique_tags


def get_semantic_clusters(
    tag_data: List[Dict[str, Any]], 
    similarity_threshold: float = 0.95
) -> List[List[str]]:
    """
    Group semantically similar tags into clusters.
    Useful for understanding which tags are considered duplicates.
    
    Args:
        tag_data: List of dictionaries with "tag" and "vector"
        similarity_threshold: Similarity threshold for clustering
        
    Returns:
        List of clusters, where each cluster is a list of similar tag names
        
    Example:
        >>> tags = [
        ...     {"tag": "javascript", "vector": np.array([0.1, 0.2])},
        ...     {"tag": "js", "vector": np.array([0.11, 0.21])},
        ...     {"tag": "python", "vector": np.array([0.9, 0.8])},
        ...     {"tag": "py", "vector": np.array([0.91, 0.81])}
        ... ]
        >>> clusters = get_semantic_clusters(tags)
        >>> print(clusters)
        ['javascript', 'react', 'frontend', 'ui']
    """
    # Input validation
    if not tag_data:
        return []
    
    if not isinstance(tag_data, list):
        raise ValueError(f"tag_data must be a list, got {type(tag_data)}")
    
    if not (0.0 <= similarity_threshold <= 1.0):
        raise ValueError(f"similarity_threshold must be between 0 and 1, got {similarity_threshold}")
    
    # Validate data structure
    for i, item in enumerate(tag_data):
        if not isinstance(item, dict):
            raise ValueError(f"tag_data[{i}] must be a dictionary")
        if "tag" not in item or "vector" not in item:
            raise ValueError(f"tag_data[{i}] must have 'tag' and 'vector' keys")
        if not isinstance(item["vector"], np.ndarray):
            raise ValueError(f"tag_data[{i}]['vector'] must be a numpy array")
            
    clusters = []
    assigned = set()
    
    for i, tag_item in enumerate(tag_data):
        if i in assigned:
            continue
        
        # Start a new cluster
        cluster = [tag_item["tag"]]
        assigned.add(i)
        tag_vector = tag_item["vector"]
        
        # Find all similar tags
        for j in range(i + 1, len(tag_data)):
            if j in assigned:
                continue
            
            other_vector = tag_data[j]["vector"]
            
            try:
                similarity = cosine_similarity(tag_vector, other_vector)
                
                # Handle NaN values
                if np.isnan(similarity) or np.isinf(similarity):
                    continue
                
                if similarity >= similarity_threshold:
                    cluster.append(tag_data[j]["tag"])
                    assigned.add(j)
            except Exception as e:
                print(f"[semantic_deduplication] Error in clustering: {str(e)}")
                continue
        
        clusters.append(cluster)
    
    return clusters
