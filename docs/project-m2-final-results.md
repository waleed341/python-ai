# Sweet Crumbs AI Business Assistant: actual verification

Automated local llama3.2 session using temporary order/history storage.
Owner approvals in this demo were simulated yes answers for sample orders only.
The following output and echoed test inputs are unedited.

```text
Warning: orders.json not found; starting fresh.
Warning: transcript.json not found; starting fresh.
============================================================
  Sweet Crumbs AI Business Assistant
============================================================
Ask anything, or use: /import, /orders, /reset, bye
You: What are your hours?
  [tool] get_info({'topic': 'hours'}) -> hours: Daily, 9 AM to 10 PM
Assistant: Sweet Crumbs is open daily from 9 AM to 10 PM.
You: Compare the price of a brownie and a cupcake.
  [tool] get_price({'item': 'brownie'}) -> brownie costs 300 PKR
  [tool] get_price({'item': 'cupcake'}) -> cupcake costs 250 PKR
Assistant: The brownie costs 300 PKR and the cupcake costs 250 PKR.
You: My name is Ali. Please place an order for 2 cupcakes.
  [approve] 2 x cupcake for Ali = 500 PKR. Save order? (yes/no) yes
  [tool] place_order({'item': 'cupcake', 'quantity': '2', 'customer': 'Ali'}) -> Order A101 placed for Ali: 2 x cupcake; total 500 PKR.
Assistant: Order A101 placed for Ali: 2 x cupcake; total 500 PKR.
You: Where is order A101?
  [tool] order_status({'order_id': 'A101'}) -> Order A101 for Ali is received, total 500 PKR
Assistant: Order A101 for Ali is received, total 500 PKR.
You: /import
Paste the WhatsApp message: My name is Sara. I want 2 brownies. Model Town.
  2 x brownie = 600 PKR
  Customer: Sara, Address: Model Town
  Total: 600 PKR
  [approve] 2 x brownie for Sara = 600 PKR. Save order? (yes/no) yes
  Order A102 placed for Sara: 2 x brownie; total 600 PKR.
You: /orders
  1. A101 | Ali | 500 PKR | received
  2. A102 | Sara | 600 PKR | received
You: bye
Assistant: Goodbye! Everything is saved.
============================================================
Session report
Questions: 4 | Answered: 4 | Errors: 0
WhatsApp imports: 1 | Orders placed: 2 | Orders on file: 2
Tool calls:
  get_price: 2
  get_info: 1
  order_status: 1
  place_order: 1
============================================================

```

See the final report for actual counts. The demo does not place real bakery orders.

## Additional checks

The temporary-data checks also passed owner rejection without a write, malformed
orders/history recovery, missing business-file exit, invalid-model logging,
strict positive item quantities, reloading an edited cupcake price, and supplying
a saved customer name to the model after restarting. Unknown tools and wrong tool
arguments were checked in the manual agent; its MAX_STEPS fallback was verified.
The create_agent version returned a rejected order's exact cancellation message
without sending it back to a model that might rewrite the outcome.

Demo orders are samples only. Existing local software-demo records were backed up
before switching the live business facts to the bakery; no real customer orders
were changed by these temporary tests. Marketing copy remains subject to owner
review, as documented in the Content Studio results.
