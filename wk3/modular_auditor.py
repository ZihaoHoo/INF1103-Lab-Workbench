# HOO ZI HAO (2603028) Week 3 Lab

#region headers_formatted
def formattedHeader(message, char="*"):
    divider = char * len(message)
    return(f"{divider}\n{message}\n{divider}")
#endregion

#region Input Validation
def get_valid_input():
    item_input = input("Enter item Qty or 'quit' to stop: ").strip()
    if item_input.lower() == 'quit':
        return 'quit'
    try:
        item_qty = int(item_input)
    except ValueError:
        print("Invalid input. Please enter a valid integer quantity.")
        return None
    if item_qty < 0:
        print("Invalid Qty. Negative values are not allowed.")
        return None
    return item_qty
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
    while True:
        item_qty = get_valid_input()
        if item_qty is None:
            failed_entries += 1
            continue
        if item_qty == 'quit':
            break

        inventory_qty = process_delivery(inventory_qty, item_qty)
        print(f"Current inventory: {inventory_qty}/{inventory_max_qty}")

        deliveries_processed += 1

        calculated_tax = calculate_tax(item_qty)
        print(f"Tax for this delivery: {calculated_tax:.2f}")

        if not max_inventory_check(inventory_qty, inventory_max_qty):
            break
    generate_report(inventory_qty, deliveries_processed, failed_entries)
#endregion

#region Summary Report
def generate_report(total_units, deliveries_processed, failed_attempts):
    print("\n" + formattedHeader("Inventory Audit Summary"))
    print(f"Total items audited: {total_units}")
    print(f"Total deliveries processed: {deliveries_processed}")
    print(f"Total failed entries: {failed_attempts}")
#endregion

#region Main Program
def main_program():
    print(formattedHeader("Welcome to the Smart Inventory Auditor!"))
    inventory_audit()
#endregion

if __name__ == "__main__":
    main_program()