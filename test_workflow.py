
import os
import sys
from dotenv import load_dotenv
import json

# Add the current directory to sys.path so we can import modules
sys.path.append(os.getcwd())

from workflows.workflow import run_simple_analysis_workflow

def test_workflow():
    print("Starting workflow test...")
    # Use a known repo
    owner = "sagarjariwala333"
    repo = "automated-tags-generator"
    
    try:
        result = run_simple_analysis_workflow(owner, repo)
        print("Workflow Result:")
        print(json.dumps(result, indent=2))
        
        if result.get("success"):
            print("\nSUCCESS: Workflow completed successfully.")
        else:
            print("\nFAILURE: Workflow failed.")
            
    except Exception as e:
        print("Caught exception:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_workflow()
