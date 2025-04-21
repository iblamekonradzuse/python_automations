#!/usr/bin/env python3
# script to organize markdown files based on tags 
import os
import re
import shutil
from pathlib import Path

def extract_tags(file_path):
    """Extract tags from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Print the file content for debugging
            print(f"\nDebug - Content of {os.path.basename(file_path)}:")
            print(f"First 300 characters: {content[:300]}")
            
            # Look for tags with more flexible patterns
            # Pattern 1: Standard ***Tags:** [[tag1]] [[tag2]]
            tag_pattern1 = r'\*\*\*Tags:\*\*\s*(\[\[.*?\]\].*?)(?:\n|$)'
            # Pattern 2: Just look for [[tag]] anywhere in the file
            tag_pattern2 = r'\[\[(.*?)\]\]'
            
            # Try the first pattern
            tag_section = re.search(tag_pattern1, content, re.DOTALL)
            if tag_section:
                tags = re.findall(r'\[\[(.*?)\]\]', tag_section.group(1))
                print(f"Found tags with pattern 1: {tags}")
                return tags
            
            # If first pattern fails, try just finding all [[tag]] instances
            tags = re.findall(tag_pattern2, content)
            if tags:
                print(f"Found tags with pattern 2: {tags}")
                return tags
                
            print("No tags found in any pattern")
            return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def get_existing_folders(root_dir):
    """Get a dictionary of all existing folders in the directory structure with their depths."""
    folders = {}
    
    # Walk through the directory structure to find all folders
    for dirpath, dirnames, _ in os.walk(root_dir):
        # Skip the source directory itself if it's defined
        if 'source_dir' in globals() and dirpath == source_dir:
            continue
            
        # Skip .git directories
        if '.git' in dirpath:
            continue
            
        for dirname in dirnames:
            folder_path = os.path.join(dirpath, dirname)
            # Use the folder name as the key
            folder_name = dirname.lower()
            
            # Calculate the depth of this folder (relative to root_dir)
            path_parts = os.path.relpath(folder_path, root_dir).split(os.sep)
            depth = len(path_parts)
            
            # Store both the path and depth
            folders[folder_name] = {
                'path': folder_path,
                'depth': depth
            }
    
    # Debug: print some of the found folders
    print("\nDebug - Some detected target folders:")
    count = 0
    for name, info in folders.items():
        if "cs" in name.lower() or "terminal" in name.lower():
            print(f"  - {name}: {info['path']} (depth: {info['depth']})")
            count += 1
            if count >= 10:
                break
            
    return folders

def is_date_tag(tag):
    """Check if a tag resembles a date format."""
    # Check for common date formats like YYYY-MM-DD
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}$',         # YYYY-MM
        r'^\d{2}-\d{2}-\d{4}$',   # DD-MM-YYYY
        r'^\d{2}-\d{2}-\d{2}$'    # DD-MM-YY
    ]
    
    for pattern in date_patterns:
        if re.match(pattern, tag):
            return True
    
    return False

def find_best_matching_folder(tags, folders):
    """Find the deepest matching folder for the given tags."""
    matches = []
    
    print(f"\nDebug - Looking for matches for tags: {tags}")
    
    # Remove date-type tags
    non_date_tags = [tag for tag in tags if not is_date_tag(tag)]
    if non_date_tags != tags:
        print(f"  - Ignoring date tags. Using only: {non_date_tags}")
    
    if not non_date_tags:
        print("  - No non-date tags found to match with folders")
        return None
    
    # Try to find matches for all non-date tags
    for tag in non_date_tags:
        tag_lower = tag.lower()
        
        # Check for matches
        for folder_name, folder_info in folders.items():
            match_type = None
            # Exact match (ignoring case)
            if tag_lower == folder_name:
                match_type = "exact"
                matches.append((folder_info, match_type))
            # Skip partial matches entirely - they cause too many problems
                
            if match_type:
                print(f"  - Tag '{tag}' {match_type} match with folder '{folder_name}': {folder_info['path']}")
    
    if not matches:
        print("  - No matching folders found")
        return None
    
    # Sort matches by depth (deepest first)
    matches.sort(key=lambda x: x[0]['depth'], reverse=True)
    
    # Return the path of the deepest match
    best_match = matches[0][0]['path']
    print(f"  - Best match: {best_match}")
    return best_match

def sort_markdown_files(source_dir, root_dir):
    """Sort markdown files from a single directory based on their tags."""
    # Get all existing folders for matching
    existing_folders = get_existing_folders(root_dir)
    print(f"Found {len(existing_folders)} potential target folders.")
    
    # Get all markdown files in the specified directory (not subdirectories)
    markdown_files = []
    for filename in os.listdir(source_dir):
        if filename.lower().endswith('.md'):
            file_path = os.path.join(source_dir, filename)
            if os.path.isfile(file_path):  # Ensure it's a file, not a directory
                markdown_files.append(file_path)
    
    print(f"Found {len(markdown_files)} markdown files in {source_dir}.")
    
    # Process each file
    moved_count = 0
    for file_path in markdown_files:
        print(f"\nProcessing file: {file_path}")
        tags = extract_tags(file_path)
        
        if not tags:
            print(f"No tags found in {file_path}")
            continue
        
        # Find the best (deepest) matching folder for all tags
        target_folder = find_best_matching_folder(tags, existing_folders)
        
        if not target_folder:
            print(f"No matching folder found for tags {tags} in {file_path}. Leaving in place.")
            continue
        
        # If the file is already in the right place, skip it
        if os.path.normpath(os.path.dirname(file_path)) == os.path.normpath(target_folder):
            print(f"File {file_path} is already in the right location.")
            continue
        
        # Get the destination path
        destination = os.path.join(target_folder, os.path.basename(file_path))
        
        # If a file with the same name already exists in the destination, add a suffix
        if os.path.exists(destination):
            base_name, ext = os.path.splitext(os.path.basename(file_path))
            i = 1
            while os.path.exists(os.path.join(target_folder, f"{base_name}_{i}{ext}")):
                i += 1
            destination = os.path.join(target_folder, f"{base_name}_{i}{ext}")
        
        # Move the file
        try:
            shutil.move(file_path, destination)
            print(f"Moved {file_path} to {destination} based on tags {tags}")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {file_path}: {e}")
    
    print(f"Sorting complete! Moved {moved_count} files.")

def browse_directories(starting_dir=None):
    """Interactive directory browser to select a directory."""
    current_dir = starting_dir or os.getcwd()
    
    while True:
        print(f"\nCurrent directory: {current_dir}")
        print("\nAvailable options:")
        print("0: Select this directory")
        print("b: Go back to parent directory")
        
        # List subdirectories
        subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
        
        if not subdirs:
            print("No subdirectories found.")
        else:
            for i, subdir in enumerate(subdirs, 1):
                print(f"{i}: {subdir}")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "0":
            return current_dir
        elif choice.lower() == "b":
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # We're at the root
                print("Already at the root directory.")
            else:
                current_dir = parent_dir
        elif choice.isdigit() and 1 <= int(choice) <= len(subdirs):
            current_dir = os.path.join(current_dir, subdirs[int(choice) - 1])
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    print("Welcome to the Markdown Tag Sorter!\n")
    
    # Start from current directory or script location
    script_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()
    
    # First, select the source directory
    print("\n--- Step 1: Select the source directory containing markdown files to sort ---")
    source_dir = browse_directories(script_dir)
    
    # Then, select the root directory for potential target folders
    print("\n--- Step 2: Select the root directory of your notes structure ---")
    root_dir = browse_directories(script_dir)
    
    # Confirm before proceeding
    print(f"\nAbout to sort markdown files from: {source_dir}")
    print(f"Will look for target folders in: {root_dir}")
    confirm = input("Proceed? (y/n): ")
    
    if confirm.lower() == 'y':
        sort_markdown_files(source_dir, root_dir)
    else:
        print("Operation cancelled.")
