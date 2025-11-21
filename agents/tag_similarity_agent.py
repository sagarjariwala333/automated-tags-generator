import numpy as np
from typing import List, Dict, Any
from tool.readme_chunking import chunk_text
from tool.ollama_embeddings import get_ollama_embeddings
from tool.similarity_calculator import calculate_tag_chunk_similarity
from tool.semantic_deduplication import deduplicate_tags_semantically


def calculate_tag_similarity(readme_content: str, candidate_tags: List[str]) -> Dict[str, Any]:
    """
    Tag Similarity Agent - Calculates cosine similarity between README chunks and tags using Ollama embeddings.
    
    Uses a chunking strategy to better capture semantic meaning across long README files.
    Each tag is compared against all README chunks and the maximum similarity is used.
    
    Args:
        readme_content: Plain text content from README
        candidate_tags: List of candidate tags from tag_candidate_agent
    
    Returns:
        Dictionary containing similarity scores and analysis
    """
    # Input validation
    if not readme_content or not isinstance(readme_content, str):
        return {
            "success": False,
            "error": "Invalid readme_content: must be a non-empty string",
            "agent": "tag_similarity_agent"
        }
    
    if not readme_content.strip():
        return {
            "success": False,
            "error": "README content is empty after stripping whitespace",
            "agent": "tag_similarity_agent"
        }
    
    if not candidate_tags or not isinstance(candidate_tags, list):
        return {
            "success": False,
            "error": "Invalid candidate_tags: must be a non-empty list",
            "agent": "tag_similarity_agent"
        }
    
    # Filter out non-string tags
    valid_tags = [tag for tag in candidate_tags if isinstance(tag, str) and tag.strip()]
    
    if not valid_tags:
        return {
            "success": False,
            "error": "No valid tags found in candidate_tags after filtering",
            "agent": "tag_similarity_agent"
        }
    
    try:
        # Step 1: Chunk the README content for better semantic coverage
        try:
            readme_chunks = chunk_text(readme_content, chunk_size=1000, overlap=200)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to chunk README content: {str(e)}",
                "agent": "tag_similarity_agent"
            }
        
        if not readme_chunks:
            return {
                "success": False,
                "error": "Failed to chunk README content - no chunks generated",
                "agent": "tag_similarity_agent"
            }
        
        # Step 2: Embed README chunks using Ollama
        try:
            readme_embeddings = get_ollama_embeddings(readme_chunks)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate README embeddings: {str(e)}",
                "agent": "tag_similarity_agent"
            }
        
        if not readme_embeddings or len(readme_embeddings) != len(readme_chunks):
            return {
                "success": False,
                "error": "Embedding count mismatch for README chunks",
                "agent": "tag_similarity_agent"
            }
        
        # Step 3: Embed candidate tags using Ollama
        try:
            tag_embeddings = get_ollama_embeddings(valid_tags)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate tag embeddings: {str(e)}",
                "agent": "tag_similarity_agent"
            }
        
        if not tag_embeddings or len(tag_embeddings) != len(valid_tags):
            return {
                "success": False,
                "error": "Embedding count mismatch for tags",
                "agent": "tag_similarity_agent"
            }
        
        # Step 4: Prepare data structures for similarity calculation
        tag_data = [
            {"tag": tag, "vector": vector}
            for tag, vector in zip(valid_tags, tag_embeddings)
        ]
        
        # Step 4.5: Semantic deduplication - Remove semantically identical tags
        try:
            deduplicated_tags = deduplicate_tags_semantically(tag_data, similarity_threshold=0.8)
        except Exception as e:
            print(f"[tag_similarity_agent] Warning: Deduplication failed, using all tags: {str(e)}")
            deduplicated_tags = valid_tags
        
        # Filter tag_data to only include deduplicated tags
        tag_data_deduplicated = [
            item for item in tag_data if item["tag"] in deduplicated_tags
        ]
        
        # Track how many duplicates were removed
        duplicates_removed = len(valid_tags) - len(deduplicated_tags)
        
        readme_chunk_data = [
            {"chunk": chunk, "vector": vector}
            for chunk, vector in zip(readme_chunks, readme_embeddings)
        ]
        
        # Step 5: Calculate similarity using the similarity calculator tool
        try:
            ranked_tags = calculate_tag_chunk_similarity(tag_data_deduplicated, readme_chunk_data)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate tag similarities: {str(e)}",
                "agent": "tag_similarity_agent"
            }
        
        if not ranked_tags:
            return {
                "success": True,
                "agent": "tag_similarity_agent",
                "method": "ollama_embeddings_with_chunking_and_deduplication",
                "total_tags_input": len(candidate_tags),
                "total_tags_after_dedup": len(deduplicated_tags),
                "duplicates_removed": duplicates_removed,
                "total_chunks": len(readme_chunks),
                "tag_similarities": [],
                "categorized_tags": {
                    "high_relevance": [],
                    "medium_relevance": [],
                    "low_relevance": []
                },
                "statistics": {
                    "average_similarity": 0.0,
                    "max_similarity": 0.0,
                    "min_similarity": 0.0,
                    "high_relevance_count": 0,
                    "medium_relevance_count": 0,
                    "low_relevance_count": 0
                },
                "recommended_tags": []
            }
        
        # Step 6: Format results to match expected output structure
        tag_similarities = [
            {
                "tag": tag,
                "similarity_score": float(score),
                "relevance": "high" if score > 0.7 else "medium" if score > 0.5 else "low"
            }
            for tag, score in ranked_tags
            if float(score) > 0.5
        ]
        
        # Categorize tags by relevance
        high_relevance = [t for t in tag_similarities if t["similarity_score"] > 0.7]
        medium_relevance = [t for t in tag_similarities if 0.5 < t["similarity_score"] <= 0.7]
        low_relevance = [t for t in tag_similarities if t["similarity_score"] <= 0.5]
        
        # Calculate statistics with zero-division protection
        scores = [t["similarity_score"] for t in tag_similarities]
        avg_similarity = float(np.mean(scores)) if scores else 0.0
        max_similarity = float(np.max(scores)) if scores else 0.0
        min_similarity = float(np.min(scores)) if scores else 0.0
        
        return {
            "success": True,
            "agent": "tag_similarity_agent",
            "method": "ollama_embeddings_with_chunking_and_deduplication",
            "total_tags_input": len(candidate_tags),
            "total_tags_after_dedup": len(deduplicated_tags),
            "duplicates_removed": duplicates_removed,
            "total_chunks": len(readme_chunks),
            "tag_similarities": tag_similarities,
            "categorized_tags": {
                "high_relevance": [t["tag"] for t in high_relevance],
                "medium_relevance": [t["tag"] for t in medium_relevance],
                "low_relevance": [t["tag"] for t in low_relevance]
            },
            "statistics": {
                "average_similarity": avg_similarity,
                "max_similarity": max_similarity,
                "min_similarity": min_similarity,
                "high_relevance_count": len(high_relevance),
                "medium_relevance_count": len(medium_relevance),
                "low_relevance_count": len(low_relevance)
            },
            "recommended_tags": [t["tag"] for t in high_relevance[:10]]  # Top 10 most relevant
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Similarity calculation failed: {str(e)}",
            "agent": "tag_similarity_agent"
        }

