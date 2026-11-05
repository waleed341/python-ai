
"""
Lesson 2.7 - AI Order Extractor

Extract structured orders from English and Roman Urdu messages.
Validate products and customer names, calculate prices in Python,
and save accepted orders to orders.json.
"""

import json
import csv
import re
from pathlib import Path

from langchain_ollama import ChatOllama


# WHY: Prices come from our business menu, not from AI guesses.
PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
    "cookie": 200,
    "custom cake": 4500,
}

BASE_DIR = Path(__file__).resolve().parent
ORDERS_FILE = BASE_DIR / "orders.json"


# Five different customer messages required by the task.
MESSAGES = [
    # 1. Normal order
    "My name is Ali. I need 1 chocolate cake. Lahore.",

    # 2. Multiple products
    "I am Sara. Please book 2 cupcakes and 1 brownie. Gulberg.",

    # 3. Mixed valid and off-menu items
    "My name is Bilal. I need 1 pizza and 1 cookie. Model Town.",

    # 4. Not an order
    "Hi, do you provide customer support on Sundays?",

    # 5. Roman Urdu
    "Salam, mera naam Ahmed hai. Mujhe 2 cupcake aur "
    "1 chocolate cake chahiye. Johar Town.",
]


# WHY: JSON schema requests a predictable structure from the AI.
ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "is_order": {"type": "boolean"},
        "customer": {"type": "string"},
        "address": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["name", "quantity"],
            },
        },
    },
    "required": ["is_order", "customer", "address", "items"],
}


llm = ChatOllama(
    model="llama3.2",
    base_url="http://127.0.0.1:11434",
    temperature=0,
    format=ORDER_SCHEMA,
)


def extract_order(message: str) -> dict | None:
    """Extract a customer order as structured JSON."""

    prompt = f"""
You are an accurate customer order extraction assistant.

Business: Sweet Crumbs

Official bakery menu:
{json.dumps(list(PRICES.keys()), indent=2)}

Read the customer message and return JSON matching the schema.

IMPORTANT RULES:

1. Set is_order to true when the customer requests any product or service.

2. A message containing both menu and off-menu items is still an order.

3. Extract ALL requested items, including off-menu items such as pizza.

4. Never reject an entire order just because one item is not on the menu.

5. Set is_order to false only when the message contains no purchase request.

6. Normalize known products to their exact official menu names.

7. Keep unknown item names unchanged.

8. Extract the correct quantity for each requested item.

9. Do not invent customer names, addresses, products, or quantities.

10. Use an empty string if customer name or address is missing.

11. For non-order questions, return:
    is_order = false
    items = []

12. Understand both English and Roman Urdu.

Example of a mixed order:

Customer:
"My name is Bilal. I need 1 pizza and 1 cookie. Model Town."

Correct JSON:
{{
    "is_order": true,
    "customer": "Bilal",
    "address": "Model Town",
    "items": [
        {{"name": "pizza", "quantity": 1}},
        {{"name": "cookie", "quantity": 1}}
    ]
}}

Return JSON only.

Customer message:
{message}
"""

    response = llm.invoke(prompt)

    try:
        # WHY: AI output must be parsed and checked before using it.
        data = json.loads(response.content)

        if not isinstance(data, dict):
            print("  CHECK: AI returned an unexpected JSON structure.")
            return None

        return data

    except (json.JSONDecodeError, TypeError):
        print("  CHECK: AI returned invalid JSON.")
        return None


def name_in_message(name: str, message: str) -> bool:
    """Verify that the extracted customer name exists in the message."""

    if not name:
        return False

    # WHY: Word boundaries prevent partial name matches.
    pattern = rf"(?<!\w){re.escape(name)}(?!\w)"

    return re.search(pattern, message, re.IGNORECASE) is not None


def validate_order(
    data: dict,
    message: str,
) -> tuple[dict | None, list[str]]:
    """Validate extracted items and calculate totals in Python."""

    checks = []

    if not data.get("is_order", False):
        return None, checks

    customer = data.get("customer", "")
    address = data.get("address", "")
    raw_items = data.get("items", [])

    if not isinstance(customer, str):
        customer = ""

    if not isinstance(address, str):
        address = ""

    if not name_in_message(customer, message):
        checks.append(
            f"CHECK: Customer name '{customer}' "
            "was not found in the message."
        )
        customer = "Unverified"

    if not isinstance(raw_items, list):
        checks.append("CHECK: Items must be a list.")
        raw_items = []

    valid_items = []
    total = 0

    for item in raw_items:
        if not isinstance(item, dict):
            checks.append("CHECK: Invalid item structure.")
            continue

        name = item.get("name", "")
        quantity = item.get("quantity", 0)

        if not isinstance(name, str):
            checks.append("CHECK: Invalid item name.")
            continue

        name = name.strip().lower()
        aliases = {"cupcakes":"cupcake", "brownies":"brownie", "cookies":"cookie",
                   "chocolate cakes":"chocolate cake", "custom cakes":"custom cake"}
        name = aliases.get(name, name)

        if name not in PRICES:
            checks.append(f"CHECK: '{name}' is not on the menu.")
            continue

        # WHY: A quantity must be a positive integer, not a guess.
        if type(quantity) is not int or quantity <= 0:
            checks.append(
                f"CHECK: Invalid quantity for '{name}'."
            )
            continue

        # WHY: Python calculates money using trusted menu prices.
        line_total = PRICES[name] * quantity
        total += line_total

        valid_items.append({
            "name": name,
            "quantity": quantity,
            "unit_price": PRICES[name],
            "line_total": line_total,
        })

    if not valid_items:
        checks.append("CHECK: No valid menu items found.")
        return None, checks

    order = {
        "customer": customer,
        "address": address,
        "items": valid_items,
        "total": total,
        "original_message": message,
    }

    return order, checks


def main() -> None:
    """Process all customer messages and save validated orders."""

    orders = []
    all_checks = []
    total_value = 0

    print("Sweet Crumbs - AI Order Extractor\n")

    for message in MESSAGES:
        print(f"Message: {message}")

        try:
            data = extract_order(message)

        except Exception as error:
            warning = f"CHECK: AI extraction failed: {error}"
            print(f"  {warning}")
            all_checks.append(warning)
            print()
            continue

        if data is None:
            all_checks.append("CHECK: Invalid AI JSON or structure.")
            print()
            continue

        order, checks = validate_order(data, message)
        all_checks.extend(checks)

        if order is None:
            if not data.get("is_order", False):
                print("  Not an order: needs a human reply.")

            for warning in checks:
                print(f"  {warning}")

            print()
            continue

        for item in order["items"]:
            print(
                f"  {item['quantity']} x {item['name']} "
                f"= {item['line_total']:,} PKR"
            )

        print(
            f"  Customer: {order['customer']}, "
            f"Address: {order['address']}"
        )
        print(f"  Total: {order['total']:,} PKR")

        for warning in checks:
            print(f"  {warning}")

        orders.append(order)
        total_value += order["total"]

        print()

    # WHY: Save validated orders, never unverified AI output.
    with open(ORDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            orders,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 50)
    print(
        f"Orders found: {len(orders)} | "
        f"Total value: {total_value:,} PKR | "
        f"Checks: {len(all_checks)}"
    )
    print(f"Saved {len(orders)} orders to orders.json")

    # WHY: CSV export lets the owner inspect line totals in a spreadsheet.
    with (BASE_DIR / "orders.csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["customer", "item", "quantity", "line_total"])
        for order in orders:
            for item in order["items"]:
                writer.writerow([order["customer"], item["name"], item["quantity"], item["line_total"]])
    print("Saved item rows to orders.csv")


if __name__ == "__main__":
    main()
