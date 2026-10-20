# Module 1 Checkpoint 2 — AI Front Desk Design

## Business: Sweet Crumbs Bakery

Sweet Crumbs is a local bakery in Lahore, Pakistan.

The AI Front Desk will answer common customer questions, calculate order prices, and prepare AI prompts for questions it cannot answer.

## 1. FAQ Intents

| Intent | Keywords | Reply |
|---|---|---|
| Complaint | refund, complaint, late | Sorry about that. A manager will call you within 1 hour. |
| Greeting | hi, hello, hey | Welcome to Sweet Crumbs Bakery! How can I help you? |
| Opening hours | hours, open, closing | We are open from 9 AM to 10 PM every day. |
| Location | location, where, shop | We are located in Lahore, Pakistan. |
| Delivery | delivery, deliver | Yes, we offer delivery in Lahore. |
| Menu | menu, items, products | We sell cupcakes, brownies, and chocolate cakes. |
| Payment | payment, cash, card | We accept cash and bank transfers. |
| Human support | agent, human | Connecting you to a human... |

## 2. Business Rules

| Rule | Value |
|---|---|
| Business name | Sweet Crumbs Bakery |
| Location | Lahore, Pakistan |
| Opening hours | 9 AM to 10 PM, every day |
| Cupcake price | 250 PKR |
| Brownie price | 300 PKR |
| Chocolate cake price | 1,500 PKR |
| Bulk discount | 10% off for 10 or more items |
| Delivery fee | 200 PKR |
| Free delivery | Orders with discounted subtotal of 3,000 PKR or more |
| Private keywords | phone, cnic, my address |
| Complaint keywords | refund, complaint, late |
| Human handover keywords | agent, human |
| Local AI model | Local model, estimated cost 0 PKR |
| Cloud AI model | Small cloud model, estimated token cost |

## 3. Rule Tests

| # | You type | Expected result | Pass? |
|---|---|---|---|
| 1 | `  WHAT are your hours  ` | Opening hours displayed | PASS |
| 2 | `which cake is best?` | AI fallback, not greeting | PASS |
| 3 | `my order is late` | Manager complaint response | PASS |
| 4 | `/quote` → chocolate cake → 1 | Delivery fee of 200 PKR charged | PASS |
| 5 | `/quote` → chocolate cake → 3 | Free delivery above 3,000 PKR | PASS |
| 6 | `/quote` → cupcake → 12 | 10% discount; total 2,900 PKR | PASS |
| 7 | `/quote` → pizza → 2 | Not on our menu; no crash | PASS |
| 8 | `Can I update my phone number?` | Local AI model; 0 PKR cost | PASS |
| 9 | Press Enter without typing | Ask for input again | PASS |
| 10 | `BYE` | Goodbye message and session report | PASS |

## 4. Bonus Tests

| # | You type | Expected result | Pass? |
|---|---|---|---|
| 11 | `/quote` → cupcake → abc | Invalid quantity handled without crashing | PASS |
| 12 | `I want to speak to a human` | Human handover and session report | PASS |
| 13 | `I have a complaint` | Manager response; complaint counter increases | PASS |