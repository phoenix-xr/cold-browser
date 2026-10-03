import os
import sys
import json
import time
from laya import Router

url = "google.co.in"
query = "click on the search bar and search for Justin Bieber"

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def read_accessibility_tree(filepath="a11y_tree_log.txt"):
    """Reads the accessibility tree from a text file."""
    if not os.path.exists(filepath):
        print(f"Error: Could not find {filepath}")
        return None
        
    with open(filepath, 'r', encoding='utf-8') as f:
        tree_content = f.read()
        
    return tree_content

if __name__ == "__main__":
    # Using the google tree since it has a lot of elements
    file_to_read = "google_a11y_tree.txt" 
    
    print(f"Reading from {file_to_read}...\n")
    tree = read_accessibility_tree(file_to_read)
    
    if tree:
        print(f"Successfully loaded tree with {len(tree)} characters.\n")
        
        # preparing state
        state = f"""
        User is on the {url}. User wants to {query}.

        Past actions: 
            {{
                "element_id":"9 : Search combobox",
                "action":"CLICK"
            }}
        """

        print("Initializing Laya Router...")
        router = Router(preload=True)
        
        import re
        element_choices = {}
        for line in tree.split('\n'):
            match = re.search(r'\[(\d+)\]\s+([a-zA-Z0-9]+)(?:\s+"([^"]*)")?', line)
            if match:
                idx, role, name = match.groups()
                element_choices[str(idx)] = f"{role} {name if name else ''}".strip()
                
        # Define questions to ask about the DOM tree
        questions = {
            "element_id": {
                "type": "choice",
                "instructions": "Which next element ID should the user interact with next to accomplish the goal?",
                "criteria": element_choices
            }, 
            "action": {
                "type": "choice",
                "instructions": "Which action should be performed on the selected element?",
                "criteria": [
                    "CLICK",
                    "TYPE_TEXT",
                    "SELECT",
                    "SCROLL_UP",
                    "SCROLL_DOWN",
                    "WAIT",
                    "DONE",
                    "BLOCKED"
                ]
            }
        }
        
        print("Sending state to Laya...")
        start = time.time()
        result = router.predict(state, questions)
        end = time.time()
        
        print(f"\nPrediction took {end - start:.4f} seconds")
        print("\nPrediction Result:")
        print(json.dumps(result, indent=2))
