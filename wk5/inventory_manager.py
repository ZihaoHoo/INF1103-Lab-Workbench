# HOO ZI HAO (2603028) Week 5 Lab
import json
from pathlib import Path

#region headers_formatted
def formattedHeader(message, char="*"):
    divider = char * len(message)
    return(f"{divider}\n{message}\n{divider}")
#endregion

#region Load Inventory from JSON
def load_inventory():
    script_dir = Path(__file__).parent
    file_path = script_dir / "inventory.json"
    
    if not file_path.is_file():
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)
        print("inventory.json not found. Created a new inventory file.")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            inventory = json.load(file)
            print("inventory.json found.")
            print("Inventory loaded successfully.")
            return inventory
        except json.JSONDecodeError:
            print("Error reading inventory.json. Starting with an empty inventory.")
            return []
#endregion

if __name__ == "__main__":
    load_inventory()