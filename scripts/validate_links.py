import os
import re
from pathlib import Path

def find_md_files(root_dir):
    md_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def validate_links(root_dir):
    md_files = find_md_files(root_dir)
    broken_links = []
    
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        links = link_pattern.findall(content)
        file_dir = os.path.dirname(file_path)
        
        for link in links:
            # Skip anchor links within same file
            if link.startswith('#'):
                continue
            # Skip external links
            if link.startswith('http://') or link.startswith('https://'):
                continue
            
            # Handle anchor in file links (e.g. file.md#section)
            target_file = link.split('#')[0]
            if not target_file: # Case where link is just #anchor (handled above)
                continue
                
            target_path = os.path.join(file_dir, target_file)
            target_path = os.path.normpath(target_path)
            
            if not os.path.exists(target_path):
                broken_links.append({
                    'source': file_path,
                    'link': link,
                    'target': target_path
                })
                
    return broken_links

if __name__ == "__main__":
    root_dir = "lesson-18/interactive/logical-fallacies/tutorials/"
    print(f"Scanning {root_dir} for broken links...")
    broken = validate_links(root_dir)
    
    if broken:
        print(f"Found {len(broken)} broken links:")
        for item in broken:
            print(f"Source: {item['source']}")
            print(f"  Link: {item['link']}")
            print(f"  Target: {item['target']}")
        exit(1)
    else:
        print("No broken links found.")
        exit(0)

