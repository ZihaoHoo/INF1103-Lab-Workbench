import json
from pathlib import Path
from inventory import Supplier, Product, PhysicalProduct, DigitalProduct, Inventory, Order

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

        suppliers: dict[str, Supplier] = {}

        for item in data:
            product_id = item["ID"]
            name = item["Name"]
            price = item["Price"]
            stock = item["Stock"]
            product_type = item["Type"]
            supplier_data = item["Supplier"]
            supplier_id = supplier_data["Supplier_ID"]

            if supplier_id not in suppliers:
                suppliers[supplier_id] = Supplier(supplier_id,supplier_data["Name"], supplier_data["Contact_Email"])
            else:
                existing_supplier = suppliers[supplier_id]
                if (existing_supplier.name != supplier_data["Name"] or existing_supplier.contact_email != supplier_data["Contact_Email"]):
                    raise ValueError(f"Conflicting details for supplier {supplier_id}.")
                
            supplier = suppliers[supplier_id]
            if product_type == "physical":
                product = PhysicalProduct(product_id, name, price, stock, item["Weight"], supplier)
            elif product_type == "digital":
                product = DigitalProduct( product_id, name, price, stock, item["Download_Size"], supplier)
            else:
                raise ValueError(f"Unknown product type: {product_type}")
            inventory.add_product(product)
        print("Inventory loaded successfully.")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Unable to load inventory: {error}") from error
    return inventory

def save_inventory(inventory: Inventory) -> None:
    data = [product.to_dict() for product in inventory.get_products().values()]
    with FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print("Inventory saved successfully.")

def display_menu() -> None:
    options = ["Display all products", "Add a new product", "Update product stock", "Search for a product", "Remove a product", "Create an order", "Save inventory", "Exit"]
    print("\n===== Inventory Management System =====")
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")

#region Supplier input
def get_supplier(inventory: Inventory) -> Supplier:
    suppliers: dict[str, Supplier] = {}
    for product in inventory.get_products().values():
        supplier = product.supplier
        suppliers[supplier.supplier_id] = supplier
    supplier_id = input("Enter supplier ID: ").strip().upper()
    if not supplier_id:
        raise ValueError("Supplier ID cannot be empty.")
    if supplier_id in suppliers:
        print("Using existing supplier.")
        return suppliers[supplier_id]
    print("Supplier not found. Creating a new supplier.")
    name = input("Enter supplier name: ").strip()
    contact_email = input("Enter supplier email: ").strip()
    if not name or not contact_email:
        raise ValueError("Supplier name and email cannot be empty.")
    return Supplier(supplier_id, name, contact_email)
#endregion

def add_product(inventory: Inventory) -> None:
    product_type = input( "Choose product type (1. Physical, 2. Digital): " ).strip()
    if product_type not in ("1", "2"):
        print("Invalid product type. Please enter 1 or 2.")
        return
    try:
        name = input("Enter product name: ").strip()
        if not name:
            print("Product name cannot be empty.")
            return
        price = float(input("Enter product price: $"))
        stock = int(input("Enter initial stock quantity: "))

        if price < 0:
            raise ValueError("Price cannot be negative.")
        supplier = get_supplier(inventory)
        product_id = inventory.generate_next_id()

        if product_type == "1":
            weight = float(input("Enter product weight (kg): "))
            if weight < 0:
                raise ValueError("Weight cannot be negative.")
            product = PhysicalProduct(product_id, name, price, stock, weight, supplier)
        else:
            download_size = float(input("Enter download size (MB): "))
            if download_size < 0:
                raise ValueError("Download size cannot be negative.")
            product = DigitalProduct(product_id, name, price, stock, download_size, supplier)
        inventory.add_product(product)
        print(f"Product {product_id} added successfully.")
    except ValueError as error:
        print(f"Invalid input: {error}")

def update_product_stock(inventory: Inventory) -> None:
    product_id = input("Enter product ID: ").strip().upper()
    if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
    products = inventory.find_products(product_id)
    product = next((item for item in products if item.product_id == product_id), None)
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

def find_products(inventory: Inventory) -> None:
    query = input("Enter product ID or name: ").strip()
    products = inventory.find_products(query)
    if not products:
        print("No matching products found.")
        return
    print(f"\nFound {len(products)} matching product(s):")
    inventory.display_products(products)

#region Remove product
def remove_product(inventory: Inventory) -> None:
    product_id = input("Enter product ID: ").strip().upper()
    if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
    products = inventory.find_products(product_id)
    product = next((item for item in products if item.product_id == product_id), None)
    if product is None:
        print("Product not found.")
        return
    inventory.remove_product(product_id)
    print(f"Product {product_id} removed successfully.")
#endregion

#region Create order
def create_order(inventory: Inventory) -> None:
    order_id = input("Enter order ID: ").strip()
    if not order_id:
        print("Order ID cannot be empty.")
        return
    order = Order(order_id)
    while True:
        product_id = input("Enter product ID (blank to finish): ").strip().upper()
        if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
        products = inventory.find_products(product_id)
        product = next((item for item in products if item.product_id == product_id), None)
        if not product_id:
            break
        product = inventory.find_products(product_id)
        if product is None:
            print("Product not found.")
            continue
        try:
            quantity = int(input("Enter order quantity: "))
            order.add_order_line(product, quantity)
            print("Order line added successfully.")
        except ValueError as error:
            print(f"Invalid input: {error}")
    order.display_information()
    print("Order preview completed. Order was not saved.")
#endregion

def main() -> None:
    try:
        inventory = load_inventory()
    except ValueError as error:
        print(error)
        return
    while True:
        display_menu()
        choice = input("Enter your choice (1-8): ").strip()
        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_product_stock(inventory)
        elif choice == "4":
            find_products(inventory)
        elif choice == "5":
            remove_product(inventory)
        elif choice == "6":
            create_order(inventory)
        elif choice == "7":
            try:
                save_inventory(inventory)
            except OSError as error:
                print(f"Unable to save inventory: {error}")
        elif choice == "8":
            try:
                save_inventory(inventory)
                print("Exiting Inventory Management System.")
            except OSError as error:
                print(f"Unable to save inventory: {error}")
                print("Exiting without saving the latest changes.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")

if __name__ == "__main__":
    main()
