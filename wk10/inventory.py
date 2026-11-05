from abc import ABC, abstractmethod
from dataclasses import dataclass

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
        self.__products.pop(product_id, None)

    def find_product(self, product_id: str) -> Product | None:
        return self.__products.get(product_id)
    
    def update_stock(self, product_id: str, quantity: int) -> bool:
        product = self.find_product(product_id)
        if product is None: return False
        product.update_stock(quantity)
        return True

    def display_all(self) -> None:
        if not self.__products:
            print("No products found in inventory.")
            return
        print("\n===== Current Inventory =====")

        for product in self.__products.values():
            print()
            product.display_information()
            print(f"Fulfilment: {product.get_fulfilment_info()}")
            print("-" * 30)

    def display_all_products(self) -> None:
        if not self.__products:
            print("No products found in inventory.")
            return

        for product in self.__products.values():
            print()
            product.display_information()
            print(f"Fulfilment: {product.get_fulfilment_info()}")

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