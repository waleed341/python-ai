
"""
Lesson 2.8 - Your First Agent

Sweet Crumbs AI Agent.

The agent can:
1. Read business item prices.
2. Check order status.
3. Place an order only after owner approval.
4. Read business FAQ information.

Uses LangChain tool calling, conversation memory,
a maximum-step limit, and safe error handling.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_ollama import ChatOllama


BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "faq.json"
ORDERS_FILE = BASE_DIR / "agent_orders.json"

MAX_STEPS = 5

# WHY: Python owns the official prices so the AI cannot invent totals.
PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
    "cookie": 200,
    "custom cake": 4500,
}

# Demo orders for testing the status-check tool.
ORDER_STATUS = {
    "A101": "Pending",
    "A102": "In progress",
    "A103": "Completed",
}


def normalize_item(item: str) -> str:
    """Map ordinary bakery plurals to the official menu key."""
    name = item.strip().lower()
    return {"cupcakes":"cupcake", "brownies":"brownie", "cookies":"cookie",
            "chocolate cakes":"chocolate cake", "custom cakes":"custom cake"}.get(name, name)


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Look up the official price of a Sweet Crumbs service.

    Args:
        item: The item name to look up.
    """
    name = normalize_item(item)

    if name not in PRICES:
        return f"'{item}' is not on the bakery menu."

    return f"{name} costs {PRICES[name]:,} PKR"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the status of an existing customer order.

    Args:
        order_id: The order identifier, such as A102.
    """
    order_id = order_id.strip().upper()

    if order_id not in ORDER_STATUS:
        return f"Order {order_id} was not found."

    return f"Order {order_id} status: {ORDER_STATUS[order_id]}"


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Place a new bakery order after asking the owner for approval.

    Args:
        item: The item the customer wants to order.
        quantity: The number of bakery items requested.
        customer: The name of the customer placing the order.
    """
    name = normalize_item(item)
    customer = customer.strip()

    if name not in PRICES:
        return f"Order rejected: '{item}' is not on the menu."

    if quantity <= 0:
        return "Order rejected: quantity must be greater than zero."

    if not customer:
        return "Order rejected: customer name is required."

    total = PRICES[name] * quantity

    # WHY: The AI must never place an order without human approval.
    approval = input(
        f"  [approve] {quantity} x {name} for {customer} "
        f"= {total:,} PKR. Place it? (yes/no) "
    ).strip().lower()

    if approval != "yes":
        return "Order cancelled: owner did not approve."

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as file:
            orders = json.load(file)

        if not isinstance(orders, list):
            orders = []

    except (FileNotFoundError, json.JSONDecodeError):
        orders = []

    order_id = f"A{104 + len(orders)}"

    order = {
        "order_id": order_id,
        "customer": customer,
        "item": name,
        "quantity": quantity,
        "total": total,
        "status": "Pending",
    }

    orders.append(order)

    with open(ORDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(orders, file, indent=2, ensure_ascii=False)

    ORDER_STATUS[order_id] = "Pending"

    return (
        f"Order {order_id} placed: "
        f"{quantity} x {name} for {customer}, "
        f"total {total:,} PKR"
    )


@tool(parse_docstring=True)
def read_faq(question: str) -> str:
    """Read business information from the saved FAQ file.

    Args:
        question: The customer's question about the business.
    """
    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as file:
            facts = json.load(file)

    except FileNotFoundError:
        return "FAQ file not found."

    except json.JSONDecodeError:
        return "FAQ file contains invalid JSON."

    # WHY: Read the existing FAQ instead of inventing business facts.
    return (
        f"Business question: {question}\n"
        f"Official business facts:\n"
        f"{json.dumps(facts, indent=2, ensure_ascii=False)}"
    )


# Register tools so the agent can find them by name.
TOOL_LIST = [
    get_price,
    order_status,
    place_order,
    read_faq,
]

TOOLS = {
    selected_tool.name: selected_tool
    for selected_tool in TOOL_LIST
}


llm = ChatOllama(
    model="llama3.2",
    base_url="http://127.0.0.1:11434",
    temperature=0,
    client_kwargs={"timeout": 60},
)

# WHY: bind_tools lets the AI request actions, but Python executes them.
agent = llm.bind_tools(TOOL_LIST)


SYSTEM_PROMPT = """
You are the Sweet Crumbs AI business assistant.

You can use tools to:
- Look up item prices.
- Check existing order status.
- Place service orders after owner approval.
- Read business facts from FAQ.

Rules:
1. Use get_price for price questions.
2. Use order_status for order tracking.
3. Use place_order when a customer requests a new order.
4. Use read_faq for business hours, products, and policies.
5. Never invent prices or order statuses.
6. Never claim an order was placed unless the tool confirms it.
7. If the owner rejects an order, explain that it was cancelled.
8. Be helpful, concise, and accurate.
"""

history = [
    SystemMessage(content=SYSTEM_PROMPT)
]


def run_agent(question: str) -> str:
    """Run the agent with tool calls and a maximum-step limit."""

    history.append(HumanMessage(content=question))

    for step in range(MAX_STEPS):
        try:
            response = agent.invoke(history)

        except Exception as error:
            return f"Agent error: {error}"

        history.append(response)

        if not response.tool_calls:
            return str(response.content)

        action_result = None
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            selected_tool = TOOLS.get(tool_name)

            if selected_tool is None:
                result = f"Unknown tool: {tool_name}"

            elif tool_name == "place_order" and action_result is not None:
                result = "An order action was already handled this turn."
            else:
                try:
                    result = selected_tool.invoke(tool_args)

                except ValidationError as error:
                    result = f"Invalid tool arguments: {error}"

                except Exception as error:
                    result = f"Tool error: {error}"

            print(
                f"  [tool] {tool_name}({tool_args}) -> {result}"
            )

            # WHY: tool_call_id links the tool result to the AI request.
            history.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id,
                )
            )
            if tool_name == "place_order" and action_result is None:
                action_result = str(result)

        # WHY: Report the exact approval outcome so the model cannot claim a cancelled order was placed.
        if action_result is not None:
            history.append(AIMessage(content=action_result))
            return action_result

    else:
        return (
            "I reached the maximum number of steps. "
            "Please try a simpler request."
        )


print(
    "Sweet Crumbs Agent: ask about prices, orders, "
    "or place an order. Type 'bye' to exit."
)

while True:
    try:
        question = input("You: ").strip()

    except (KeyboardInterrupt, EOFError):
        print("\nAgent: Goodbye!")
        break

    if not question:
        continue

    if question.lower() == "bye":
        print("Agent: Goodbye!")
        break

    answer = run_agent(question)

    print(f"Agent: {answer}")

