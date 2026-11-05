# Sweet Crumbs Content Studio: actual verification

Inputs:

```text
/price CUPCAKE
/price mango tart
/price pizza
/menu
/post fun
/post premium
/post urgent
/post pirate
What are your opening hours?
What is the price of a cupcake?
Do you sell pizza?
My name is Ali.
What is my name?
/reset
What is my name?
BYE
```

Unedited local Ollama output:

```text
==================================================
Sweet Crumbs AI Content Studio
/menu | /post fun|premium|urgent | /price <item> | /reset | bye
You: cupcake: 250 PKR
You: Coming soon.
You: Not on our menu.
You: Skipping mango tart: coming soon.
1. chocolate cake (1,500 PKR)
   The chocolate cake is priced at 1500 PKR.
2. cupcake (250 PKR)
   A cupcake is priced at 250 PKR at Sweet Crumbs.
3. brownie (300 PKR)
   The brownie costs 300 PKR.
4. cookie (200 PKR)
   The cookie at Sweet Crumbs costs 200 PKR.
You: Studio (friendly and playful):
"Hey Lahore! It's your favorite bakery, Sweet Crumbs, here! What's sweetening your day? Treat yourself to our scrumptious cakes, cupcakes, and more! Visit us daily from 9 AM to 10 PM and indulge in a little sweetness. See you soon!"
You: Studio (calm and professional):
"Indulge in the sweetness of Lahore with Sweet Crumbs! Visit us daily from 9 AM to 10 PM and discover our delicious treats, including our upcoming chocolate cake. Prices vary, please confirm with the bakery owner for details. #SweetCrumbs #Lahore #BakeryLife"
You: Studio (energetic, without invented deadlines or discounts):
"Sweet treats alert! Come and indulge in our scrumptious desserts at Sweet Crumbs in Lahore! From rich chocolate cakes to decadent brownies, our treats are sure to satisfy your cravings! Visit us today and treat yourself to a delightful experience! #SweetCrumbs #Lahore #Desserts #TreatYourself"
You: Studio (calm and professional):
"Welcome to Sweet Crumbs, your go-to destination for delicious treats in Lahore! We're open daily from 9 AM to 10 PM, and you can enjoy our mouth-watering cakes, cupcakes, brownies, cookies, and more. Delivery options are available for 200 PKR from Lahore and free above 3,000 PKR. Please confirm payment terms with our bakery owner. We look forward to serving you!"
You: Our opening hours are Daily, 9 AM to 10 PM.
Memory: 3 messages; sent 213 tokens
You: The price of a cupcake is 250 PKR.
Memory: 5 messages; sent 246 tokens
You: I don't know if you sell pizza.
Memory: 7 messages; sent 273 tokens
You: Hello Ali!
Memory: 9 messages; sent 297 tokens
You: Your name is Ali.
Memory: 9 messages; sent 315 tokens
You: Memory reset.
You: I don't know your name. You haven't told me what it is.
Memory: 3 messages; sent 212 tokens
You: Goodbye!
==================================================
Chat answers: 6 | Menu descriptions: 4 | Posts: 4 | Price answers: 3
AI usage: 3,695 tokens in 123.6 seconds (local Ollama: no API fee)


```

Exit code: 0

## Quality review

| Check | Result |
|---|---|
| Cupcake price, exact dictionary lookup | 250 PKR; no AI call |
| Mango tart | Coming soon; skipped before the menu AI calls |
| Unknown item | Not on our menu |
| Hours and AI price answer | Daily 9 AM-10 PM; cupcake 250 PKR |
| Unknown pizza question | Admitted missing knowledge |
| Name before / after reset | Ali / no name known |
| All tones and invalid tone | All streamed; invalid tone used the premium default |
| Session totals | 6 chats, 4 descriptions, 4 posts, 3 price lookups |

The fun tone was the clearest promotional draft in this run. The premium draft
incorrectly called the available chocolate cake "upcoming" and claimed prices
vary. Those statements are unsupported: the provided sample price is 1,500 PKR.
The urgent draft added descriptive adjectives not established by the facts.
These drafts need owner review; AI marketing text is not treated as an official
price list. Exact `/price` results come from Python. The image is a rendering of
recorded stdout and the exact test inputs, not a photograph of a terminal.
