import json
import argparse
from playwright.sync_api import sync_playwright

def get_accessibility_tree(url):
    print(f"Navigating to {url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        
        print("Capturing accessibility tree...")
        # Get the accessibility tree snapshot
        snapshot = page.locator('body').aria_snapshot()
        
        browser.close()
        return snapshot

def add_numbering_to_level_2(snapshot_str):
    lines = snapshot_str.strip('\n').split('\n')
    counter = 1
    for i, line in enumerate(lines):
        # In Playwright's aria_snapshot, level 2 elements start with exactly two spaces and a hyphen
        if line.startswith('  - '):
            lines[i] = line.replace('  - ', f'  - [{counter}] ', 1)
            counter += 1
    return '\n'.join(lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get accessibility tree for a URL using Playwright")
    parser.add_argument("url", help="The URL to navigate to", default="https://example.com", nargs="?")
    args = parser.parse_args()
    
    result = get_accessibility_tree(args.url)
    numbered_result = add_numbering_to_level_2(result)
    
    print("\nAccessibility Tree:")
    print(numbered_result)
    
    log_filename = "a11y_tree_log.txt"
    with open(log_filename, "w", encoding="utf-8") as f:
        f.write(numbered_result)
    
    print(f"\nTree successfully saved to {log_filename}")
