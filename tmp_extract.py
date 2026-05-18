import json
import sys

def parse_nb(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"\n\n=== {file_path} ===")
    for cell in nb.get("cells", []):
        if cell["cell_type"] == "code":
            source = "".join(cell.get("source", []))
            # Let's rudimentarily filter only the DB operations
            if "db." in source or "aggregate" in source or "mapReduce" in source:
                print("\n-- CELL --")
                print(source)

parse_nb(sys.argv[1])
parse_nb(sys.argv[2])
