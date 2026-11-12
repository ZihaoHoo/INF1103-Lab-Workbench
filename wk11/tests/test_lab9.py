from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from discounts import (DiscountStrategy, NoDiscount, PercentageDiscount, BulkDiscount, StudentDiscount,)
from inventory import (DigitalProduct, Inventory, Order, OrderLine, PhysicalProduct, ProductFactory, Supplier,)
from inventory_manager import (choose_discount, get_positive_float, load_inventory, load_products, save_inventory,)

class TestLab9(unittest.TestCase):
    # Give each test independent products and supplier data.
    def setUp(self) -> None:
        self.supplier = Supplier("SUP001", "Test Supplier", "test@example.com")
        self.product = ProductFactory.create("physical", "P001", "Test Product", 125.0, 10, self.supplier, weight=1.0)

    def make_order(self, discount=None) -> Order:
        order = Order("O001", discount)
        order.add_order_line(self.product, 2)
        return order

    # Verify default, percentage, bulk, and student discount results.
    def test_default_discount(self) -> None:
        order = self.make_order()
        self.assertIsInstance(order.discount, NoDiscount)
        self.assertEqual(order.calculate_total(), 250.0)

    def test_percentage_discount(self) -> None:
        order = self.make_order(PercentageDiscount(10))
        self.assertEqual(order.calculate_total(), 225.0)

    def test_bulk_discount_boundaries(self) -> None:
        discount = BulkDiscount(200, 20)
        self.assertEqual(discount.apply(199), 199)
        self.assertEqual(discount.apply(200), 180)
        self.assertEqual(discount.apply(250), 230)

    def test_bulk_discount_does_not_make_total_negative(self) -> None:
        self.assertEqual(BulkDiscount(0, 20).apply(5), 0.0)

    def test_student_discount(self) -> None:
        order = self.make_order(StudentDiscount())
        self.assertEqual(order.calculate_total(), 237.5)

    def test_switch_strategy(self) -> None:
        order = self.make_order(BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 230.0)
        order.set_discount(PercentageDiscount(10))
        self.assertEqual(order.calculate_total(), 225.0)

    # Prove that Order can use a new strategy without being edited.
    def test_custom_strategy(self) -> None:
        class HalfPriceDiscount(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        order = self.make_order(HalfPriceDiscount())
        self.assertEqual(order.calculate_total(), 125.0)

    def test_shared_strategy(self) -> None:
        discount = PercentageDiscount(10)
        first = self.make_order(discount)
        second = self.make_order(discount)
        self.assertIs(first.discount, second.discount)

    def test_invalid_strategy(self) -> None:
        with self.assertRaises(TypeError):
            self.make_order().set_discount("percentage")

    def test_invalid_discount_parameters(self) -> None:
        for percentage in (-1, 101, float("nan"), float("inf"), True):
            with self.subTest(percentage=percentage):
                with self.assertRaises(ValueError):
                    PercentageDiscount(percentage)

        with self.assertRaises(ValueError):
            BulkDiscount(-1, 20)
        with self.assertRaises(ValueError):
            BulkDiscount(200, -1)

    # Verify that the factory selects the correct concrete product class.
    def test_factory_product_types(self) -> None:
        self.assertIsInstance(self.product, PhysicalProduct)
        self.assertEqual(self.product.weight, 1.0)

        digital = ProductFactory.create("digital", "D001", "Software", 49.90, 100, self.supplier, download_size=250.0)
        self.assertIsInstance(digital, DigitalProduct)
        self.assertEqual(digital.download_size, 250.0)

    def test_factory_unknown_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown product type: service"):
            ProductFactory.create("service", "S001", "Installation", 30, 5, self.supplier)

    # Confirm that both product subclasses preserve the base validation rules.
    def test_invalid_product_prices(self) -> None:
        for product_type in ("physical", "digital"):
            for price in (0, -5, float("nan"), float("inf"), True):
                with self.subTest(product_type=product_type, price=price):
                    with self.assertRaises(ValueError):
                        ProductFactory.create(product_type, "X001", "Invalid", price, 5, self.supplier)

    def test_invalid_stock(self) -> None:
        for product_type in ("physical", "digital"):
            for stock in (-1, 1.5, True):
                with self.subTest(product_type=product_type, stock=stock):
                    with self.assertRaises(ValueError):
                        ProductFactory.create(product_type, "X001", "Invalid", 10, stock, self.supplier)

    def test_invalid_order_quantities(self) -> None:
        for quantity in (0, -1, 1.5, True):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    OrderLine(self.product, quantity)

    # Check retry behaviour and the messages shown to the user.
    def test_positive_price_retries(self) -> None:
        output = StringIO()
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]):
            with redirect_stdout(output):
                result = get_positive_float("Price: ")

        self.assertEqual(result, 12.5)
        self.assertEqual(output.getvalue().splitlines(), [ "Please enter a valid number, e.g. 12.50", "Please enter a number greater than zero.", ])

    def test_nonfinite_price_input_retries(self) -> None:
        with patch("builtins.input", side_effect=["nan", "inf", "0", "10"]):
            with redirect_stdout(StringIO()):
                result = get_positive_float("Price: ")
        self.assertEqual(result, 10.0)

    def test_discount_selection_retries(self) -> None:
        output = StringIO()
        with patch("builtins.input", side_effect=["9", "4"]):
            with redirect_stdout(output):
                discount = choose_discount()
        self.assertIsInstance(discount, StudentDiscount)
        self.assertIn("Invalid choice.", output.getvalue())

    # Confirm that the supplied CSV skips two invalid rows and loads three products.
    def test_sample_csv(self) -> None:
        inventory = Inventory()
        path = Path(__file__).resolve().parents[1] / "products.csv"
        output = StringIO()

        with redirect_stdout(output):
            load_products(str(path), inventory, self.supplier)

        self.assertEqual(len(inventory), 3)
        self.assertEqual(set(inventory.get_products()), {"P001", "D001", "P003"})
        self.assertIsInstance(inventory.get_products()["D001"], DigitalProduct)
        self.assertEqual(output.getvalue().splitlines(),
            [
                "Skipping row 4: Unknown product type: service",
                "Skipping row 5: could not convert string to float: 'abc'",
                "3 products loaded.",
                "Load attempt finished.",
            ],
        )

    def test_missing_csv(self) -> None:
        inventory = Inventory()
        output = StringIO()

        with TemporaryDirectory() as directory:
            path = str(Path(directory) / "missing.csv")
            with redirect_stdout(output):
                load_products(path, inventory, self.supplier)

        self.assertEqual(len(inventory), 0)
        self.assertEqual(output.getvalue().splitlines(), [ f"Products file not found: {path}", "Load attempt finished.",])

    def test_malformed_csv_row_does_not_stop_loading(self) -> None:
        text = "product_type,product_id,name,price,stock_quantity\nphysical,BROKEN\nphysical,P009,Valid Product,10,3\n"
        inventory = Inventory()
        output = StringIO()

        with TemporaryDirectory() as directory:
            path = Path(directory) / "products.csv"
            path.write_text(text, encoding="utf-8")
            with redirect_stdout(output):
                load_products(str(path), inventory, self.supplier)

        self.assertEqual(len(inventory), 1)
        self.assertIn("Skipping row 2: Expected exactly 5 columns.", output.getvalue())
        self.assertIn("1 products loaded.", output.getvalue())

    # Ensure discounts survive saving and historical orders do not deduct stock twice.
    def test_discount_save_load_with_sold_out_product(self) -> None:
        discounts = [(NoDiscount(), 250.0), (PercentageDiscount(10), 225.0), (BulkDiscount(200, 20), 230.0), (StudentDiscount(), 237.5)]

        for discount, expected_total in discounts:
            with self.subTest(discount=type(discount).__name__):
                product = ProductFactory.create("physical", "P001", "Test Product", 125, 2, self.supplier)
                inventory = Inventory()
                inventory.add_product(product)

                order = Order("O001", discount)
                order.add_order_line(product, 2)
                order.fulfil_order()
                self.assertEqual(product.stock, 0)

                with TemporaryDirectory() as directory:
                    path = Path(directory) / "inventory.json"
                    with patch("inventory_manager.FILE_PATH", path):
                        with redirect_stdout(StringIO()):
                            save_inventory(inventory, {"O001": order})
                            loaded_inventory, loaded_orders = load_inventory()

                restored = loaded_orders["O001"]
                self.assertIsInstance(restored.discount, type(discount))
                self.assertEqual(restored.calculate_total(), expected_total)
                self.assertEqual(loaded_inventory.get_products()["P001"].stock, 0)
                self.assertIs(restored.order_lines[0].product, loaded_inventory.get_products()["P001"])
                with self.assertRaises(ValueError):
                    restored.fulfil_order()

    def test_old_order_without_discount_data(self) -> None:
        data = {"Order_ID": "O001", "Order_Lines": [{"Product_ID": "P001", "Quantity": 2}]}
        order = Order.from_dict(data, {"P001": self.product})
        self.assertIsInstance(order.discount, NoDiscount)
        self.assertEqual(order.calculate_total(), 250.0)

if __name__ == "__main__":
    unittest.main(verbosity=2)