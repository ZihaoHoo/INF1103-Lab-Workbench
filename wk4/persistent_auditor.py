# HOO ZI HAO (2603028) Week 4 Lab
import csv
from pathlib import Path

#region headers_formatted
def formattedHeader(message, char="*"):
    divider = char * len(message)
    return(f"{divider}\n{message}\n{divider}")
#endregion

#region Input Validation
def get_valid_input():
    item_name = input("Enter Product Name or 'quit' to stop: ").strip()
    if item_name.lower() == "quit":
        return "quit"
    
    item_input = input(f"Enter {item_name} Qty: ").strip()
    try:
        item_qty = int(item_input)
    except ValueError:
        print("Invalid input. Please enter a valid integer quantity.")
        return None
    if item_qty < 0:
        print("Invalid Qty. Negative values are not allowed.")
        return None
    return [item_name,item_qty]
#endregion

#region Inventory Processing
def process_delivery(inventory_qty, item_qty):
    return inventory_qty + item_qty
#endregion

#region Inventory Check
def max_inventory_check(inventory_qty, inventory_max_qty):
    if inventory_qty > inventory_max_qty:
        print("Inventory limit exceeded! Please audit the inventory.")
        return False
    return True
#endregion

#region Tax Calculation
def calculate_tax(amount, tax_rate=0.10):
    return amount * tax_rate
#endregion

#region Inventory Audit
def inventory_audit():
    inventory_qty = 0
    inventory_max_qty = 500
    failed_entries = 0
    deliveries_processed = 0
    newly_added_orders = []
    inventoryList = load_inventory()
    for item in inventoryList:
        inventory_qty += int(item[2])
    inv_id = len(inventoryList) + 1
    
    show_inventoryList(inventoryList)
    print(f"Current inventory: {inventory_qty}/{inventory_max_qty}\n")
    while True:
        
        item = get_valid_input()
        if item == 'quit':
            #save_inventory(inventoryList)
            break

        if item is None:
            failed_entries += 1
            continue

        item_qty = item[1]
        inventory_qty = process_delivery(inventory_qty, item_qty)
        print(f"Current inventory: {inventory_qty}/{inventory_max_qty}")

        order = [inv_id, item[0], item[1]]
        inventoryList.append(order)
        newly_added_orders.append(order)
        inv_id += 1

        deliveries_processed += 1

        calculated_tax = calculate_tax(item_qty)
        print(f"Tax for this {item[0]}: {calculated_tax:.2f}")

        if not max_inventory_check(inventory_qty, inventory_max_qty):
            #save_inventory(inventoryList)
            break
    generate_report(inventory_qty, deliveries_processed, failed_entries,newly_added_orders)
#endregion

#region Summary Report
def generate_report(total_units, deliveries_processed, failed_attempts, newly_added_inv):
    print("\n" + formattedHeader("Inventory Audit Summary"))
    print("Newly added orders:")
    if len(newly_added_inv) == 0:
        print("No new orders added.")
    else:
        for item in newly_added_inv:
            print(f"{item[0]},{item[1]},{item[2]}")
    print("\n")
    print(f"Total items audited: {total_units}")
    print(f"Total deliveries processed: {deliveries_processed}")
    print(f"Total failed entries: {failed_attempts}")
#endregion

#region normalize file to list
def load_inventory():
    script_dir = Path(__file__).parent
    file_path = script_dir / "inventory.txt"
    
    if not file_path.is_file():
        file_path.touch()
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=',')
        return [row for row in reader]
#endregion

#region show inital list
def show_inventoryList(inventory):
    if len(inventory) == 0:
        return print("There is no record in inventory record list!\n")
    print("Current inventory record list:")
    for item in inventory:
        print(f"{item[0]},{item[1]},{item[2]}")
    
#region Main Program
def main_program():
    print(formattedHeader("Welcome to the Smart Inventory Auditor!"))
    inventory_audit()
#endregion

if __name__ == "__main__":
    main_program()