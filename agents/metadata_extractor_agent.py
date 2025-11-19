from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from .prompts import metadata_extractor_prompt

load_dotenv()

# Initialize LLM with Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

class MetadataExtractorResponse(BaseModel):
    title: Optional[str]
    keywords: Optional[List[str]]
    category: Optional[str]
    summary: Optional[str]
    entities: Optional[List[str]]
    sentiment: Optional[str]
    language: Optional[str]
    word_count: Optional[int]


def extract_metadata(content: str) -> dict:
    """Metadata Extractor Agent - Extracts structured metadata from content"""
    prompt = metadata_extractor_prompt.format(content=content)
    try:
        structured_llm = llm.with_structured_output(MetadataExtractorResponse)
        metadata = structured_llm.invoke(prompt)
        return metadata.dict()
    except Exception as e:
        return {
            "error": f"Failed to extract metadata: {str(e)}"
        }
