import os

EXCLUDE = {'.DS_Store', '.git', 'node_modules', 'venv'}

def print_tree(start_path, prefix=""):
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        print(f"{prefix}└── [Permission Denied]")
        return
    except FileNotFoundError:
        print(f"{prefix}└── [Path Not Found]")
        return

    entries = [e for e in entries if e not in EXCLUDE]

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            extension = "    " if index == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension)


if __name__ == "__main__":
    root_directory = "."  # Change this to your target directory
    print(root_directory)
    print_tree(root_directory)