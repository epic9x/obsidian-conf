#!/usr/bin/env python3
import argparse
import os
import re
from pathlib import Path
from typing import List, Set

def is_naked_url(content: str) -> bool:
    """Check if content only contains a single URL and nothing else."""
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if len(lines) != 1:
        return False
    
    url_pattern = r'^https?://\S+$'
    return bool(re.match(url_pattern, lines[0]))

def find_naked_urls(directory: str) -> List[str]:
    """Find all markdown files containing only a single URL."""
    naked_urls = []
    
    for path in Path(directory).rglob('*.md'):
        try:
            content = path.read_text()
            if is_naked_url(content):
                naked_urls.append(str(path))
        except Exception as e:
            print(f"Error reading {path}: {e}")
    
    return naked_urls

def main():
    parser = argparse.ArgumentParser(description='Analyze Obsidian vault')
    parser.add_argument('--find-naked-urls', type=str, help='Directory to search for files with naked URLs')
    
    args = parser.parse_args()

    if args.find_naked_urls:
        naked_urls = find_naked_urls(args.find_naked_urls)
        if naked_urls:
            print("\nFiles containing only URLs:")
            for file in naked_urls:
                print(f"  {file}")
        else:
            print("No files with naked URLs found.")

if __name__ == "__main__":
    main()
