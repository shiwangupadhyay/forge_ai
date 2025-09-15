from langchain_core.tools import tool
from rich.console import Console
from rich.panel import Panel

import os
import sys
import json
import subprocess

from .tool_utils import _show_diff, _extract_csv_tsv, _extract_json

@tool
def read_file(file_path: str) -> str:
    """Reads and returns the entire content of a specified text file.

    Args:
        file_path: The path to the file to read.

    Returns:
        The content of the file as a string, or an error message if the file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"[ToolError: Error reading file '{file_path}': {e}]"


@tool
def propose_changes(file_path: str, new_content: str) -> str:
    """Proposes changes to a file by showing a diff and asking for user approval.

    This function first reads the existing content of the file (if it exists),
    then generates a colorized diff between the original and new content.
    If the directory for the file doesn't exist, it will be created upon approval.
    Changes are only written to the file if the user approves.

    Args:
        file_path: The path to the file to propose changes for.
        new_content: The new content to write to the file if approved.

    Returns:
        A string indicating the outcome:
        - "changes applied to {file_path}": The change was approved and written.
        - "changes rejected by user": The user did not approve the change.
        - "[Info] No changes detected.": The new content is identical to the original.
        - "[ToolError: ...]": An error occurred during file reading or writing.
    """
    original_content = ""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            return f"[ToolError: Could not read '{file_path}': {e}]"

    diff_result = _show_diff(original_content, new_content, filename=file_path)

    if "[Info] No changes detected." in diff_result:
        return diff_result

    # Ask user for approval (interactive)
    choice = input(f"\nApply changes to {file_path}? [y/N]: ").strip().lower()

    if choice in ("y", "yes"):
        try:
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"changes applied to {file_path}"
        except Exception as e:
            return f"[ToolError: Failed to write changes: {e}]"
    else:
        return "changes rejected by user"

@tool
def read_notebook_cells(file_path: str) -> str:
    """Reads a Jupyter Notebook (.ipynb) and extracts all cell sources into a single string.

    Each cell's source content is joined, and then all cell contents are
    joined by a separator string ("\\n\\n---\\n\\n").

    Args:
        file_path: The path to the Jupyter Notebook file.

    Returns:
        A single string containing the concatenated source code of all cells,
        or an error message if the notebook cannot be read or parsed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
        content = ["".join(cell["source"]) for cell in notebook.get("cells", []) if "source" in cell]
        return "\n\n---\n\n".join(content)
    except Exception as e:
        return f"[ToolError: Error reading notebook '{file_path}': {e}]"

@tool
def summarize_dataset(file_path: str) -> str:
    """Inspects a data file (.csv, .tsv, .json, .ndjson) and provides a summary.

    The summary includes the file name, inferred schema, and a few sample rows.
    Supports CSV, TSV, JSON, and NDJSON formats.

    Args:
        file_path: The path to the data file to summarize.

    Returns:
        A multi-line string containing the summary of the dataset, including schema
        and sample rows. Returns an error message if the file is not found,
        the format is unsupported, or an error occurs during processing.
    """
    if not os.path.exists(file_path):
        return f"[ToolError: The file '{file_path}' was not found.]"

    ext = os.path.splitext(file_path)[1].lower()
    info = {}
    if ext == ".csv": info = _extract_csv_tsv(file_path, sep=",")
    elif ext == ".tsv": info = _extract_csv_tsv(file_path, sep="\t")
    elif ext in [".json", ".ndjson"]: info = _extract_json(file_path)
    else: return f"[ToolError: Unsupported file format '{ext}'.]"

    if "error" in info:
        return f"[ToolError: Could not process '{file_path}': {info['error']}]"

    lines = [f"File: {os.path.basename(file_path)}"]
    schema = info.get("schema", {})
    if isinstance(schema, dict):
        lines.append(f"Schema: {', '.join(f'{k} (type: {v})' for k, v in schema.items())}")
    else:
        lines.append(f"Schema: {json.dumps(schema)}")

    sample_rows = info.get("sample", [])
    if sample_rows:
        lines.append("Sample Rows:")
        for row in sample_rows:
            lines.append(" | ".join(str(v) for v in row.values()) if isinstance(row, dict) else str(row))
    return "\n".join(lines)

@tool
def execute_code(code: str) -> str:
    """
    Executes a given string of Python code after getting user permission.
    It captures and returns the code's output and errors.

    Args:
        code: A string containing the Python code to be executed.

    Returns:
        A string containing the outcome: execution output, user rejection, or an error.
    """
    console = Console()

    prompt_panel = Panel(
        f"[cyan]{code}[/cyan]\n\n"
        f"[bold red]Warning: Executing this code can modify files and interact with your system.[/bold red]",
        title="[bold yellow]Permission Required to Execute Code[/bold yellow]",
        border_style="yellow",
        expand=False
    )
    console.print(prompt_panel)
    
    try:
        # Ask for user confirmation.
        choice = console.input("[bold]Do you approve? [y/N]:[/bold] ").strip().lower()
        if choice not in ('y', 'yes'):
            return "[Action Rejected by User] Code execution cancelled."
    except KeyboardInterrupt:
        return "[Action Rejected by User] Code execution cancelled."

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
            timeout=30 
        )
        output = ""
        if result.stdout:
            output += f"--- Output ---\n{result.stdout}\n"
        if result.stderr:
            output += f"--- Error ---\n{result.stderr}\n"
        if not output:
            return "Code executed with no output."
            
        return output

    except subprocess.TimeoutExpired:
        return "[ToolError: Code execution timed out after 30 seconds.]"
    except Exception as e:
        return f"[ToolError: An unexpected error occurred: {e}]"
    
@tool
def write_notebook(file_path: str, notebook_json: str) -> str:
    """
    Writes a JSON string to a .ipynb file after getting user permission.

    This tool is for saving a complete Jupyter Notebook. The agent must generate
    the full, valid JSON content of the notebook first.

    Args:
        file_path: The path to the .ipynb file to create (e.g., 'analysis.ipynb').
        notebook_json: A string containing the full, valid JSON of the notebook.

    Returns:
        A string indicating the outcome of the operation.
    """
    if not file_path.endswith(".ipynb"):
        return "[ToolError: file_path must end with .ipynb]"
    
    print(f"\n--- Notebook to be created at: {file_path} ---")
    try:
        # Ask for user confirmation.
        choice = input("Do you want to create/update this notebook? [y/N]: ").strip().lower()
        if choice not in ('y', 'yes'):
            return "[Action Rejected by User] Notebook creation cancelled."
    except KeyboardInterrupt:
        return "[Action Rejected by User] Notebook creation cancelled."
    
    try:
        notebook_data = json.loads(notebook_json)
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notebook_data, f, indent=2)
            
        return f"Successfully wrote notebook to {file_path}"
    except json.JSONDecodeError:
        return "[ToolError: The provided 'notebook_json' string is not valid JSON.]"
    except Exception as e:
        return f"[ToolError: An unexpected error occurred: {e}]"