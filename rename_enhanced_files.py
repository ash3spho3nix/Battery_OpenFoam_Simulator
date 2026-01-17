#!/usr/bin/env python3
"""
Script to find and rename files with '_enhanced' suffix to their original names.
"""

import os
import re
from pathlib import Path

def find_enhanced_files(directory):
    """Find all files with '_enhanced' suffix in the directory."""
    enhanced_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_enhanced.py'):
                full_path = os.path.join(root, file)
                enhanced_files.append(full_path)
    
    return enhanced_files

def rename_file(old_path, new_path):
    """Rename a file from old_path to new_path."""
    try:
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")
        return True
    except Exception as e:
        print(f"Error renaming {old_path}: {e}")
        return False

def get_new_filename(old_filename):
    """Generate new filename by removing '_enhanced' suffix."""
    # Remove '_enhanced' suffix
    new_filename = old_filename.replace('_enhanced.py', '.py')
    return new_filename

def main():
    """Main function to find and rename enhanced files."""
    print("Finding files with '_enhanced' suffix...")
    
    # Start from current directory
    current_dir = os.getcwd()
    enhanced_files = find_enhanced_files(current_dir)
    
    if not enhanced_files:
        print("No files with '_enhanced' suffix found.")
        return
    
    print(f"Found {len(enhanced_files)} files with '_enhanced' suffix:")
    for file in enhanced_files:
        print(f"  - {file}")
    
    print("\nRenaming files...")
    success_count = 0
    
    for old_path in enhanced_files:
        # Get the directory and filename
        dir_name = os.path.dirname(old_path)
        old_filename = os.path.basename(old_path)
        
        # Generate new filename
        new_filename = get_new_filename(old_filename)
        new_path = os.path.join(dir_name, new_filename)
        
        # Rename the file
        if rename_file(old_path, new_path):
            success_count += 1
    
    print(f"\nRenamed {success_count}/{len(enhanced_files)} files successfully.")
    
    # Check for potential import issues
    print("\nChecking for potential import issues...")
    check_imports(current_dir)

def check_imports(directory):
    """Check for import statements that might need updating."""
    import_pattern = re.compile(r'import\s+.*_enhanced|from\s+.*_enhanced\s+import')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = import_pattern.findall(content)
                        if matches:
                            print(f"Potential import issue in {file_path}:")
                            for match in matches:
                                print(f"  - {match.strip()}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    main()