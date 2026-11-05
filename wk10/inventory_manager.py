import json
from pathlib import Path
from inventory import Supplier, Product, PhysicalProduct, DigitalProduct, Inventory, Order

# JSON file location
FILE_PATH = Path(__file__).parent / "inventory.json"

def load_inventory() -> tuple[Inventory, dict[str, Order]]:
    inventory = Inventory()
    orders: dict[str, Order] = {}
    if not FILE_PATH.exists():
        print("Inventory file not found. Starting with empty data.")
        return inventory, orders
    try:
        with FILE_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            products_data, orders_data = data, []
        elif isinstance(data, dict):
            products_data = data["Products"]
            orders_data = data["Orders"]
        else:
            raise ValueError("Invalid inventory JSON format.")
        if not isinstance(products_data, list) or not isinstance(orders_data, list):
            raise ValueError("Products and Orders must be lists.")
        suppliers: dict[str, Supplier] = {}
        # Load products
        for item in products_data:
            supplier_data = item["Supplier"]
            supplier_id = supplier_data["Supplier_ID"]

            if supplier_id not in suppliers:
                suppliers[supplier_id] = Supplier(supplier_id, supplier_data["Name"], supplier_data["Contact_Email"])
            elif (suppliers[supplier_id].name != supplier_data["Name"] or suppliers[supplier_id].contact_email != supplier_data["Contact_Email"]):
                raise ValueError(f"Conflicting supplier details for {supplier_id}.")
            supplier = suppliers[supplier_id]
            product_id, name, price, stock = item["ID"], item["Name"], item["Price"], item["Stock"]
            if item["Type"] == "physical":
                product = PhysicalProduct(product_id, name, price, stock, item["Weight"], supplier)
            elif item["Type"] == "digital":
                product = DigitalProduct(product_id, name, price, stock, item["Download_Size"], supplier)
            else:
                raise ValueError(f"Unknown product type: {item['Type']}")
            inventory.add_product(product)
        # Load orders
        for item in orders_data:
            order_id = item["Order_ID"]
            if order_id in orders: raise ValueError(f"Duplicate Order ID: {order_id}")

            order = Order(order_id)
            for line in item["Order_Lines"]:
                product_id = line["Product_ID"]
                products = inventory.find_products(product_id)
                product = next((p for p in products if p.product_id == product_id), None)
                if product is None: raise ValueError(f"Order {order_id} references missing product {product_id}.")
                order.add_order_line(product, line["Quantity"])
            if not order.order_lines:
                raise ValueError(f"Order {order_id} contains no order lines.")
            order.mark_fulfilled()
            orders[order_id] = order
        print("Inventory and orders loaded successfully.")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Unable to load inventory: {error}") from error
    return inventory, orders

def save_inventory(inventory: Inventory, orders: dict[str, Order]) -> None:
    data = {
        "Products": [product.to_dict() for product in inventory.get_products().values()],
        "Orders": [order.to_dict() for order in orders.values()]
    }
    with FILE_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print("Inventory and orders saved successfully.")

#region Generate Order ID
def generate_next_order_id(orders: dict[str, Order]) -> str:
    max_num = 0
    for order_id in orders:
        try:
            number = int(order_id.removeprefix("O"))
            max_num = max(max_num, number)
        except ValueError:
            continue
    return f"O{max_num + 1:03d}"
#endregion

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
    if not products:
        print("Product not found.")
        return
    product = products[0]
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
def remove_product(inventory: Inventory, orders: dict[str, Order]) -> None:
    product_id = input("Enter Product ID to remove: ").strip().upper()
    if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
    products = inventory.find_products(product_id)
    product = next((item for item in products if item.product_id == product_id), None)
    if product is None:
        print("Product not found.")
        return
    for order in orders.values():
        if any(line.product is product for line in order.order_lines):
            print(f"Cannot remove {product_id}: referenced by Order {order.order_id}.")
            return
    inventory.remove_product(product_id)
    print(f"Product {product_id} removed successfully.")
#endregion

#region Create order
def create_order(inventory: Inventory, orders: dict[str, Order]) -> Order | None:
    if len(inventory) == 0:
        print("No products available in inventory.")
        return None
    order = Order(generate_next_order_id(orders))
    print(f"\n===== Create Order {order.order_id} =====")
    while True:
        product_id = input("\nEnter Product ID (blank to finish): ").strip().upper()
        if not product_id: break
        if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
        products = inventory.find_products(product_id)
        product = next((item for item in products if item.product_id == product_id), None)
        if product is None:
            print("Product not found. Please enter a valid Product ID.")
            continue
        print(f"Selected: {product.name} | Price: ${product.price:.2f} | Stock: {product.stock}")
        try:
            quantity = int(input("Enter quantity: "))
            order.add_order_line(product, quantity)
            print(f"Added {quantity} x {product.name} to order.")
        except ValueError as error:
            print(f"Invalid input: {error}")
    if not order.order_lines:
        print("Order cancelled. No products were added.")
        return None
    order.display_information()
    return order
#endregion

#region Main
def main() -> None:
    try:
        inventory, orders = load_inventory()
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
            remove_product(inventory, orders)
        elif choice == "6":
            order = create_order(inventory, orders)
            if order is not None:
                previous_stock = {line.product.product_id: line.product.stock for line in order.order_lines}
                try:
                    order.fulfil_order()
                    orders[order.order_id] = order
                    save_inventory(inventory, orders)
                    print(f"Order {order.order_id} saved successfully.\nInventory stock updated successfully.")
                except (ValueError, OSError) as error:
                    for product_id, stock in previous_stock.items():
                        products = inventory.find_products(product_id)
                        if products: products[0].update_stock(stock)
                    orders.pop(order.order_id, None)
                    print(f"Unable to complete order: {error}")
        elif choice == "7":
            try:
                save_inventory(inventory, orders)
            except OSError as error:
                print(f"Unable to save inventory: {error}")
        elif choice == "8":
            try:
                save_inventory(inventory, orders)
                print("Exiting Inventory Management System.")
            except OSError as error:
                print(f"Unable to save inventory: {error}")
                print("Exiting without saving the latest changes.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")
#endregion

if __name__ == "__main__":
    main()
