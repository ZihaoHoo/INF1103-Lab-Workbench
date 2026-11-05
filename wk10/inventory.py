from abc import ABC, abstractmethod
from dataclasses import dataclass
import math

#region Shipping interface
class CanBeShipped(ABC):
    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass
#endregion

#region Supplier
@dataclass(slots=True)
class Supplier:
    supplier_id: str
    name: str
    contact_email: str

    def display_information(self) -> None:
        print(f"Supplier ID: {self.supplier_id}\nSupplier Name: {self.name}\nContact Email: {self.contact_email}")

    def to_dict(self) -> dict:
        return {"Supplier_ID": self.supplier_id, "Name": self.name, "Contact_Email": self.contact_email}
#endregion

#region Product
@dataclass(slots=True)
class Product(ABC):
    product_id: str
    name: str
    price: float
    stock: int
    supplier: Supplier

    def __post_init__(self) -> None:
        self.validate_stock(self.stock)
        if not isinstance(self.supplier, Supplier):
            raise TypeError("Supplier must be a Supplier object.")
        if isinstance(self.price, bool) or not isinstance(self.price, (int, float)) or not math.isfinite(self.price) or self.price < 0:
            raise ValueError("Price must be a finite non-negative number.")

    def validate_stock(self, quantity: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("Stock quantity must be a whole number.")
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")

    def update_stock(self, quantity: int) -> None:
        self.validate_stock(quantity)
        self.stock = quantity

    def display_information(self) -> None:
        print(f"ID: {self.product_id}\nName: {self.name}\nPrice: ${self.price:.2f}\nStock: {self.stock}\nSupplier: {self.supplier.name}")

    def to_dict(self) -> dict:
        return {"ID": self.product_id, "Name": self.name, "Price": self.price, "Stock": self.stock, "Supplier": self.supplier.to_dict()}
    
    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass
#endregion

#region PhysicalProduct
class PhysicalProduct(Product, CanBeShipped):
    def __init__(self, product_id: str, name: str, price: float, stock: int, weight: float, supplier: Supplier) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight < 0:
            raise ValueError("Weight must be a finite non-negative number.")
        self.weight = weight
    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.weight:.2f} kg")
    def get_fulfilment_info(self) -> str:
        return "Requires physical shipping."
    def calculate_shipping_cost(self) -> float:
        return round(self.weight * 2.00, 2)
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"Type": "physical", "Weight": self.weight})
        return data
#endregion

# Manages a collection of Product objects using a dictionary.
#region Inventory class
class Inventory:
    def __init__(self) -> None:
        self.__products: dict[str, Product] = {}

    def add_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("Only Product objects can be added.")

        if product.product_id in self.__products:
            raise ValueError(f"Product ID {product.product_id} already exists.")
        self.__products[product.product_id] = product
    
    def remove_product(self, product_id: str) -> None:
        product_id = product_id.strip().upper()
        if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
        self.__products.pop(product_id, None)

    def find_products(self, query: str) -> list[Product]:
        query = query.strip()
        if not query: return []
        product_id = query.upper()
        if product_id.isdigit(): product_id = f"P{int(product_id):03d}"
        product = self.__products.get(product_id)
        if product is not None: return [product]
        return [product for product in self.__products.values() if query.casefold() in product.name.casefold()]
    
    def update_stock(self, product_id: str, quantity: int) -> bool:
        product = self.__products.get(product_id.strip().upper())
        if product is None and product_id.strip().isdigit():
            product = self.__products.get(f"P{int(product_id.strip()):03d}")
        if product is None: return False
        product.update_stock(quantity)
        return True
    
    @staticmethod
    def display_products(products: list[Product]) -> None:
        if not products:
            print("No products found.")
            return
        headers = ["ID", "Name", "Type", "Price", "Stock", "Supplier", "Fulfilment"]
        rows = [[product.product_id, product.name, type(product).__name__.removesuffix("Product"), f"${product.price:.2f}", 
                 str(product.stock), product.supplier.name, product.get_fulfilment_info() ] for product in products ]
        widths = [max(len(str(value)) for value in [headers[i]] + [row[i] for row in rows]) for i in range(len(headers))]
        fmt = " | ".join(f"{{:<{width}}}" for width in widths)
        print(fmt.format(*headers))
        print("-" * (sum(widths) + 3 * (len(headers) - 1)))
        for row in rows:
            print(fmt.format(*row))

    def display_all(self) -> None:
        print("\n===== Current Inventory =====")
        self.display_products(list(self.__products.values()))

    def generate_next_id(self) -> str:
        max_num = 0
        for product_id in self.__products:
            try:
                number = int(product_id.removeprefix("P"))
                max_num = max(max_num, number)
            except ValueError:
                continue

        return f"P{max_num + 1:03d}"

    def get_products(self) -> dict[str, Product]:
        return self.__products.copy()

    def __len__(self) -> int:
        return len(self.__products)
#endregion

#region DigitalProduct
class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, price: float, stock: int, download_size: float, supplier: Supplier) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        if isinstance(download_size, bool) or not isinstance(download_size, (int, float)) or not math.isfinite(download_size) or download_size < 0:
            raise ValueError("Download size must be a finite non-negative number.")
        self.download_size = download_size
    def display_information(self) -> None:
        super().display_information()
        print(f"Download Size: {self.download_size:.2f} MB")
    def get_fulfilment_info(self) -> str:
        return "Delivered digitally via download."
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"Type": "digital", "Download_Size": self.download_size})
        return data
#endregion

#region OrderLine
@dataclass(slots=True)
class OrderLine:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValueError("Order quantity must be a whole number.")
        if self.quantity <= 0:
            raise ValueError("Order quantity must be greater than zero.")

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity

    def display_information(self) -> None:
        print(f"Product: {self.product.name}\nQuantity: {self.quantity}\nSubtotal: ${self.calculate_subtotal():.2f}")
#endregion

#region Order
class Order:
    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

    @property
    def order_lines(self) -> tuple[OrderLine, ...]:
        return tuple(self.__order_lines)

    def add_order_line(self, product: Product, quantity: int) -> None:
        if not isinstance(product, Product): raise TypeError("Order line requires a Product object.")
        order_line = OrderLine(product, quantity)
        already_ordered = sum(line.quantity for line in self.__order_lines if line.product is product)
        available_stock = product.stock - already_ordered
        if quantity > available_stock: raise ValueError(f"Only {available_stock} units available for {product.name}.")
        self.__order_lines.append(order_line)

    def remove_order_line(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise ValueError("Order line index must be a whole number.")

        if index < 0 or index >= len(self.__order_lines):
            raise IndexError("Order line index does not exist.")

        self.__order_lines.pop(index)

    def calculate_total(self) -> float:
        return sum(line.calculate_subtotal() for line in self.__order_lines)

    def display_information(self) -> None:
        print(f"\nOrder ID: {self.order_id}")
        if not self.__order_lines:
            print("No order lines found.")
            return
        for index, line in enumerate(self.__order_lines, start=1):
            line.display_information()
        print(f"\nOrder Total: ${self.calculate_total():.2f}")

    def to_dict(self) -> dict:
        return {
            "Order_ID": self.order_id,
            "Order_Lines": [
                {"Product_ID": line.product.product_id, "Quantity": line.quantity}
                for line in self.__order_lines
            ]
        }
#endregion