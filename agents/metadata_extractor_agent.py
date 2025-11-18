from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize LLM with Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def extract_metadata(content: str) -> dict:
    """Metadata Extractor Agent - Extracts structured metadata from content"""
    
    prompt = f"""You are a Metadata Extractor Agent. Analyze the following content and extract structured metadata.

Content: {content}

Extract and return the following metadata in JSON format:
- title: Main title or topic
- keywords: List of 5-10 relevant keywords
- category: Primary category (e.g., Technology, Business, Science, etc.)
- summary: Brief 2-3 sentence summary
- entities: List of important entities (people, organizations, locations)
- sentiment: Overall sentiment (positive, negative, neutral)
- language: Detected language
- word_count: Approximate word count

Return ONLY valid JSON, no additional text."""
    
    response = llm.invoke(prompt)
    
    try:
        # Clean the response - remove markdown code blocks if present
        content = response.content.strip()
        
        # Remove ```json and ``` markers
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        
        content = content.strip()
        
        # Try to parse as JSON
        metadata = json.loads(content)
        return metadata
    except json.JSONDecodeError as e:
        # If not valid JSON, return raw response
        return {
            "raw_response": response.content,
            "error": f"Failed to parse as JSON: {str(e)}"
        }
