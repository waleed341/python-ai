"""Lesson 3.2: nested structured extraction and validated quotes, not confirmed orders."""
from sweet_crumbs.config import BASE, make_model
from sweet_crumbs.data import read_business, write_json
from sweet_crumbs.models import Order

MESSAGES = [
    "My name is Ali. I need 1 chocolate cake. Lahore.",
    "Sara wants 2 cupcake and 1 brownie. Gulberg.",
    "Bilal wants 1 pizza and 1 cookie. Model Town.",
    "Hi, do you provide customer support on Sundays?",
    "Salam, mera naam Ahmed hai. Mujhe 2 cupcake chahiye. Johar Town.",
    "Sara wants zero cupcakes; just testing.",
]

def main() -> None:
    """Extract examples into checked objects, flag unsupported facts and save candidates."""
    prices = read_business()["prices"]
    extractor = make_model(0).with_structured_output(Order, method="json_schema")
    saved = []
    for message in MESSAGES:
        print(f"\nMessage: {message}")
        try:
            order = extractor.invoke([
                {"role":"system","content":f"You extract Sweet Crumbs bakery orders. Official product names: {list(prices)}. Use those exact singular names for known products. Extract the customer's stated name and address; a city is an address, never a product. Example: 'My name is Ali. I want 2 cupcakes. Lahore.' means customer='Ali', address='Lahore', items=[{{'name':'cupcake','quantity':2}}]. Preserve genuinely unknown requested products so Python can flag them. Never invent details. Non-order questions must have is_order=false and items=[]."},
                {"role":"user","content":message},
            ])
            if not order.is_order:
                print("Not an order: needs a human reply.")
                continue
            problems = order.problems(prices,message)
            for problem in problems:
                print(f"CHECK: {problem}")
            if problems:
                print("Not saved: correct the flagged details.")
                continue
            row = order.model_dump()
            row["total"] = order.total(prices)
            saved.append(row)
            print(order.model_dump_json(indent=2))
            print(f"Quote: {row['total']:,} PKR (not an approved order)")
        except Exception as error:
            print(f"CHECK: extraction/validation failed: {error}")
    target = BASE / "module3_extracted_orders.json"
    write_json(target,saved)
    print(f"Saved {len(saved)} validated candidates to {target.name}; no confirmed orders placed.")

if __name__ == "__main__":
    main()
