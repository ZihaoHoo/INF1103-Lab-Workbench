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

#region print menu
def print_menu():
    print("\n" + formattedHeader("Inventory Management Menu"))
    print("1. Display all inventory")
    print("2. Add a new product")
    print("3. Update stock for an existing product")
    print("4. Search for a product")
    print("5. Save inventory to file")
    print("6. Exit the program")
#endregion

#region display all inventory
def display_all(inventory):
    if not inventory:
        print("No products found in inventory.")
        return
    headers = ["ID", "Name", "Price", "Stock"]

    widths = {
        "ID": max(len(str(item["ID"])) for item in inventory),
        "Name": max(len(str(item["Name"])) for item in inventory),
        "Price": max(len(f"${item['Price']:.2f}") for item in inventory),
        "Stock": max(len(str(item["Stock"])) for item in inventory),
    }

    for key in widths:
        widths[key] = max(widths[key], len(key))

    fmt = (f"{{ID:<{widths['ID']}}} | "
        f"{{Name:<{widths['Name']}}} | "
        f"{{Price:<{widths['Price']}}} | "
        f"{{Stock:<{widths['Stock']}}}"
    )

    print("\nCurrent Inventory")
    print(fmt.format(**{h: h for h in headers}))
    
    total_width = sum(widths.values()) + (3 * (len(headers) - 1))
    print("-" * total_width)

    for item in inventory:
        print(
            fmt.format(
                ID=item["ID"],
                Name=item["Name"],
                Price=f"${item['Price']:.2f}",
                Stock=item["Stock"]
            )
        )
#endregion

#region generate next ID and format ID
def generate_next_id(inventory: list) -> str:
    #Generates the next sequential ID in the format 'P00X'.
    if not inventory:
        return "P001"
    
    max_num = 0
    for item in inventory:
        try:
            num_part = int(item["ID"].replace("P", ""))
            if num_part > max_num:
                max_num = num_part
        except (ValueError, KeyError):
            continue
            
    next_num = max_num + 1
    return f"P{next_num:03d}"

def format_id(user_input: str) -> str | None:
    #Standardizes user input into the 'P00X' format. Returns None if invalid.
    try:
        # Strip 'P' (case-insensitive), convert to integer, and pad to 3 digits
        digits = int(user_input.upper().replace("P", "").strip())
        if digits <= 0:
            return None
        return f"P{digits:03d}"
    except ValueError:
        return None
#endregion

#region add product
def add_product(inventory):
    new_id = generate_next_id(inventory)
    name = input("Enter product name: ").strip()

    if name == "":
        print("Product name cannot be empty.")
        return

    price_input = input("Enter product price S$: ").strip()
    try:
        price = float(price_input)
    except ValueError:
        print("Invalid price. Please enter a valid number.")
        return
    if price < 0:
        print("Price cannot be negative.")
        return

    stock_input = input("Enter product stock quantity: ").strip()
    try:
        stock = int(stock_input)
    except ValueError:
        print("Invalid stock quantity. Please enter a valid integer.")
        return
    if stock < 0:
        print("Stock quantity cannot be negative.")
        return

    new_product = {
        "ID": new_id,
        "Name": name,
        "Price": price,
        "Stock": stock
    }

    inventory.append(new_product)
    print(f"Product '{name}' added successfully with ID {new_id}.")
#endregion

#region update stock
def update_stock(inventory):
    raw_id = input("Enter product ID (e.g., 1, 001, or P001): ").strip()
    product_id = format_id(raw_id)
    
    if product_id is None:
        print("Invalid product ID.")
        return
    
    product = next((item for item in inventory if item["ID"] == product_id), None)
    if product is None:
        print(f"No product found with ID {product_id}.")
        return
    
    print("-" * 40)
    print("Product Found:")
    print(f"ID: {product['ID']}")
    print(f"Name: {product['Name']}")
    print(f"Current Stock: {product['Stock']}\n")
    print("-" * 40)

    stock_input = input("Enter the new stock quantity: ").strip()
    try:
        stock = int(stock_input)
    except ValueError:
        print("Invalid input. Stock quantity must be a whole number.")
        return
    if stock < 0:
        print("Stock quantity cannot be negative.")
        return
    
    product["Stock"] = stock
    print(f"Product '{product['Name']}' stock updated successfully to {stock}.")
#endregion

#region search product
def search_product(inventory):
    raw_id = input("Enter product ID (e.g., 1, 001, or P001): ").strip()
    product_id = format_id(raw_id)
    
    if product_id is None:
        print("Invalid product ID.")
        return

    product = next((item for item in inventory if item["ID"] == product_id), None)
    if product is None:
        print(f"No product found with ID {product_id}.")
    else:
        print(f"Product found: {product['Name']} \nPrice: ${product['Price']:.2f} \nStock: {product['Stock']}")
#endregion

#region main function
def main():
    print(formattedHeader("INVENTORY MANAGEMENT SYSTEM", "="))
    inventory = load_inventory()

    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            print("Saving inventory before exit...")
            save_inventory(inventory)
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please select a valid option.")
#endregion

if __name__ == "__main__":
    main()