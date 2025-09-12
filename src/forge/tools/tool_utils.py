from rich.console import Console
from rich.syntax import Syntax

import csv
import json
import difflib
from typing import Any, Union

console = Console()

def _show_diff(old_content: str, new_content: str, filename: str) -> str:
    """Generates and displays a colorized, unified diff in the terminal."""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    )
    diff_text = "".join(diff)

    if not diff_text:
        return "[Info] No changes detected."

    console.print(Syntax(diff_text, "diff", theme="monokai", line_numbers=True))
    return diff_text

MAX_FIELD_LEN = 100
MAX_LIST_ITEMS = 5
MAX_SAMPLE_ROWS = 3

def _truncate_value(val: Any) -> Any:
    """Helper to truncate long values for a compact summary."""
    if isinstance(val, str):
        return val if len(val) <= MAX_FIELD_LEN else val[:MAX_FIELD_LEN] + "..."
    if isinstance(val, list):
        return [_truncate_value(v) for v in val[:MAX_LIST_ITEMS]]
    if isinstance(val, dict):
        return {k: _truncate_value(v) for k, v in val.items()}
    return val

def _guess_type(value: Any) -> Union[str, dict, list]:
    """Helper to infer the data type of a given value."""
    if value is None or value == "": return "null"
    if isinstance(value, dict): return {k: _guess_type(v) for k, v in value.items()}
    if isinstance(value, list): return ["list(empty)" if not value else _guess_type(value[0])]
    try:
        int(str(value)); return "int"
    except (ValueError, TypeError): pass
    try:
        float(str(value)); return "float"
    except (ValueError, TypeError): pass
    if str(value).lower() in ["true", "false"]: return "bool"
    return "string"

def _extract_csv_tsv(file_path: str, sep: str) -> dict:
    """Helper to extract schema and sample rows from a CSV or TSV file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter=sep)
            rows = [_truncate_value(row) for i, row in enumerate(reader) if i < MAX_SAMPLE_ROWS]
            schema = {}
            if rows and reader.fieldnames:
                for col in reader.fieldnames:
                    values = [row.get(col) for row in rows if row.get(col) not in (None, "")]
                    schema[col] = _guess_type(values[0]) if values else "unknown"
            return {"schema": schema, "sample": rows}
    except Exception as e:
        return {"error": str(e)}

def _extract_json(file_path: str) -> dict:
    """Helper to extract schema and sample rows from a JSON or JSONL file."""
    rows = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            try:
                data = json.load(f)
                rows = [_truncate_value(d) for d in (data if isinstance(data, list) else [data])[:MAX_SAMPLE_ROWS]]
            except json.JSONDecodeError:
                f.seek(0)
                for line in f:
                    if line.strip() and len(rows) < MAX_SAMPLE_ROWS:
                        rows.append(_truncate_value(json.loads(line)))
        schema = _guess_type(rows[0]) if rows else {}
        return {"schema": schema, "sample": rows}
    except Exception as e:
        return {"error": str(e)}