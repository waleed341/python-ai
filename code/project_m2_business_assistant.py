"""Module 2 final: Zentrox Lab AI Business Assistant with safe tool calling."""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from ollama import ResponseError
from pydantic import BaseModel, Field, ValidationError

BASE_DIR = Path(__file__).resolve().parent
BUSINESS_FILE = BASE_DIR / "business.json"
ORDERS_FILE = BASE_DIR / "orders.json"
TRANSCRIPT_FILE = BASE_DIR / "transcript.json"
ERROR_FILE = BASE_DIR / "errors.log"
MODEL_NAME = "llama3.2"
MAX_STEPS = 5
MEMORY_LIMIT = 8


def load_json(path: Path, default: Any) -> Any:
    """Read JSON safely, returning a default if it is missing or damaged."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Warning: {path.name} not found; starting fresh.")
    except (json.JSONDecodeError, UnicodeError, OSError) as error:
        print(f"Warning: {path.name} cannot be read; starting fresh.")
        log_error(f"Reading {path.name}: {error}")
    return default


def save_json(path: Path, value: Any) -> bool:
    """Write formatted Unicode JSON and report whether saving succeeded."""
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(value, file, indent=2, ensure_ascii=False)
        return True
    except (OSError, TypeError, ValueError) as error:
        log_error(f"Saving {path.name}: {error}")
        print(f"Could not save {path.name}. Please contact the owner.")
        return False


def log_error(message: str) -> bool:
    """Append an internal error to the local error log."""
    try:
        with ERROR_FILE.open("a", encoding="utf-8") as file:
            file.write(message + "\n")
        return True
    except OSError:
        return False


def calculate_total(items: list[dict[str, Any]], prices: dict[str, int]) -> int:
    """Calculate a validated order total in Python, not with an LLM."""
    total = 0
    for entry in items:
        name = str(entry["item"]).strip().lower()
        quantity = entry["quantity"]
        if name not in prices or type(quantity) is not int or quantity <= 0:
            raise ValueError(f"Invalid order item: {entry}")
        total += prices[name] * quantity
    return total


def next_order_id(orders: list[dict[str, Any]]) -> str:
    """Return an unused sequential order ID from the saved order list."""
    existing = {str(order.get("id", "")) for order in orders}
    number = 101
    while f"A{number}" in existing:
        number += 1
    return f"A{number}"


def request_approval(description: str) -> bool:
    """Ask the owner explicitly before any order is saved."""
    try:
        return input(f"  [approve] {description} (yes/no) ").strip().lower() == "yes"
    except (EOFError, KeyboardInterrupt):
        print("\n  Approval not received.")
        return False


# WHY: Verify money calculations without involving AI.
assert calculate_total([{"item": "sample", "quantity": 2}], {"sample": 10}) == 20

if not BUSINESS_FILE.is_file():
    print(f"Missing {BUSINESS_FILE.name}. Create code/business.json before running.")
    raise SystemExit(1)

business = load_json(BUSINESS_FILE, None)
if not isinstance(business, dict) or not isinstance(business.get("prices"), dict):
    print("business.json is invalid. Please repair it before running.")
    raise SystemExit(1)

try:
    PRICES = {str(k).strip().lower(): int(v) for k, v in business["prices"].items()}
    if not PRICES or any(price < 0 for price in PRICES.values()):
        raise ValueError("Prices must be nonnegative and nonempty")
except (TypeError, ValueError):
    print("business.json has invalid prices. Please correct them.")
    raise SystemExit(1)

orders = load_json(ORDERS_FILE, [])
if not isinstance(orders, list) or any(not isinstance(item, dict) for item in orders):
    print("Warning: orders.json has an unexpected structure; starting with an empty list.")
    orders = []
transcript = load_json(TRANSCRIPT_FILE, [])
if not isinstance(transcript, list) or any(
    not isinstance(entry, dict) or entry.get("role") not in ("user", "assistant")
    or not isinstance(entry.get("content"), str) for entry in transcript
):
    print("Warning: transcript.json has an unexpected structure; starting fresh.")
    transcript = []

stats = {"questions": 0, "answered": 0, "errors": 0, "imports": 0, "placed": 0}
tool_counts: Counter[str] = Counter()


def create_order(customer: str, items: list[dict[str, Any]], address: str = "") -> str:
    """Validate, request owner approval, and persist one order."""
    customer = customer.strip()
    if not customer:
        return "Order not saved: customer name is required."
    try:
        total = calculate_total(items, PRICES)
    except (ValueError, KeyError, TypeError) as error:
        return f"Order not saved: {error}"
    if not items:
        return "Order not saved: no valid items."
    details = ", ".join(f"{entry['quantity']} x {entry['item']}" for entry in items)
    if not request_approval(f"{details} for {customer} = {total:,} PKR. Save order?"):
        return "Order not saved: owner did not approve."
    order_id = next_order_id(orders)
    order = {"id": order_id, "customer": customer, "items": items,
             "total": total, "status": "received", "address": address}
    # WHY: Update the in-memory list only after the disk write succeeds.
    if not save_json(ORDERS_FILE, orders + [order]):
        stats["errors"] += 1
        return "Order not saved: storage error."
    orders.append(order)
    stats["placed"] += 1
    return f"Order {order_id} placed for {customer}: {details}; total {total:,} PKR."


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Look up a service price from the owner's business data.

    Args:
        item: Exact service name to look up.
    """
    name = item.strip().lower()
    if name not in PRICES:
        return f"'{item}' is not on the menu. Available: {', '.join(PRICES)}"
    return f"{name} costs {PRICES[name]:,} PKR"


@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Read official business details such as name, hours, delivery, or support.

    Args:
        topic: The business information field requested by the customer.
    """
    key = topic.strip().lower().replace(" ", "_")
    aliases = {"working_hours": "hours", "opening_hours": "hours", "location": "city"}
    key = aliases.get(key, key)
    if key == "prices":
        return "For prices, use get_price with the requested service."
    if key not in business:
        return f"Information about '{topic}' is not available in the business file."
    return f"{key}: {business[key]}"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Look up an existing order status from saved orders.

    Args:
        order_id: Saved order ID, for example A101.
    """
    for order in orders:
        if str(order.get("id", "")).upper() == order_id.strip().upper():
            return (f"Order {order['id']} for {order.get('customer', 'unknown')} "
                    f"is {order.get('status', 'unknown')}, total {order.get('total', 0):,} PKR")
    return f"Order {order_id} was not found."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Place an order for one service, only after owner approval.

    Args:
        item: Exact service name from the price menu.
        quantity: Positive number of service units.
        customer: Customer name for the new order.
    """
    return create_order(customer, [{"item": item.strip().lower(), "quantity": quantity}])


TOOL_LIST = [get_price, get_info, order_status, place_order]
TOOLS = {selected.name: selected for selected in TOOL_LIST}
llm = ChatOllama(model=MODEL_NAME, base_url="http://127.0.0.1:11434", temperature=0)
agent = llm.bind_tools(TOOL_LIST)
SYSTEM_PROMPT = ("You are the Zentrox Lab business assistant. Use get_price for prices, "
                 "get_info for business details, order_status for existing orders, and "
                 "place_order for new orders. Never invent prices, hours, status, or promise "
                 "notifications. Never say an order was saved unless the tool confirms it. "
                 "If approval was refused, clearly say the order was NOT placed. "
                 "Do not promise future owner approval when approval already happened. "
                 "If a tool result says an order was not saved, report that honestly.")


class ExtractedItem(BaseModel):
    item: str = Field(description="Service requested, preserving the original item name")
    quantity: int = Field(description="Quantity explicitly requested; use 1 if unspecified")


class ExtractedOrder(BaseModel):
    is_order: bool = Field(description="True only if the message requests an order")
    customer: str = Field(description="Customer name stated in message, or empty string")
    address: str = Field(description="Address stated in message, or empty string")
    items: list[ExtractedItem] = Field(description="Requested services and quantities")


extractor = ChatOllama(model=MODEL_NAME, base_url="http://127.0.0.1:11434", temperature=0)


def friendly_error(error: Exception) -> str:
    """Log internal failures and return a customer-safe error message."""
    stats["errors"] += 1
    log_error(f"{type(error).__name__}: {error}")
    if isinstance(error, httpx.ConnectError):
        return "AI service is offline. Please start Ollama and try again."
    return "Something went wrong. Please try again or contact the owner."


def remember(role: str, content: str) -> None:
    """Save a plain-dictionary transcript after each conversation message."""
    transcript.append({"role": role, "content": content})
    if not save_json(TRANSCRIPT_FILE, transcript):
        stats["errors"] += 1


def run_agent(question: str) -> str:
    """Execute the bounded agent loop with tool validation and message memory."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    # WHY: Send only recent plain-dictionary memory to keep context bounded.
    for entry in transcript[-MEMORY_LIMIT:]:
        cls = HumanMessage if entry["role"] == "user" else AIMessage
        messages.append(cls(content=entry["content"]))
    messages.append(HumanMessage(content=question))
    for _ in range(MAX_STEPS):
        try:
            response = agent.invoke(messages)
        except (httpx.ConnectError, ResponseError) as error:
            return friendly_error(error)
        except Exception as error:
            return friendly_error(error)
        messages.append(response)
        if not response.tool_calls:
            return str(response.content)
        for call in response.tool_calls:
            name, arguments = call["name"], call["args"]
            selected = TOOLS.get(name)
            tool_counts[name] += 1
            if selected is None:
                result = f"Unknown tool: {name}"
            else:
                try:
                    result = selected.invoke(arguments)
                except ValidationError as error:
                    result = f"Invalid tool arguments: {error}"
                except Exception as error:
                    result = friendly_error(error)
            print(f"  [tool] {name}({arguments}) -> {result}")
            # WHY: The matching tool_call_id allows the model to read the right result.
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    else:
        return "I reached the maximum number of steps. Please try a simpler request."


def import_whatsapp() -> None:
    """Extract, check and optionally save a pasted WhatsApp order."""
    stats["imports"] += 1
    try:
        message = input("Paste the WhatsApp message: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nImport cancelled.")
        return
    if not message:
        print("Please paste a message next time.")
        return
    try:
        response = extractor.invoke(
            [SystemMessage(content="Extract only facts stated in the customer's message. "
                                   "Do not invent a customer name, address, item or quantity. "
                                   "Use empty strings for missing name/address. "
                                   "If the message is a question rather than an order, is_order=false."),
             HumanMessage(content=message)],
            format=ExtractedOrder.model_json_schema(),
        )
        raw = json.loads(str(response.content))
        if not isinstance(raw, dict):
            raise ValueError("Extractor did not return a JSON object")
    except (httpx.ConnectError, ResponseError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"  {friendly_error(error)}")
        return
    except Exception as error:
        print(f"  {friendly_error(error)}")
        return
    if not raw.get("is_order", False):
        print("Not an order: needs a human reply.")
        return
    customer = str(raw.get("customer") or "").strip()
    address = str(raw.get("address") or "").strip()
    checks: list[str] = []
    if not customer:
        checks.append("customer name is missing")
    elif not re.search(r"(?<!\w)" + re.escape(customer) + r"(?!\w)", message, re.IGNORECASE):
        checks.append(f"customer '{customer}' is not in the message (invented?)")
    if address and address.lower() not in message.lower():
        checks.append(f"address '{address}' is not in the message (invented?)")
    valid_items: list[dict[str, Any]] = []
    entries = raw.get("items", [])
    if not isinstance(entries, list):
        entries = []
        checks.append("items are not a list")
    for entry in entries:
        if not isinstance(entry, dict):
            checks.append("invalid item structure")
            continue
        name = str(entry.get("item") or "").strip().lower()
        quantity = entry.get("quantity")
        if name not in PRICES:
            checks.append(f"'{name}' is not on the menu")
            continue
        if type(quantity) is not int or quantity <= 0:
            checks.append(f"invalid quantity for '{name}'")
            continue
        valid_items.append({"item": name, "quantity": quantity})
        print(f"  {quantity} x {name} = {quantity * PRICES[name]:,} PKR")
    total = calculate_total(valid_items, PRICES)
    print(f"  Customer: {customer or '(missing)'}, Address: {address or '(missing)'}")
    print(f"  Total: {total:,} PKR")
    if not valid_items:
        checks.append("no valid menu items found")
    for check in checks:
        print(f"  CHECK: {check}")
    # WHY: Suspicious imports require correction rather than silently saving partial orders.
    if checks:
        print("  Not saved: resolve CHECK warnings before importing this order.")
        return
    print("  " + create_order(customer, valid_items, address))


def show_orders() -> None:
    """Display saved orders as a numbered list."""
    if not orders:
        print("  No orders on file.")
        return
    for number, order in enumerate(orders, start=1):
        print(f"  {number}. {order.get('id')} | {order.get('customer')} | "
              f"{order.get('total', 0):,} PKR | {order.get('status')}")


print("=" * 60)
print(f"  {business.get('name', 'Business')} AI Business Assistant")
print("=" * 60)
print("Ask anything, or use: /import, /orders, /reset, bye")
try:
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistant: Goodbye! Everything is saved.")
            break
        if not question:
            print("Please type a question or command.")
            continue
        if question.lower() == "bye":
            print("Assistant: Goodbye! Everything is saved.")
            break
        if question == "/orders":
            show_orders()
            continue
        if question == "/reset":
            transcript.clear()
            if not save_json(TRANSCRIPT_FILE, transcript):
                stats["errors"] += 1
            print("Chat memory cleared. Orders are unchanged.")
            continue
        if question == "/import":
            import_whatsapp()
            continue
        stats["questions"] += 1
        answer = run_agent(question)
        print(f"Assistant: {answer}")
        if not (answer.startswith("Something went wrong") or answer.startswith("AI service is offline")):
            stats["answered"] += 1
        remember("user", question)
        remember("assistant", answer)
finally:
    print("=" * 60)
    print("Session report")
    print(f"Questions: {stats['questions']} | Answered: {stats['answered']} | Errors: {stats['errors']}")
    print(f"WhatsApp imports: {stats['imports']} | Orders placed: {stats['placed']} | Orders on file: {len(orders)}")
    print("Tool calls:")
    for name in TOOLS:
        print(f"  {name}: {tool_counts[name]}")
    print("=" * 60)
