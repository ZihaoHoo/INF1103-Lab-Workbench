from abc import ABC, abstractmethod
import math

# Define the common operation used by every discount strategy.
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass

    def to_dict(self) -> dict:
        return {"Type": type(self).__name__}

# Leave the order total unchanged.
class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total

# Reduce the total by a configurable percentage.
class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float) -> None:
        if (isinstance(percentage, bool)
            or not isinstance(percentage, (int, float))
            or not math.isfinite(percentage)
            or not 0 <= percentage <= 100):
            raise ValueError("Percentage must be a finite number from 0 to 100.")
        self.percentage = percentage

    def apply(self, total: float) -> float:
        return round(total * (1 - self.percentage / 100), 2)

    def to_dict(self) -> dict:
        return {"Type": type(self).__name__, "Percentage": self.percentage}

# Deduct a fixed amount when the total reaches the threshold.
class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float) -> None:
        for label, value in (("Threshold", threshold), ("Amount", amount)):
            if (isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0):
                raise ValueError(f"{label} must be a finite non-negative number.")
        self.threshold = threshold
        self.amount = amount

    def apply(self, total: float) -> float:
        if total >= self.threshold:
            return round(max(0.0, total - self.amount), 2)
        return total

    def to_dict(self) -> dict:
        return {"Type": type(self).__name__, "Threshold": self.threshold, "Amount": self.amount}

# Add a student discount strategy without changing the Order calculation.
class StudentDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return round(total * 0.95, 2)


# Rebuild a saved strategy while supporting older orders with no discount data.
def discount_from_dict(data: dict | None) -> DiscountStrategy:
    if data is None:
        return NoDiscount()
    if not isinstance(data, dict):
        raise ValueError("Discount data must be a dictionary.")

    discount_type = data.get("Type")
    if discount_type == "NoDiscount":
        return NoDiscount()
    if discount_type == "PercentageDiscount":
        return PercentageDiscount(data["Percentage"])
    if discount_type == "BulkDiscount":
        return BulkDiscount(data["Threshold"], data["Amount"])
    if discount_type == "StudentDiscount":
        return StudentDiscount()
    raise ValueError(f"Unknown discount type: {discount_type}")