# Sweet Crumbs Content Studio design

| Fact | Value |
|---|---|
| Business | Sweet Crumbs bakery, Lahore |
| Hours | Daily, 9 AM-10 PM |
| Delivery | 200 PKR; free for orders from 3,000 PKR |
| Payment | Confirm with the bakery owner |
| Prices (PKR) | Chocolate cake 1,500; cupcake 250; brownie 300; cookie 200; mango tart 0 (coming soon) |

| Tone | Instruction |
|---|---|
| fun | Friendly and playful |
| premium | Calm and professional |
| urgent | Energetic, without invented deadlines or discounts |

| Job | Model | Reason |
|---|---|---|
| Menu and posts | llama3.2, temperature 0.8 | Varied marketing copy |
| Customer chat | llama3.2, temperature 0.2 | Consistent factual answers |
| Price lookup | Python dictionary | Exact price with no AI call |

The system instruction is preserved along with four recent conversation turns.
Reset clears personal memory. Price-0 products are skipped. Tokens and AI seconds
are accumulated across the session. See project-m2-cp1-results.md for actual runs.
