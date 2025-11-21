import requests
import time
import numpy as np
from typing import List

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"
MAX_BATCH_SIZE = 100  # Limit batch size to avoid overwhelming Ollama


def _check_ollama_health(timeout: int = 5) -> bool:
    """Check if Ollama service is running"""
    try:
        health_url = "http://localhost:11434/api/tags"
        response = requests.get(health_url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def get_ollama_embeddings(texts: List[str], max_retries: int = 3, timeout: int = 30) -> List[np.ndarray]:
    """
    Calls Ollama's embedding API to generate embeddings for multiple texts.
    
    Args:
        texts: List of text strings to embed
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 30)
        
    Returns:
        List of numpy array vectors (each is a np.ndarray)
        
    Raises:
        Exception: If the API call fails after all retries
    """
    # Input validation
    if not texts:
        raise Exception("Input texts list is empty")
    
    if not isinstance(texts, list):
        raise Exception(f"Input must be a list, got {type(texts)}")
    
    # Filter out empty strings and validate
    valid_texts = []
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            print(f"[ollama_embeddings] Warning: Skipping non-string item at index {i}")
            continue
        if text.strip():
            valid_texts.append(text)
        else:
            print(f"[ollama_embeddings] Warning: Skipping empty string at index {i}")
    
    if not valid_texts:
        raise Exception("No valid text strings found in input after filtering")
    
    # Check batch size
    if len(valid_texts) > MAX_BATCH_SIZE:
        print(f"[ollama_embeddings] Warning: Batch size {len(valid_texts)} exceeds max {MAX_BATCH_SIZE}, processing in chunks")
        # Process in chunks
        all_embeddings = []
        for i in range(0, len(valid_texts), MAX_BATCH_SIZE):
            chunk = valid_texts[i:i + MAX_BATCH_SIZE]
            chunk_embeddings = get_ollama_embeddings(chunk, max_retries, timeout)
            all_embeddings.extend(chunk_embeddings)
        return all_embeddings
    
    # Health check before processing
    if not _check_ollama_health():
        raise Exception(
            "Ollama service is not running or unreachable. "
            "Please ensure Ollama is installed and running on http://localhost:11434. "
            "You can start it with: 'ollama serve'"
        )
    
    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            payload = {
                "model": EMBED_MODEL,
                "input": valid_texts
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate response structure
            if not isinstance(data, dict) or "embeddings" not in data:
                raise Exception("Invalid response format from Ollama API")
            
            embeddings_data = data["embeddings"]
            
            # Validate embeddings is a list
            if not isinstance(embeddings_data, list):
                raise Exception("Embeddings data is not a list")
            
            # Validate we got the right number of embeddings
            if len(embeddings_data) != len(valid_texts):
                raise Exception(
                    f"Expected {len(valid_texts)} embeddings but got {len(embeddings_data)}"
                )
            
            # Convert each embedding list to numpy array and validate
            embeddings = []
            expected_dim = None
            
            for i, emb in enumerate(embeddings_data):
                if not isinstance(emb, list):
                    raise Exception(f"Embedding at index {i} is not a list")
                
                # Convert to numpy array
                emb_array = np.array(emb)
                
                # Validate dimensions are consistent
                if expected_dim is None:
                    expected_dim = len(emb)
                elif len(emb) != expected_dim:
                    raise Exception(
                        f"Inconsistent embedding dimensions: expected {expected_dim}, got {len(emb)} at index {i}"
                    )
                
                # Check for NaN or Inf values
                if np.any(np.isnan(emb_array)) or np.any(np.isinf(emb_array)):
                    raise Exception(f"Embedding at index {i} contains NaN or Inf values")
                
                embeddings.append(emb_array)
            
            return embeddings
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[ollama_embeddings] Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise Exception(
                f"Ollama embedding API timeout after {max_retries} attempts. "
                f"The request may be too large or Ollama may be overloaded."
            )
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[ollama_embeddings] Connection error on attempt {attempt + 1}, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise Exception(
                "Cannot connect to Ollama service. "
                "Please ensure Ollama is running on http://localhost:11434. "
                "You can start it with: 'ollama serve'"
            )
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[ollama_embeddings] Request error on attempt {attempt + 1}, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise Exception(f"Ollama embedding API request failed after {max_retries} attempts: {str(e)}")
            
        except Exception as e:
            # Don't retry on validation errors or unexpected errors
            raise Exception(f"Ollama embedding API failed: {str(e)}")
    
    # Should not reach here
    raise Exception("Maximum retries exceeded")
