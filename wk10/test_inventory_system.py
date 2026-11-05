from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch
from inventory import DigitalProduct, Inventory, Order, PhysicalProduct, Product, Supplier
from inventory_manager import create_order, generate_next_order_id, load_inventory, save_inventory


class TestLab8(unittest.TestCase):
    def setUp(self) -> None:
        self.supplier = Supplier("S001", "ABC Supplies", "abc@example.com")
        self.physical = PhysicalProduct("P001", "CD", 12.0, 20, 0.5, self.supplier)
        self.digital = DigitalProduct("P002", "VSCode", 12.0, 30, 250.0, self.supplier)
    #Region Association
    def test_01_supplier_association(self) -> None:
        self.assertIs(self.physical.supplier, self.supplier)
        self.assertIs(self.digital.supplier, self.supplier)
    def test_02_supplier_reference(self) -> None:
        product = self.physical
        supplier = self.supplier
        del supplier
        self.assertEqual(product.supplier.name, "ABC Supplies")
    #Endregion
    #Region Aggregation
    def test_03_add_product(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        self.assertEqual(inventory.find_products("P001"), [self.physical])
    def test_04_remove_product(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        inventory.remove_product("P001")
        self.assertEqual(inventory.find_products("P001"), [])
        self.assertEqual(self.physical.name, "CD")
    def test_05_transfer_product(self) -> None:
        inventory_a = Inventory()
        inventory_b = Inventory()
        inventory_a.add_product(self.physical)
        inventory_a.remove_product("P001")
        inventory_b.add_product(self.physical)
        self.assertIs(inventory_b.find_products("P001")[0], self.physical)
    #Endregion
    #Region Composition
    def test_06_order_subtotal(self) -> None:
        order = Order("O001")
        order.add_order_line(self.physical, 2)
        self.assertEqual(order.order_lines[0].calculate_subtotal(), 24.0)
    def test_07_order_total(self) -> None:
        order = Order("O001")
        order.add_order_line(self.physical, 2)
        order.add_order_line(self.digital, 3)
        self.assertEqual(order.calculate_total(), 60.0)
    def test_08_separate_order_lines(self) -> None:
        order_a = Order("O001")
        order_b = Order("O002")
        order_a.add_order_line(self.physical, 2)
        order_b.add_order_line(self.physical, 1)
        self.assertIsNot(order_a.order_lines[0], order_b.order_lines[0])
        self.assertIs(order_a.order_lines[0].product, order_b.order_lines[0].product )
    def test_09_remove_order_line(self) -> None:
        order = Order("O001")
        order.add_order_line(self.physical, 2)
        order.remove_order_line(0)
        self.assertEqual(len(order.order_lines), 0)
        self.assertEqual(order.calculate_total(), 0.0)
    def test_10_invalid_quantity(self) -> None:
        order = Order("O001")
        with self.assertRaises(ValueError):
            order.add_order_line(self.physical, 0)
    #Endregion
    #Region Liskov Substitution Principle

    def test_11_lsp_stock_update(self) -> None:
        products: list[Product] = [self.physical, self.digital]
        for product in products:
            product.update_stock(10)
            self.assertEqual(product.stock, 10)
    def test_12_lsp_stock_validation(self) -> None:
        products: list[Product] = [self.physical, self.digital]
        for product in products:
            with self.assertRaises(ValueError):
                product.update_stock(-1)
    def test_13_lsp_common_methods(self) -> None:
        def show_product_details(product: Product) -> None:
            product.display_information()
            print(product.get_fulfilment_info())
        output = StringIO()
        with redirect_stdout(output):
            show_product_details(self.physical)
            show_product_details(self.digital)
        result = output.getvalue()
        self.assertIn("Requires physical shipping.", result)
        self.assertIn("Delivered digitally via download.", result)
    #Endregion
    #Region Polymorphism
    def test_14_polymorphism(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        inventory.add_product(self.digital)
        output = StringIO()
        with redirect_stdout(output): inventory.display_all()
        result = output.getvalue()
        self.assertIn("Requires physical shipping.", result)
        self.assertIn("Delivered digitally via download.", result)
        self.assertIn("Physical", result)
        self.assertIn("Digital", result)
        self.assertIn("P001", result)
        self.assertIn("P002", result)
    #Endregion
    #Region Product Search
    def test_15_search_full_id(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        self.assertEqual(inventory.find_products("P001"), [self.physical])
    def test_16_search_numeric_id(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        self.assertEqual(inventory.find_products("001"), [self.physical])
    def test_17_search_partial_name(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        self.assertEqual(inventory.find_products("cd"), [self.physical])
    def test_18_search_multiple_products(self) -> None:
        inventory = Inventory()
        milk = PhysicalProduct("P003", "Milk", 3.50, 20, 1.0, self.supplier)
        chocolate_milk = PhysicalProduct("P004", "Chocolate Milk", 4.20, 15, 1.0, self.supplier)
        low_fat_milk = PhysicalProduct("P005", "Low Fat Milk", 3.80, 10, 1.0, self.supplier)
        for product in [milk, chocolate_milk, low_fat_milk]: inventory.add_product(product)
        results = inventory.find_products("milk")
        self.assertEqual(len(results), 3)
        self.assertIn(milk, results)
        self.assertIn(chocolate_milk, results)
        self.assertIn(low_fat_milk, results)
    def test_19_search_not_found(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        self.assertEqual(inventory.find_products("Nonexistent"), [])
    #Endregion
    def test_20_cli_create_order(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        inventory.add_product(self.digital)
        inputs = ["O001", "001", "2", "002", "3", ""]
        output = StringIO()
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(output):
                create_order(inventory, {})
        self.assertIn("Order ID: O001", output.getvalue())
        self.assertIn("Order Total: $60.00", output.getvalue())
    #Region Order Persistence
    def test_21_generate_first_order_id(self) -> None:
        self.assertEqual(generate_next_order_id({}), "O001")
    def test_22_generate_next_order_id(self) -> None:
        orders = {"O001": Order("O001"), "O003": Order("O003")}
        self.assertEqual(generate_next_order_id(orders), "O004")
    def test_23_order_serialization(self) -> None:
        order = Order("O001")
        order.add_order_line(self.physical, 2)
        self.assertEqual(order.to_dict(), {"Order_ID": "O001", "Order_Lines": [{"Product_ID": "P001", "Quantity": 2}]})
    def test_24_empty_order_cancelled(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        with patch("builtins.input", side_effect=[""]):
            with redirect_stdout(StringIO()):
                order = create_order(inventory, {})
        self.assertIsNone(order)
    def test_25_create_order_by_numeric_product_id(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        with patch("builtins.input", side_effect=["001", "2", ""]):
            with redirect_stdout(StringIO()):
                order = create_order(inventory, {})
        self.assertIsNotNone(order)
        self.assertEqual(order.order_id, "O001")
        self.assertIs(order.order_lines[0].product, self.physical)
        self.assertEqual(order.calculate_total(), 24.0)
    def test_26_order_save_load(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        order = Order("O001")
        order.add_order_line(self.physical, 2)
        orders = {"O001": order}
        with TemporaryDirectory() as directory:
            test_path = Path(directory) / "inventory.json"
            with patch("inventory_manager.FILE_PATH", test_path):
                save_inventory(inventory, orders)
                loaded_inventory, loaded_orders = load_inventory()
            self.assertEqual(len(loaded_orders), 1)
            self.assertEqual(loaded_orders["O001"].calculate_total(), 24.0)
            self.assertIs(loaded_orders["O001"].order_lines[0].product, loaded_inventory.find_products("P001")[0])
    #Endregion

if __name__ == "__main__":
    unittest.main(verbosity=2)