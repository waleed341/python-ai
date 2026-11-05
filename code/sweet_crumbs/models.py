"""Nested validated orders. Run from code/: uv run python -m sweet_crumbs.models."""
import re
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from .pricing import calculate_total

class OrderItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100, description="Requested item; preserve unknown items to flag them")
    quantity: int = Field(strict=True, ge=1, le=100, description="Positive whole requested quantity from 1 to 100")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        name = value.lower()
        aliases = {"cupcakes":"cupcake", "brownies":"brownie", "cookies":"cookie",
                   "chocolate cakes":"chocolate cake", "custom cakes":"custom cake"}
        return aliases.get(name, name)

class Order(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    is_order: bool = Field(strict=True, description="True only for an explicit purchase request; false for questions")
    customer: str = Field(default="", max_length=100, description="Exact customer name stated in the message; empty if absent")
    address: str = Field(default="", max_length=300, description="Exact address stated in the message; empty if absent")
    items: list[OrderItem] = Field(default_factory=list, max_length=30, description="Requested products; empty for non-order messages")

    def problems(self, prices: dict[str, int], message: str) -> list[str]:
        """Find business-rule violations that a JSON schema cannot establish."""
        if not self.is_order:
            return ["non-order message contains bakery items"] if self.items else []
        checks = []
        if not self.customer:
            checks.append("customer name is missing")
        elif not re.search(r"(?<!\w)" + re.escape(self.customer) + r"(?!\w)", message, re.I):
            checks.append(f"customer '{self.customer}' was not in the message")
        if self.address and self.address.casefold() not in message.casefold():
            checks.append("address was not in the message")
        if not self.items:
            checks.append("no bakery items supplied")
        checks.extend(f"'{item.name}' is not on the menu" for item in self.items if item.name not in prices)
        for item in self.items:
            if re.search(r"\b(?:zero|0)\s+" + re.escape(item.name) + r"s?\b", message, re.I):
                checks.append(f"message requests zero '{item.name}'; quantity must be positive")
        return checks

    def total(self, prices: dict[str, int]) -> int:
        """Calculate a quote only when every item has an official price."""
        return calculate_total([item.model_dump() for item in self.items], prices)

if __name__ == "__main__":
    order = Order(is_order=True, customer="Ali", items=[{"name":"Cupcake","quantity":2}])
    assert order.total({"cupcake":250}) == 500
    assert order.problems({"cupcake":250}, "Ali wants 2 cupcakes") == []
    assert order.problems({"cupcake":250}, "Sara wants 2 cupcakes")
    assert order.problems({}, "Ali wants a cupcake")
    for quantity in (0,-1,True,1.5,101):
        try:
            OrderItem(name="cupcake", quantity=quantity)
        except ValidationError:
            pass
        else:
            raise AssertionError(f"Accepted quantity {quantity}")
    print("Models: nested validation, name checks and pricing tests passed.")
