from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import numpy as np
from typing import List, Dict, Any

load_dotenv()

# Initialize embeddings model
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

def calculate_tag_similarity(readme_content: str, candidate_tags: List[str]) -> Dict[str, Any]:
    """
    Tag Similarity Agent - Calculates cosine similarity between README and tags using embeddings
    
    Args:
        readme_content: Plain text content from README
        candidate_tags: List of candidate tags from tag_candidate_agent
    
    Returns:
        Dictionary containing similarity scores and analysis
    """
    
    try:
        # Embed the README content
        print("[Similarity Agent] Embedding README content...")
        readme_embedding = embeddings_model.embed_query(readme_content[:5000])  # Limit to 5000 chars
        readme_vector = np.array(readme_embedding)
        
        # Embed each tag and calculate similarity
        print(f"[Similarity Agent] Embedding {len(candidate_tags)} tags...")
        tag_similarities = []
        
        for tag in candidate_tags:
            tag_embedding = embeddings_model.embed_query(tag)
            tag_vector = np.array(tag_embedding)
            
            similarity_score = cosine_similarity(readme_vector, tag_vector)
            
            tag_similarities.append({
                "tag": tag,
                "similarity_score": float(similarity_score),
                "relevance": "high" if similarity_score > 0.7 else "medium" if similarity_score > 0.5 else "low"
            })
        
        # Sort by similarity score (descending)
        tag_similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Categorize tags
        high_relevance = [t for t in tag_similarities if t["similarity_score"] > 0.7]
        medium_relevance = [t for t in tag_similarities if 0.5 < t["similarity_score"] <= 0.7]
        low_relevance = [t for t in tag_similarities if t["similarity_score"] <= 0.5]
        
        # Calculate statistics
        scores = [t["similarity_score"] for t in tag_similarities]
        avg_similarity = np.mean(scores) if scores else 0.0
        max_similarity = np.max(scores) if scores else 0.0
        min_similarity = np.min(scores) if scores else 0.0
        
        return {
            "success": True,
            "agent": "tag_similarity_agent",
            "method": "cosine_similarity_with_embeddings",
            "total_tags": len(candidate_tags),
            "tag_similarities": tag_similarities,
            "categorized_tags": {
                "high_relevance": [t["tag"] for t in high_relevance],
                "medium_relevance": [t["tag"] for t in medium_relevance],
                "low_relevance": [t["tag"] for t in low_relevance]
            },
            "statistics": {
                "average_similarity": float(avg_similarity),
                "max_similarity": float(max_similarity),
                "min_similarity": float(min_similarity),
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
