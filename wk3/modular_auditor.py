# HOO ZI HAO (2603028) Week 3 Lab

#region Global Variables
inventory_qty = 0
inventory_max_qty = 500
failed_entries = 0
#endregion

#region headers_formatted
def formattedHeader(message, char="*"):
    divider = char * len(message)
    return(f"{divider}\n{message}\n{divider}")
#endregion

#region Input Validation
def get_valid_input():
    global failed_entries
    try:
        item_input = input("Enter item Qty or 'quit' to stop: ").strip()
        if item_input.lower() == 'quit':
            return item_qty == 'quit'
        try:
            item_qty = int(item_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer quantity.")
            failed_entries += 1
            return None
        if item_qty < 0:
            print("Invalid Qty. Negative values are not allowed.")
            failed_entries += 1
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return item_qty
#endregion

#region Inventory Processing
def process_delivery(inventory_qty,item_qty):
    return inventory_qty + item_qty
#endregion

#region Inventory Check
def max_inventory_check(inventory_qty, inventory_max_qty):
    if inventory_qty > inventory_max_qty:
        print("Inventory limit exceeded! Please audit the inventory.")
        return False
    return True
#endregion

#region Inventory Audit
def inventory_audit():
    global inventory_qty, inventory_max_qty, failed_entries
    while True:
        item_qty = get_valid_input()
        if item_qty is None:
            continue

        if item_qty == 'quit':
            break

        inventory_qty = process_delivery(inventory_qty, item_qty)

        print(f"Current inventory: {inventory_qty}/{inventory_max_qty}")

        if not max_inventory_check(inventory_qty, inventory_max_qty):
            break
#endregion

#region Summary Report
def summary_report(inventory_qty, failed_entries):
    print("\n" + formattedHeader("Inventory Audit Summary"))
    print(f"Total items audited: {inventory_qty}")
    print(f"Total failed entries: {failed_entries}")
#endregion

#region Main Program
def main_program():
    print(formattedHeader("Welcome to the Smart Inventory Auditor!"))
    inventory_audit()
    summary_report(inventory_qty, failed_entries)
#endregion

if __name__ == "__main__":
    main_program()