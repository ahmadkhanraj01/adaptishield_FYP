import os

# Directories to ignore
IGNORE_DIRS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist",
]

IGNORE_FILES = [
    "README.md",
]

def search_keyword(root_directory, keyword, case_sensitive=False):
    matches = 0

    for current_path, directories, files in os.walk(root_directory):

        # Remove ignored directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORE_DIRS
        ]

        for file in files:
            file_path = os.path.join(current_path, file)
            if file in IGNORE_FILES:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_number, line in enumerate(f, start=1):

                        if case_sensitive:
                            found = keyword in line
                        else:
                            found = keyword.lower() in line.lower()

                        if found:
                            if matches == 0:
                                print(f"\nSearching for: '{keyword}'\n")

                            matches += 1
                            print(f"📄 {file_path}")
                            print(f"   Line {line_number}: {line.strip()}")
                            print()

            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    if matches == 0:
        print(f"No matches found for '{keyword}'.")
    else:
        print(f"Total matches: {matches}")


if __name__ == "__main__":
    root_directory = "."
    keyword = input("Enter keyword to search: ").strip()

    search_keyword(root_directory, keyword)