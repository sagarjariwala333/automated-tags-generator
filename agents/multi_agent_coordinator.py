from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM with Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def run_multi_agent_system(task: str) -> str:
    """Run optimized multi-agent system with a single comprehensive call"""
    # Input validation
    if not task or not isinstance(task, str):
        return "Error: Invalid task parameter - must be a non-empty string"
    
    if not task.strip():
        return "Error: Task is empty after stripping whitespace"
    
    # Check task length
    MAX_TASK_LENGTH = 10000
    if len(task) > MAX_TASK_LENGTH:
        print(f"[multi_agent_coordinator] Warning: Task length {len(task)} exceeds max {MAX_TASK_LENGTH}, truncating")
        task = task[:MAX_TASK_LENGTH]
    
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
    
    try:
        response = llm.invoke(prompt)
        
        if not response or not hasattr(response, 'content'):
            return "Error: LLM returned empty or invalid response"
        
        if not response.content or not response.content.strip():
            return "Error: LLM response content is empty"
        
        return response.content
        
    except Exception as e:
        return f"Error: Multi-agent system failed - {str(e)}"
