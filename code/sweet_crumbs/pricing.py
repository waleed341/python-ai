"""Trusted Python pricing. Run from code/: uv run python -m sweet_crumbs.pricing."""

def normalize_item(item: str) -> str:
    """Map ordinary bakery plurals to the official menu key."""
    name = item.strip().lower()
    return {"cupcakes":"cupcake", "brownies":"brownie", "cookies":"cookie",
            "chocolate cakes":"chocolate cake", "custom cakes":"custom cake"}.get(name, name)

def calculate_total(items: list[dict], prices: dict[str, int]) -> int:
    """Reject unknown products and invalid quantities before calculating a total."""
    if not items:
        raise ValueError("No bakery items supplied")
    total = 0
    for item in items:
        name, quantity = normalize_item(item["name"]), item["quantity"]
        if name not in prices:
            raise ValueError(f"Unknown item: {name}")
        if type(quantity) is not int or not 1 <= quantity <= 100:
            raise ValueError("Quantity must be a whole number from 1 to 100")
        total += prices[name] * quantity
    return total

if __name__ == "__main__":
    assert calculate_total([{"name":"cupcake", "quantity":2}], {"cupcake":250}) == 500
    for name, quantity in (("unknown",1),("cupcake",0),("cupcake",True),("cupcake",1.5)):
        try:
            calculate_total([{"name":name,"quantity":quantity}], {"cupcake":250})
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid order was accepted")
    print("Pricing: exact totals and invalid-order tests passed.")
