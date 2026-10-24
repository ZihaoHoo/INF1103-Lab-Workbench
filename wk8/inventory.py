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