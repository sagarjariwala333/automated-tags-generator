from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize LLM with Google Gemini (using faster flash model)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def run_multi_agent_system(task: str) -> str:
    """Run optimized multi-agent system with a single comprehensive call"""
    
    # Single optimized prompt that simulates all agents in one call
    prompt = f"""You are a multi-agent AI system with specialized roles. Process this task through all agents:

Task: {task}

Execute the following agents in sequence and provide their outputs:

1. **Research Agent**: Gather and analyze key information about the task
2. **Writer Agent**: Create well-structured, clear content based on the research
3. **Reviewer Agent**: Review the content and provide final improvements

Format your response as:

=== RESEARCH AGENT ===
[Your research findings here]

=== WRITER AGENT ===
[Your written content here]

=== REVIEWER AGENT ===
[Your review and final version here]

Begin processing now."""
    
    response = llm.invoke(prompt)
    return response.content

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
        # Try to parse as JSON
        metadata = json.loads(response.content)
        return metadata
    except json.JSONDecodeError:
        # If not valid JSON, return raw response
        return {
            "raw_response": response.content,
            "error": "Failed to parse as JSON"
        }

if __name__ == "__main__":
    task = "Research about AI trends, write a summary, and review it"
    result = run_multi_agent_system(task)
    # print(f"\nFinal Result:\n{result}")
