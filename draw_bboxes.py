import re
import argparse
from playwright.sync_api import sync_playwright

def add_numbering_to_level_2(snapshot_str):
    lines = snapshot_str.strip('\n').split('\n')
    counter = 1
    for i, line in enumerate(lines):
        if line.startswith('  - '):
            lines[i] = line.replace('  - ', f'  - [{counter}] ', 1)
            counter += 1
    return '\n'.join(lines)

def parse_numbered_elements(numbered_yaml):
    elements = []
    # Match strings like '  - [1] link "Learn more":'
    pattern = re.compile(r"^\s+-\s+\[(\d+)\]\s+([a-zA-Z0-9]+)(?:\s+\"([^\"]*)\")?")
    for line in numbered_yaml.split('\n'):
        match = pattern.search(line)
        if match:
            idx = int(match.group(1))
            role = match.group(2)
            name = match.group(3)
            elements.append((idx, role, name))
    return elements

def run(url):
    print(f"Navigating to {url}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(2000) # Wait for page to fully render
        
        print("Capturing accessibility tree...")
        snapshot = page.locator('body').aria_snapshot()
        numbered_result = add_numbering_to_level_2(snapshot)
        
        # Parse the elements
        elements = parse_numbered_elements(numbered_result)
        print(f"Parsed {len(elements)} numbered elements from the tree.")
        
        # Resolve bounding boxes
        boxes_to_draw = []
        for idx, role, name in elements:
            try:
                if role.lower() == "text":
                    locator = page.get_by_text(name, exact=True)
                    if locator.count() == 0:
                        locator = page.get_by_text(name)
                else:
                    if name:
                        locator = page.get_by_role(role, name=name, exact=True)
                        if locator.count() == 0:
                             locator = page.get_by_role(role, name=name)
                    else:
                        locator = page.get_by_role(role)
                
                # Get the bounding box of the first matched element
                if locator.count() > 0:
                    box = locator.first.bounding_box()
                    if box:
                        boxes_to_draw.append({
                            "id": idx,
                            "x": box["x"],
                            "y": box["y"],
                            "width": box["width"],
                            "height": box["height"]
                        })
            except Exception as e:
                pass # Ignore unsupported roles or parse issues
                
        print(f"Successfully resolved bounding boxes for {len(boxes_to_draw)} elements.")
        
        # Inject JavaScript to draw boxes on the page
        print("Drawing bounding boxes and saving screenshot...")
        page.evaluate("""(boxes) => {
            boxes.forEach(box => {
                const div = document.createElement('div');
                div.style.position = 'absolute';
                div.style.left = box.x + 'px';
                div.style.top = box.y + 'px';
                div.style.width = box.width + 'px';
                div.style.height = box.height + 'px';
                div.style.border = '2px solid red';
                div.style.pointerEvents = 'none'; // so it doesn't block clicks
                div.style.zIndex = '999999';
                div.style.boxSizing = 'border-box';
                
                const label = document.createElement('span');
                label.textContent = box.id;
                label.style.position = 'absolute';
                label.style.left = '-2px';
                label.style.top = '-18px';
                label.style.backgroundColor = 'red';
                label.style.color = 'white';
                label.style.fontSize = '12px';
                label.style.fontWeight = 'bold';
                label.style.padding = '1px 3px';
                label.style.border = '1px solid red';
                label.style.lineHeight = '14px';
                
                div.appendChild(label);
                document.body.appendChild(div);
            });
        }""", boxes_to_draw)
        
        screenshot_path = "screenshot_with_bboxes.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot successfully saved to {screenshot_path}")
        
        # Log the tree to file as well
        with open("google_a11y_tree.txt", "w", encoding="utf-8") as f:
            f.write(numbered_result)
        
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The URL to navigate to", default="https://google.co.in", nargs="?")
    args = parser.parse_args()
    run(args.url)
