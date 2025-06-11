import os
import json
import shutil
import uuid
from pathlib import Path

try:
    from rich import print
    from rich.console import Console
    from rich.markdown import Markdown
except ImportError:
    print = print
    Console = None

# === CONFIGURATION ===
SEARCH_ROOT = Path("/home/humair/MATH_PAPER_matched_notebooks")  # Use "/" to search full system
TARGET_SUBSTRINGS = [
"image.pollinations.ai"
]
OUTPUT_DIR = Path("/home/humair/MATH_PAPER_matched_notebooks_2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

console = Console() if Console else None

def check_cells_for_match(cells):
    """Return True if any cell contains a target string, with index and match"""
    for idx, cell in enumerate(cells):
        if 'source' in cell:
            source_text = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            for target in TARGET_SUBSTRINGS:
                if target in source_text:
                    return True, idx, target
    return False, -1, None

def copy_with_unique_name(src_path):
    unique_name = f"{uuid.uuid4().hex}_{src_path.name}"
    dest_path = OUTPUT_DIR / unique_name
    shutil.copy2(src_path, dest_path)
    return dest_path

def display_single_cell(cell, match_idx, target):
    cell_type = cell.get("cell_type", "unknown")
    source = cell.get("source", [])
    source_text = ''.join(source) if isinstance(source, list) else source
    print(f"\n[yellow]--- Matched Cell #{match_idx} (type: {cell_type}, match: {target}) ---[/yellow]\n")
    if console:
        console.rule()
        console.print(Markdown(source_text) if cell_type == "markdown" else source_text)
    else:
        print(source_text)

def scan_ipynbs(root: Path):
    print(f"[cyan]Scanning for .ipynb files in:[/cyan] {root}")
    count_total = count_matched = 0

    for filepath in root.rglob("*.ipynb"):
        count_total += 1
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            cells = data.get("cells", [])
            match_found, match_idx, match_str = check_cells_for_match(cells)

            if match_found:
                dest = copy_with_unique_name(filepath)
                print(f"[green][MATCH][/green] {filepath} [Cell #{match_idx}] matched [bold]{match_str}[/bold] → [bold]{dest.name}[/bold]")
                display_single_cell(cells[match_idx], match_idx, match_str)
                count_matched += 1
            else:
                print(f"[grey58][SKIP][/grey58] {filepath}")
        except Exception as e:
            print(f"[red][ERROR][/red] {filepath}: {e}")

    print(f"\n[bold yellow]Scan complete:[/bold yellow] {count_matched}/{count_total} matched.")

if __name__ == "__main__":
    scan_ipynbs(SEARCH_ROOT)
