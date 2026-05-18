import json

def dump_nb(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for i, cell in enumerate(nb.get("cells", [])):
        if cell["cell_type"] == "code":
            print(f"\n# --- CELL {i} ({file_path}) ---")
            for line in cell.get("source", []):
                print(line, end="")
            print()

dump_nb("scripts/aggregations.ipynb")
