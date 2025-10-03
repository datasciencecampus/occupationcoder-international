from deepdiff import DeepDiff
from pathlib import Path    
import os
import json

CURRENT_DIR = Path(__file__).resolve()
PACKAGE_ROOT = CURRENT_DIR.parents[1]
DICT_DIR = PACKAGE_ROOT / Path("dictionaries/isco")
BACKUP_DIR = DICT_DIR / Path("backup")
PATTERN = "buckets_isco"

# Find all matching files
matching_files = [f for f in BACKUP_DIR.glob(f"*{PATTERN}*") if f.is_file()]
# Sort alphabetically by file name
sorted_files = sorted(matching_files, key=lambda f: f.name, reverse=True)
# Get the top file name
top_file = sorted_files[0].name if sorted_files else None

# Load JSON files into Python objects
with open(DICT_DIR / Path(PATTERN + ".json")) as f1, open(BACKUP_DIR / Path(top_file)) as f2:
    json1 = json.load(f1)
    json2 = json.load(f2)

diff = DeepDiff(json1, json2, ignore_order=True)

# Save diff to a file
with open("diff_output.json", "w") as out_file:
    json.dump(diff, out_file, indent=4)

for category, changes in diff.items():
    print(f"{category}: {len(changes)} differences")

print("Diff saved to diff_output.json")

