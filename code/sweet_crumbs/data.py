"""Read official data and keep Module 3 exercises separate from existing orders."""
import json
from pathlib import Path
from .config import BASE

ORDERS_FILE = BASE / "module3_orders.json"

def read_business() -> dict:
    """Read the owner's business file; reject malformed prices."""
    business = json.loads((BASE / "business.json").read_text(encoding="utf-8-sig"))
    if not isinstance(business, dict) or not isinstance(business.get("prices"), dict):
        raise ValueError("business.json must contain a prices dictionary")
    if not business["prices"] or any(type(price) is not int or price < 0 for price in business["prices"].values()):
        raise ValueError("Prices must be nonnegative whole PKR amounts")
    return business

def read_orders() -> list[dict]:
    """Read existing orders; missing storage starts empty, damaged storage is reported."""
    if not ORDERS_FILE.exists():
        return []
    orders = json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    if not isinstance(orders, list) or any(not isinstance(row, dict) for row in orders):
        raise ValueError("Order storage must contain a list of objects")
    return orders

def write_json(path: Path, value: object) -> None:
    """Replace a complete JSON document only after its temporary write succeeds."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)

def save_order(order: dict) -> None:
    """Append a confirmed order without overwriting damaged order storage."""
    write_json(ORDERS_FILE, read_orders() + [order])
