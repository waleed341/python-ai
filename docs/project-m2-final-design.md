# Module 2 Final Project — AI Business Assistant

**Business:** Sweet Crumbs
**Project:** AI Business Assistant
**Course:** Python for AI — Module 2, Checkpoint 2

## 1. Business Data Design

Business information will be stored in `code/business.json`. The owner can update this file without changing the Python code.

| Key | Example value | Purpose |
|---|---|---|
| name | Sweet Crumbs | Business name |
| type | Bakery | Business category |
| city | Lahore, Pakistan | Business location |
| hours | Daily, 9 AM to 10 PM | Working hours |
| delivery | 200 PKR in Lahore; free from 3,000 PKR | Delivery information |
| support | Available during working hours | Customer support |
| payment_policy | Confirm payment terms with the bakery owner | Payment information |
| currency | PKR | Currency |
| prices | Nested dictionary of products and prices | Official item prices |

### Bakery Prices

| Item | Price (PKR) |
|---|---:|
| Chocolate Cake | 1,500 |
| Cupcake | 250 |
| Brownie | 300 |
| Cookie | 200 |
| Custom Cake | 4,500 |

## 2. Tools Design

The AI will select tools, but Python will execute them.

| Tool | Reads / Checks / Acts | Inputs | Needs owner approval? |
|---|---|---|---|
| `get_price` | Reads official item price | `item` | No |
| `get_info` | Reads business information | `topic` | No |
| `order_status` | Checks saved order status | `order_id` | No |
| `place_order` | Calculates total and saves a new order | `item`, `quantity`, `customer` | **Yes** |

All tools will use `@tool(parse_docstring=True)` with type hints and `Args:` docstrings.

## 3. Guardrails Design

| Risk | Guardrail in my code |
|---|---|
| Agent runs forever | Set `MAX_STEPS = 5` and use a `for ... else` fallback |
| AI invents prices | Read prices from `business.json` and calculate totals in Python |
| Order saved without permission | Ask the owner for approval using `input()` before saving |
| AI selects an unknown tool | Check the tool name against the `TOOLS` dictionary |
| AI sends incorrect arguments | Catch `ValidationError` and return a safe message |
| Missing or damaged JSON files | Handle file errors with `try / except` |
| AI invents WhatsApp customer details | Compare extracted information against the original message |
| WhatsApp item is not on the menu | Print `CHECK:` and exclude it from the calculated total |
| Ollama is offline | Show a friendly message and record the error in `errors.log` |
| Conversation grows too large | Send only the last 8 transcript messages |
| Sensitive order information is uploaded to GitHub | Add `orders.json`, `transcript.json`, and `errors.log` to `.gitignore` |

## 4. Planned Application Commands

| Command | Purpose |
|---|---|
| `/import` | Extract and validate an order from a WhatsApp message |
| `/orders` | Display saved orders in a numbered list |
| `/reset` | Clear conversation memory without deleting orders |
| `bye` | Exit and display the session report |

## 5. Testing Plan

### Agent Tests

| Test | Expected behavior | Tools called | Pass? |
|---|---|---|---|
| Ask the business name | Short answer | | Not tested |
| Ask an item price | Correct price from JSON | get_price | PASS |
| Compare two item prices | Two price lookups | get_price twice | PASS |
| Ask working hours | Read official hours | get_info | PASS |
| Check a saved order | Read status from `orders.json` | order_status | PASS |
| Reject an order | No order saved | place_order, isolated check | PASS |
| Approve an order | Order saved with Python total | place_order | PASS |
| Ask about an unavailable item | No invented price | | Not tested |
| Request a free item against the rules | No unapproved order | | Not tested |

### WhatsApp Import Tests

| Test | Expected behavior | Actual result | Pass? |
|---|---|---|---|
| Normal order with name and address | Correct items and total | 2 brownies, 600 PKR | PASS |
| Roman Urdu order with two products | Correct products and quantities | | Not tested |
| Order containing an unknown item | `CHECK:` warning | | Not tested |
| Order without a customer name | Missing or invented name flagged | | Not tested |
| Message asking only about delivery | Not an order; needs human reply | | Not tested |

### Break the Bot Tests

| Test | Expected behavior | Actual result | Pass? |
|---|---|---|---|
| Ollama offline | Friendly message and error log | | Not tested |
| Invalid model name | Friendly error and log | Simulated ResponseError, logged | PASS |
| Damaged JSON files | Warning without crashing | Temporary malformed orders/transcript recovered | PASS |
| Missing `business.json` | Clear message without traceback | Exited with status 1 and a clear message | PASS |
| Owner changes a price | New price used after restart | Temporary cupcake price reloaded as 999 PKR | PASS |
| Restart after a conversation | Previous conversation remembered | Saved name supplied in the next model request | PASS |

## 6. Development Plan

1. Create the business data JSON file.
2. Build helper functions for reading, saving, logging and calculations.
3. Implement the four LangChain tools.
4. Build the agent loop and conversation memory.
5. Implement WhatsApp order extraction and validation.
6. Add commands, error handling and session reporting.
7. Run all tests and document actual results.
8. Prepare screenshots, README and the final GitHub submission.

## 7. AI Quality Test

AI mistakes and near-misses observed during testing, along with the code changes used to address them, will be recorded separately in `docs/project-m2-final-results.md`.
