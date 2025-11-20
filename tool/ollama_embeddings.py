import requests
import numpy as np
from typing import List

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


def get_ollama_embeddings(texts: List[str]) -> List[np.ndarray]:
    """
    Calls Ollama's embedding API to generate embeddings for multiple texts.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of numpy array vectors (each is a np.ndarray)
        
    Raises:
        Exception: If the API call fails
    """
    try:
        payload = {
            "model": EMBED_MODEL,
            "input": texts
        }
        
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        
        data = response.json()
        # Convert each embedding list to numpy array
        embeddings = [np.array(emb) for emb in data["embeddings"]]
        return embeddings
        
    except Exception as e:
        raise Exception(f"Ollama embedding API failed: {e}")
