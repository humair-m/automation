import os
import json
import shutil
import uuid
from pathlib import Path

try:
    from rich import print
except ImportError:
    pass

# === CONFIGURATION ===
SEARCH_ROOT = Path("/home/humair/all_data")  # Change to "/" to scan whole system
TARGET_SUBSTRING = "pollinations.ai"
OUTPUT_DIR = Path("./matched_notebooks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def check_cells_for_match(cells):
    """Return True if any cell contains the target substring"""
    for idx, cell in enumerate(cells):
        if 'source' in cell:
            # Combine list of lines or directly use string
            source_text = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
            if TARGET_SUBSTRING in source_text:
                return True, idx
    return False, -1


def copy_with_unique_name(src_path):
    """Copy file to OUTPUT_DIR with a unique UUID-based filename"""
    unique_name = f"{uuid.uuid4().hex}_{src_path.name}"
    dest_path = OUTPUT_DIR / unique_name
    shutil.copy2(src_path, dest_path)
    return dest_path


def scan_ipynbs(root: Path):
    print(f"[cyan]Scanning for .ipynb files in:[/cyan] {root}")
    count_total = count_matched = 0

    for filepath in root.rglob("*.ipynb"):
        count_total += 1
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            cells = data.get("cells", [])
            match_found, match_cell_index = check_cells_for_match(cells)

            if match_found:
                dest = copy_with_unique_name(filepath)
                print(f"[green][MATCH][/green] {filepath} [Cell #{match_cell_index}] → [bold]{dest.name}[/bold]")
                count_matched += 1
            else:
                print(f"[grey58][SKIP][/grey58] {filepath}")
        except Exception as e:
            print(f"[red][ERROR][/red] {filepath}: {e}")

    print(f"\n[bold yellow]Scan complete:[/bold yellow] {count_matched}/{count_total} matched.")

if __name__ == "__main__":
    scan_ipynbs(SEARCH_ROOT)
