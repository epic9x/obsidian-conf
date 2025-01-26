#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Set, Optional, Tuple

class VaultAnalysisError(Exception):
    """Custom exception for vault analysis errors."""
    pass

def validate_directory(directory: str) -> Path:
    """Validate directory exists and is accessible."""
    path = Path(directory)
    if not path.exists():
        raise VaultAnalysisError(f"Directory does not exist: {directory}")
    if not path.is_dir():
        raise VaultAnalysisError(f"Not a directory: {directory}")
    if not os.access(path, os.R_OK):
        raise VaultAnalysisError(f"Directory is not readable: {directory}")
    return path

def is_naked_url(content: str) -> bool:
    """Check if content only contains a single URL and nothing else."""
    try:
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if len(lines) != 1:
            return False
        
        url_pattern = r'^https?://\S+$'
        return bool(re.match(url_pattern, lines[0]))
    except Exception as e:
        raise VaultAnalysisError(f"Error analyzing content: {e}")

def find_naked_urls(directory: str) -> List[str]:
    """Find all markdown files containing only a single URL."""
    try:
        path = validate_directory(directory)
        naked_urls = []
        
        for file_path in path.rglob('*.md'):
            try:
                if not os.access(file_path, os.R_OK):
                    print(f"Warning: Cannot read file {file_path}", file=sys.stderr)
                    continue
                    
                content = file_path.read_text(encoding='utf-8')
                if is_naked_url(content):
                    naked_urls.append(str(file_path))
            except Exception as e:
                print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)
                
        return naked_urls
    except Exception as e:
        raise VaultAnalysisError(f"Error searching for naked URLs: {e}")

def find_files_with_string(directory: str, search_string: str) -> List[str]:
    """Find all markdown files containing the specified string."""
    try:
        path = validate_directory(directory)
        matching_files = []
        
        for file_path in path.rglob('*.md'):
            try:
                if not os.access(file_path, os.R_OK):
                    print(f"Warning: Cannot read file {file_path}", file=sys.stderr)
                    continue
                    
                content = file_path.read_text(encoding='utf-8')
                if search_string in content:
                    matching_files.append(str(file_path))
            except Exception as e:
                print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)
                
        return matching_files
    except Exception as e:
        raise VaultAnalysisError(f"Error searching for string: {e}")

def move_files(files: List[str], target_dir: str) -> Tuple[List[str], List[str]]:
    """Move files to target directory, maintaining relative paths.
    Returns tuple of (successful_moves, failed_moves)."""
    try:
        target_path = Path(target_dir)
        if target_path.exists() and not target_path.is_dir():
            raise VaultAnalysisError(f"Target exists but is not a directory: {target_dir}")
            
        target_path.mkdir(parents=True, exist_ok=True)
        
        successful = []
        failed = []
        
        for file in files:
            try:
                src = Path(file)
                if not src.exists():
                    raise VaultAnalysisError(f"Source file does not exist: {file}")
                    
                dest = target_path / src.name
                if dest.exists():
                    raise VaultAnalysisError(f"Destination file already exists: {dest}")
                    
                src.rename(dest)
                successful.append(str(src))
            except Exception as e:
                print(f"Warning: Failed to move {file}: {e}", file=sys.stderr)
                failed.append(file)
                
        return successful, failed
    except Exception as e:
        raise VaultAnalysisError(f"Error moving files: {e}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Obsidian vault')
    parser.add_argument('--find-naked-urls', type=str, help='Directory to search for files with naked URLs')
    parser.add_argument('--move', type=str, help='Move files with naked URLs to specified directory')
    parser.add_argument('--filter', type=str, help='Search string to filter files by content')
    
    try:
        args = parser.parse_args()

        if args.find_naked_urls:
            try:
                files = find_naked_urls(args.find_naked_urls)
                if args.filter:
                    filtered_files = find_files_with_string(args.find_naked_urls, args.filter)
                    files = list(set(files) & set(filtered_files))
                
                if files:
                    print("\nMatching files:")
                    for file in files:
                        print(f"  {file}")
                    
                    if args.move:
                        successful, failed = move_files(naked_urls, args.move)
                        if successful:
                            print("\nSuccessfully moved files:")
                            for file in successful:
                                print(f"  {file}")
                        if failed:
                            print("\nFailed to move files:", file=sys.stderr)
                            for file in failed:
                                print(f"  {file}", file=sys.stderr)
                else:
                    print("No files with naked URLs found.")
            except VaultAnalysisError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
                
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
