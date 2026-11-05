# Sweet Crumbs: Watch the Agent Think

Real local llama3.2 calls; fresh conversational memory for each question.
Owner approval and writes were isolated sample tests, not real bakery orders.

```text
Question: Compare the price of a brownie and a cupcake. Use get_price for both.
Expected tool: get_price
Owner test response: no
  [tool] get_price({'item': 'brownie'}) -> brownie costs 300 PKR
  [tool] get_price({'item': 'cupcake'}) -> cupcake costs 250 PKR
Agent: The brownie costs 300 PKR and the cupcake costs 250 PKR.
Tool selection: PASS

Question: Where is order A102?
Expected tool: order_status
Owner test response: no
  [tool] order_status({'order_id': 'A102'}) -> Order A102 status: In progress
Agent: Order A102 is currently in progress. Would you like to know the status of the order or place a new order?
Tool selection: PASS

Question: My name is Ali. Place an order for 2 cupcakes.
Expected tool: place_order
Owner test response: yes
  [tool] place_order({'customer': 'Ali', 'item': 'cupcakes', 'quantity': '2'}) -> Order A104 placed: 2 x cupcake for Ali, total 500 PKR
Agent: Order A104 placed: 2 x cupcake for Ali, total 500 PKR
Tool selection: PASS

Question: My name is Sara. Place an order for 1 brownie.
Expected tool: place_order
Owner test response: no
  [tool] place_order({'customer': 'Sara', 'item': 'brownie', 'quantity': '1'}) -> Order cancelled: owner did not approve.
Agent: Order cancelled: owner did not approve.
Tool selection: PASS
```

Correct tool selection: 4 of 4 questions.

An earlier test showed two issues: a plural cupcake name was rejected, and the
model claimed a rejected order was placed. Plural normalisation now accepts
common menu plurals. Order actions return the exact Python approval result,
preventing the model from reversing a rejected/saved outcome.
