# Sweet Crumbs: Hallucination Hunt

Actual local llama3.2 run using five sample bakery messages. Outputs were saved
only in temporary storage; existing customer records were not used.

```text
Sweet Crumbs - AI Order Extractor

Message: My name is Ali. I need 1 chocolate cake. Lahore.
  1 x chocolate cake = 1,500 PKR
  Customer: Ali, Address: Lahore
  Total: 1,500 PKR

Message: I am Sara. Please book 2 cupcakes and 1 brownie. Gulberg.
  2 x cupcake = 500 PKR
  1 x brownie = 300 PKR
  Customer: Sara, Address: Gulberg
  Total: 800 PKR

Message: My name is Bilal. I need 1 pizza and 1 cookie. Model Town.
  1 x cookie = 200 PKR
  Customer: Bilal, Address: Model Town
  Total: 200 PKR
  CHECK: 'pizza' is not on the menu.

Message: Hi, do you provide customer support on Sundays?
  Not an order: needs a human reply.

Message: Salam, mera naam Ahmed hai. Mujhe 2 cupcake aur 1 chocolate cake chahiye. Johar Town.
  2 x cupcake = 500 PKR
  1 x chocolate cake = 1,500 PKR
  Customer: Ahmed, Address: Johar Town
  Total: 2,000 PKR

==================================================
Orders found: 4 | Total value: 4,500 PKR | Checks: 1
Saved 4 orders to orders.json
Saved item rows to orders.csv


```

Exit code: 0

## Findings

Four order candidates totalled 4,500 PKR, calculated in Python. The pizza request
was flagged and excluded from pricing while the valid cookie remained. The
Sunday support question was correctly classified as a non-order. No invented
customer name was observed in this run; that check remains in the code. Common
bakery plurals are normalised to their official singular menu names. These are
extracted candidates rather than owner-approved orders.
