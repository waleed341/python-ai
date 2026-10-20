# Lesson 2.8 — Watch the Agent Think

## Project
Zentrox Lab AI Business Agent

## Objective
Observe whether the AI agent selects the correct tools, handles customer requests, and asks for owner approval before placing orders.

## Test Results

| Test | User Request | Tool Selected | Result |
|---|---|---|---|
| 1 | Compare website development and AI chatbot prices | `get_price` (twice) | PASS |
| 2 | Check order A102 | `order_status` | PASS |
| 3 | Order 2 AI chatbots with owner approval `yes` | `place_order` | PASS |
| 4 | Order 2 AI chatbots with owner approval `no` | `place_order` | PASS |

**Correct tool selection: 4 out of 4 observed tests (100%).**

## Owner Approval Verification

The approved order was saved successfully:

- Order ID: `A104`
- Service: AI chatbot
- Quantity: 2
- Total: 50,000 PKR
- Status: Pending

The rejected order was not saved. The `agent_orders.json` file contained only the approved order.

## Observed AI Response Problems

1. After placing an approved order, the AI incorrectly said it was still waiting for owner approval.
2. After rejecting an order, the AI said the order was placed and then cancelled, instead of clearly stating that it was not placed.
3. During order tracking, the AI promised to notify the customer when the order was completed, even though automatic notifications were not implemented.
4. During price comparison, the AI provided both correct prices but did not explicitly calculate the 5,000 PKR difference.

## Conclusion

The agent correctly selected tools in all four observed tests. The Python tools enforced owner approval and saved only the approved order.

The final AI-generated responses need improvement to avoid misleading customers.

The FAQ stretch-tool test was not completed.