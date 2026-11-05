import unittest
from contextlib import redirect_stdout
from io import StringIO
from inventory import (Supplier, Product, PhysicalProduct, DigitalProduct, Inventory, Order)

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
        self.assertIs(inventory.find_product("P001"), self.physical)
    def test_04_remove_product(self) -> None:
        inventory = Inventory()
        inventory.add_product(self.physical)
        inventory.remove_product("P001")
        self.assertIsNone(inventory.find_product("P001"))
        self.assertEqual(self.physical.name, "CD")
    def test_05_transfer_product(self) -> None:
        inventory_a = Inventory()
        inventory_b = Inventory()
        inventory_a.add_product(self.physical)
        inventory_a.remove_product("P001")
        inventory_b.add_product(self.physical)
        self.assertIs(inventory_b.find_product("P001"), self.physical)
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
        with redirect_stdout(output):
            inventory.display_all()
        result = output.getvalue()
        self.assertIn("Requires physical shipping.", result)
        self.assertIn("Delivered digitally via download.", result)
        self.assertIn("Weight: 0.50 kg", result)
        self.assertIn("Download Size: 250.00 MB", result)
    #Endregion
if __name__ == "__main__":
    unittest.main(verbosity=2)