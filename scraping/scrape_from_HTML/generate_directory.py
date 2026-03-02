import os
from pathlib import Path

def generate_directory_tree(dir_path: Path, prefix: str = ''):
    """Recursively generates a tree structure while applying specific file filters."""
    try:
        # Get all contents of the current directory
        contents = list(dir_path.iterdir())
    except PermissionError:
        # Skip folders where we don't have read permissions
        return
        
    # 1. Exclude hidden files and folders (starting with '.')
    contents = [p for p in contents if not p.name.startswith('.')]
    
    # Sort alphabetically, grouping directories first, then files
    contents.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
    
    # 2. Limit .html and .txt files to maximum 2 per folder
    filtered_contents = []
    html_count = 0
    txt_count = 0
    
    for p in contents:
        if p.is_file():
            ext = p.suffix.lower()
            if ext == '.html':
                html_count += 1
                if html_count > 2: 
                    continue # Skip if we already have 2 HTML files
            elif ext == '.txt':
                txt_count += 1
                if txt_count > 2: 
                    continue # Skip if we already have 2 TXT files
                    
        filtered_contents.append(p)
        
    # Set up the tree visual pointers
    pointers = ['├── '] * (len(filtered_contents) - 1) + ['└── '] if filtered_contents else []
    
    for pointer, path in zip(pointers, filtered_contents):
        # Yield the formatted string for the current file/folder
        yield prefix + pointer + path.name
        
        # If it's a directory, recursively process its contents
        if path.is_dir():
            extension = '│   ' if pointer == '├── ' else '    '
            yield from generate_directory_tree(path, prefix=prefix + extension)

def main():
    # Set your targeted directory path and output file name
    dataset_path = Path("/Users/sameerbanchhor/Desktop/durg results/datasets")
    output_file = "result_dataset_directory.txt"
    
    # Verify the path actually exists before running
    if not dataset_path.exists():
        print(f"Error: The path '{dataset_path}' does not exist. Please check the path.")
        return

    print(f"Generating tree for: {dataset_path} ...")
    
    # Open the text file and write the generated tree
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the root folder name at the very top
        f.write(f"{dataset_path.name}/\n")
        
        # Generate and write the nested structure
        for line in generate_directory_tree(dataset_path):
            f.write(line + '\n')
            
    print(f"Done! Directory tree successfully saved to '{output_file}'.")

if __name__ == "__main__":
    main()