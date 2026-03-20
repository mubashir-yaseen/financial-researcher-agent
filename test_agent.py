from agent import ResearcherAgent
import json
from dotenv import load_dotenv
import sys
import os

# Ensure current directory is in search path
sys.path.append(os.getcwd())

load_dotenv()

def test_full_flow():
    agent = ResearcherAgent()
    print("Starting Research...")
    try:
        result = agent.run("PSX crash analysis March 2026")
        print("\nResearch Complete!")
        # Use ensure_ascii=True to avoid printing non-ascii characters to console
        print(json.dumps(result, indent=2, ensure_ascii=True))
    except Exception as e:
        print(f"\nResearch Failed: {e}")

if __name__ == "__main__":
    test_full_flow()
