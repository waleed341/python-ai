"""Read/check/act tools and two live tools for the Sweet Crumbs agent."""
from uuid import uuid4
from langchain_core.tools import tool
from .api import get_json
from .config import RATES_URL, WEATHER_URL
from .data import read_business, read_orders, save_order
from .pricing import calculate_total, normalize_item

@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Read an official item price.

    Args:
        item: Item name from the business menu.
    """
    try:
        price = read_business()["prices"].get(normalize_item(item))
        return "Service is not on the menu." if price is None else f"{item}: {price:,} PKR"
    except (OSError, ValueError) as error:
        return f"Price data unavailable: {error}"

@tool(parse_docstring=True)
def get_info(topic: str) -> str:
    """Read official business facts such as hours, city and policies.

    Args:
        topic: Business information field, or all for the full business profile.
    """
    try:
        business = read_business()
        key = topic.strip().lower()
        return str(business if key == "all" else business.get(key, "That fact is not available."))
    except (OSError, ValueError) as error:
        return f"Business data unavailable: {error}"

@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check an existing order in the saved Module 3 exercise orders.

    Args:
        order_id: Exact order ID returned when an order was saved.
    """
    try:
        for order in read_orders():
            if str(order.get("id", "")).casefold() == order_id.strip().casefold():
                return f"Order {order['id']}: {order.get('status', 'unknown')}"
        return "Order not found."
    except (OSError, ValueError) as error:
        return f"Order storage unavailable: {error}"

@tool(parse_docstring=True, return_direct=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Validate and price a requested order, then ask the terminal owner before saving.

    Args:
        item: Exact requested bakery item from the official menu.
        quantity: Whole number of requested bakery items, from 1 to 100.
        customer: Customer name supplied by the user.
    """
    try:
        customer, item = customer.strip(), normalize_item(item)
        if not customer:
            return "Order not saved: customer name is required."
        total = calculate_total([{"name":item,"quantity":quantity}], read_business()["prices"])
        read_orders()  # Check damaged storage before requesting approval.
        approval = input(f"  [approve] {quantity} x {item} for {customer} = {total:,} PKR. Save? [yes/no]: ")
        if approval.strip().lower() != "yes":
            return "Order cancelled: owner did not approve."
        order = {"id":uuid4().hex[:12], "customer":customer, "items":[{"name":item,"quantity":quantity}], "total":total,"status":"Pending"}
        # WHY: Approval comes from the terminal, never an AI-controlled argument.
        save_order(order)
        return f"Order {order['id']} saved: {total:,} PKR."
    except (OSError, ValueError, EOFError, KeyboardInterrupt) as error:
        return f"Order not saved: {error}"

@tool(parse_docstring=True)
def exchange_rate(currency: str = "USD") -> str:
    """Get the published PKR exchange rate for a currency.

    Args:
        currency: Three-letter base currency code, such as USD, GBP or AED.
    """
    currency = currency.strip().upper()
    if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
        return "Supply a three-letter currency code, such as USD."
    try:
        data = get_json(f"{RATES_URL}/{currency}")
        rate = data["rates"]["PKR"]
        if type(rate) not in (int, float) or rate <= 0:
            raise ValueError("Invalid rate returned")
        return f"1 {currency} = {rate} PKR. Updated: {data.get('time_last_update_utc', 'unknown')}. Rates by Exchange Rate API."
    except (ValueError, KeyError, TypeError) as error:
        return f"Exchange rate unavailable: {error}"

@tool(parse_docstring=True)
def lahore_weather() -> str:
    """Read current Lahore temperature from Open-Meteo for this non-commercial demo."""
    try:
        data = get_json(WEATHER_URL, {"latitude":31.558,"longitude":74.3507,"current":"temperature_2m"})
        current = data["current"]
        return f"Lahore: {current['temperature_2m']} C at {current['time']}. Weather by Open-Meteo (non-commercial demo)."
    except (ValueError, KeyError, TypeError) as error:
        return f"Weather unavailable: {error}"

BUSINESS_TOOLS = [get_price, get_info, order_status, place_order]
LIVE_TOOLS = [exchange_rate, lahore_weather]
