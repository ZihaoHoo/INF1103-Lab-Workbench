from dataclasses import dataclass

#region Product
@dataclass(slots=True)
class Product:
    product_id: str
    name: str
    price: float
    stock: int

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
        print(f"ID: {self.product_id}\nName: {self.name}\nPrice: ${self.price:.2f}\nStock: {self.stock}")

    def to_dict(self) -> dict:
        return {"ID": self.product_id, "Name": self.name, "Price": self.price, "Stock": self.stock}
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

    def search_product(self, product_id: str) -> Product | None:
        return self.__products.get(product_id)

    def update_stock(self, product_id: str, quantity: int) -> bool:
        product = self.search_product(product_id)
        if product is None:
            return False
        product.update_stock(quantity)
        return True

    def display_all(self) -> None:
        if not self.__products:
            print("No products found in inventory.")
            return

        headers = ["ID", "Name", "Price", "Stock"]
        rows = [[product.product_id, product.name, f"${product.price:.2f}", str(product.stock)] for product in self.__products.values()]
        widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
        fmt = (f"{{:<{widths[0]}}} | " f"{{:<{widths[1]}}} | " f"{{:<{widths[2]}}} | " f"{{:<{widths[3]}}}")

        print("\nCurrent Inventory")
        print(fmt.format(*headers))
        print("-" * (sum(widths) + 3 * (len(headers) - 1)))

        for row in rows:
            print(fmt.format(*row))

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