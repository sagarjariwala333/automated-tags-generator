
import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path so we can import modules
sys.path.append(os.getcwd())

from agents.tag_critic_agent import critique_tags

def reproduce():
    print("Starting reproduction...")
    tags = ["python", "coding", "ai", "bad_tag_example"]
    context = "This is a python script about AI coding."
    
    try:
        result = critique_tags(tags, context=context)
        print("Result:", result)
    except Exception as e:
        print("Caught exception:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
