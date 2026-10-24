import json
from pathlib import Path
from inventory import Product, Inventory

# JSON file location
FILE_PATH = Path(__file__).parent / "inventory.json"

def load_inventory() -> Inventory:
    inventory = Inventory()
    if not FILE_PATH.exists():
        print("Inventory file not found. Starting with an empty inventory.")
        return inventory
    try:
        with FILE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("Inventory JSON must contain a list of products.")

        for item in data:
            product = Product(product_id=item["ID"], name=item["Name"], price=float(item["Price"]), stock=int(item["Stock"]))
            inventory.add_product(product)
        print("Inventory loaded successfully.")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Unable to load inventory: {error}") from error
    return inventory

def save_inventory(inventory: Inventory) -> None:
    data = [product.to_dict() for product in inventory.get_products().values()]
    with FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print("Inventory saved successfully.")

def display_menu() -> None:
    """Display the main menu."""
    print("\n===== Inventory Management System =====")
    print("1. Display all products")
    print("2. Add a new product")
    print("3. Update product stock")
    print("4. Search for a product")
    print("5. Save inventory")
    print("6. Exit")

def add_product(inventory: Inventory) -> None:
    try:
        name = input("Enter product name: ").strip()
        if not name:
            print("Product name cannot be empty.")
            return
        price = float(input("Enter product price: $"))
        if price < 0:
            print("Price cannot be negative.")
            return

        stock = int(input("Enter initial stock quantity: "))
        product_id = inventory.generate_next_id()
        product = Product(product_id=product_id, name=name, price=price, stock=stock)
        inventory.add_product(product)
        print(f"Product {product_id} added successfully.")
    except ValueError as error:
        print(f"Invalid input: {error}")

def update_product_stock(inventory: Inventory) -> None:
    product_id = input("Enter product ID: ").strip().upper()
    product = inventory.search_product(product_id)

    if product is None:
        print("Product not found.")
        return
    print(f"Current stock for {product.name}: {product.stock}")

    try:
        quantity = int(input("Enter new stock quantity: "))
        if inventory.update_stock(product_id, quantity):
            print("Stock updated successfully.")
    except ValueError as error:
        print(f"Invalid input: {error}")

def search_product(inventory: Inventory) -> None:
    product_id = input("Enter product ID to search: ").strip().upper()
    product = inventory.search_product(product_id)

    if product is None:
        print("Product not found.")
    else:
        print("\nProduct found:")
        product.display_information()

def main() -> None:
    try:
        inventory = load_inventory()
    except ValueError as error:
        print(error)
        return

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()
        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_product_stock(inventory)
        elif choice == "4":
            search_product(inventory)
        elif choice == "5":
            try:
                save_inventory(inventory)
            except OSError as error:
                print(f"Unable to save inventory: {error}")
        elif choice == "6":
            try:
                save_inventory(inventory)
                print("Exiting Inventory Management System.")
            except OSError as error:
                print(f"Unable to save inventory: {error}")
                print("Exiting without saving the latest changes.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main()
