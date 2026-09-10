# HOO ZI HAO (2603028) Week 2 Lab

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

#region Inventory Audit
def inventory_audit():
    global inventory_qty, inventory_max_qty, failed_entries
    while True:
        item_input = input("Enter item Qty or 'quit' to stop: ").strip()

        if item_input.lower() == 'quit':
            break

        try:
            item_qty = int(item_input)
        except ValueError:
            print("Invalid input. Please enter a valid integer quantity.")
            failed_entries += 1
            continue

        if item_qty < 0:
            print("Invalid Qty. Negative values are not allowed.")
            failed_entries += 1
            continue

        inventory_qty += item_qty

        print(f"Current inventory: {inventory_qty}/{inventory_max_qty}")

        if inventory_qty > inventory_max_qty:
            print("Inventory limit exceeded! Please audit the inventory.")
            break
#endregion

#region Main Program
def main_program():
    print(formattedHeader("Welcome to the Smart Inventory Auditor!"))
#endregion

if __name__ == "__main__":
    main_program()