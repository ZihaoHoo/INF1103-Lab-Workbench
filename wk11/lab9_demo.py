from pathlib import Path
from discounts import BulkDiscount, PercentageDiscount, StudentDiscount
from inventory import Inventory, Order, ProductFactory, Supplier
from inventory_manager import get_positive_float, load_products

# Demonstrate the lab requirements without modifying the saved inventory.
def main() -> None:
    supplier = Supplier("SUP001", "Demo Supplier", "demo@example.com")

    product = ProductFactory.create("physical", "DEMO001", "Demo Product", 125.0, 10, supplier, weight=1.0)

    # Switch strategies on the same order whose subtotal is $250.
    order = Order("DEMO001", BulkDiscount(200, 20))
    order.add_order_line(product, 2)
    print(f"Bulk discount: ${order.calculate_total():.2f}")

    order.set_discount(PercentageDiscount(10))
    print(f"Percentage discount: ${order.calculate_total():.2f}")

    order.set_discount(StudentDiscount())
    print(f"Student discount: ${order.calculate_total():.2f}")

    # Show the factory's response to an unsupported product type
    try:
        ProductFactory.create("service", "S001", "Installation", 30, 5, supplier)
    except ValueError as error:
        print(f"Factory error: {error}")

    # Load the sample into a fresh inventory so existing IDs do not interfere
    csv_path = Path(__file__).with_name("products.csv")
    inventory = Inventory()
    load_products(str(csv_path), inventory, supplier)
    inventory.display_all()

    # Exercise the missing file path and its finally block.
    missing_path = Path(__file__).with_name("missing_products.csv")
    load_products(str(missing_path), Inventory(), supplier)

    # Enter abc, then -5, then 12.50 to check the input predictions.
    price = get_positive_float("\nEnter a positive price: ")
    print(f"Accepted price: ${price:.2f}")

if __name__ == "__main__":
    main()