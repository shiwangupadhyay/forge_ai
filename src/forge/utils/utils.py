import os

def generate_project_tree(root_path: str, max_depth: int = 3) -> str:
    """
    Generate a tree-like project structure using os.walk,
    ignoring common junk/system/build/venv/node_modules/etc. directories and files.

    Args:
        root_path (str): The root directory of the project.
        max_depth (int): Maximum depth of folders to display (default: 3).

    Returns:
        str: Project structure as a formatted tree string.
    """

    IGNORE_DIRS = {
        # Python
        "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
        "venv", ".venv", "env", ".env", ".tox", ".coverage",

        # Node / JS
        "node_modules", "bower_components", ".npm", ".yarn",

        # Java / JVM
        "target", "build", ".gradle", ".idea",

        # C / C++ / Rust / Go
        "cmake-build-debug", "cmake-build-release", "out", "bin", "obj",
        "cargo-target", "target", ".vs",

        # Data / logs
        "logs", "log", "tmp", "temp",

        # Git / VCS
        ".git", ".github", ".gitlab", ".svn", ".hg",

        # Editors / IDEs
        ".vscode", ".idea", ".DS_Store", "Thumbs.db"
    }

    IGNORE_FILES = {
        # Metadata & system
        ".gitignore", ".gitattributes", ".dockerignore",
        ".DS_Store", "Thumbs.db",

        # Build artifacts
        "*.pyc", "*.pyo", "*.class", "*.o", "*.obj", "*.exe",
        "*.dll", "*.so", "*.dylib",

        # Lock files
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "poetry.lock", "Pipfile.lock",

        # Coverage / reports
        "coverage.xml", "coverage.json", "lcov.info",

        # Logs
        "*.log"
    }

    tree_lines = []
    root_path = os.path.abspath(root_path)

    for current_path, dirs, files in os.walk(root_path):
        # Determine depth
        depth = current_path[len(root_path):].count(os.sep)

        if depth >= max_depth:
            dirs[:] = []  # stop walking deeper
            continue

        indent = "    " * depth
        folder_name = os.path.basename(current_path) or current_path
        tree_lines.append(f"{indent}📂 {folder_name}")

        # Filter dirs in-place so os.walk skips ignored ones
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        # Add files (skip ignored ones + patterns)
        for f in files:
            if any(f.endswith(ext) or f == ignore for ignore in IGNORE_FILES for ext in [ignore]):
                continue
            tree_lines.append(f"{indent}    📄 {f}")

    return "\n".join(tree_lines)

