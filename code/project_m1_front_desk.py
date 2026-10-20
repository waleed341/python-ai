"""
Sweet Crumbs Bakery - AI Front Desk
Answers customer FAQs, calculates order quotes, prepares AI-ready
prompts, and summarizes the customer session.
"""

# Constants: keep business settings in one place for easy updates.
BOT_NAME = "Sweet Crumbs Desk"
DELIVERY_FEE = 200
FREE_DELIVERY_LIMIT = 3000
CLOUD_PRICE_PER_1K_TOKENS = 0.10

CUPCAKE_PRICE = 250
BROWNIE_PRICE = 300
CHOCOLATE_CAKE_PRICE = 1500

# Counters help the owner understand what customers need.
messages = 0
answered_by_rules = 0
unanswered = 0
quotes = 0
total_quoted_value = 0
total_ai_cost = 0.0
complaints = 0

print("=" * 50)
print(f"  {BOT_NAME}: rules, quotes and AI-ready prompts")
print("=" * 50)
print("Ask anything, type /quote for a price, or bye to exit.")

customer_name = input(f"{BOT_NAME}: What is your name? ").strip().title()

if not customer_name:
    customer_name = "Customer"

while True:
    message = input(f"{customer_name}: ").strip().lower()

    # Ignore empty messages so they do not affect session statistics.
    if not message:
        print(f"{BOT_NAME}: Please type a question.")
        continue

    messages += 1

    # Complaints must come first, even if a message includes other keywords.
    if "refund" in message or "complaint" in message or "late" in message:
        complaints += 1
        answered_by_rules += 1
        print(f"{BOT_NAME}: Sorry about that. A manager will call you within 1 hour.")

    elif message == "bye":
        answered_by_rules += 1
        print(f"{BOT_NAME}: Goodbye, {customer_name}!")
        break

    # Human requests end the session so a real person can take over.
    elif "agent" in message or "human" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: Connecting you to a human...")
        break

    elif message == "/quote":
        item = input(f"{BOT_NAME}: Which item? ").strip().lower()
        quantity_text = input(f"{BOT_NAME}: How many? ").strip()

        # Check text before int() to avoid crashing on invalid quantities.
        if not quantity_text.isdigit() or int(quantity_text) <= 0:
            print(f"{BOT_NAME}: Please enter a positive whole number.")
            continue

        quantity = int(quantity_text)

        if item == "cupcake" or item == "cupcakes":
            unit_price = CUPCAKE_PRICE
        elif item == "brownie" or item == "brownies":
            unit_price = BROWNIE_PRICE
        elif item == "chocolate cake" or item == "chocolate cakes":
            unit_price = CHOCOLATE_CAKE_PRICE
        else:
            print(f"{BOT_NAME}: Sorry, {item} is not on our menu.")
            continue

        subtotal = unit_price * quantity

        if quantity >= 10:
            discount = subtotal * 0.10
        else:
            discount = 0

        discounted_subtotal = subtotal - discount

        # Delivery is based on the amount AFTER discount, not before.
        if discounted_subtotal >= FREE_DELIVERY_LIMIT:
            delivery = 0
        else:
            delivery = DELIVERY_FEE

        total = discounted_subtotal + delivery

        quotes += 1
        total_quoted_value += total
        answered_by_rules += 1

        print(f"{BOT_NAME}: {quantity:,} x {item} = {subtotal:,.2f} PKR")
        print(f"     Discount: -{discount:,.2f} PKR")
        print(f"     Delivery: {delivery:,} PKR")
        print(f"     Total: {total:,.2f} PKR")

    # Exact/starts-with matching prevents 'hi' inside 'which' matching.
    elif (
        message == "hi"
        or message == "hello"
        or message == "hey"
        or message.startswith("hi ")
        or message.startswith("hello ")
        or message.startswith("hey ")
    ):
        answered_by_rules += 1
        print(f"{BOT_NAME}: Welcome to Sweet Crumbs Bakery! How can I help you?")

    elif "hours" in message or "open" in message or "closing" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: We are open from 9 AM to 10 PM every day.")

    elif "location" in message or "where" in message or "shop" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: We are located in Lahore, Pakistan.")

    elif "delivery" in message or "deliver" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: We offer delivery in Lahore.")

    elif "menu" in message or "items" in message or "products" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: Cupcake 250 PKR, brownie 300 PKR, chocolate cake 1,500 PKR.")

    elif "payment" in message or "cash" in message or "card" in message:
        answered_by_rules += 1
        print(f"{BOT_NAME}: We accept cash and bank transfers.")

    else:
        unanswered += 1

        # Limit the prompt size to keep estimated AI usage inexpensive.
        clean_question = message.capitalize()[:150]
        estimated_tokens = round(len(clean_question) / 4)

        if (
            "phone" in message
            or "cnic" in message
            or "address" in message
        ):
            chosen_model = "local model (private)"
            estimated_cost = 0.0
        else:
            chosen_model = "small cloud model (cheap)"
            estimated_cost = (
                estimated_tokens / 1000
            ) * CLOUD_PRICE_PER_1K_TOKENS

        total_ai_cost += estimated_cost

        ai_prompt = f"""You are the assistant of Sweet Crumbs Bakery.
Answer {customer_name} in 2 short lines.
Only use confirmed business information. Do not invent prices or promises.
Question: {clean_question}"""

        print(
            f"{BOT_NAME}: Good question! Routed to: "
            f"{chosen_model} (~{estimated_tokens} tokens)"
        )
        print(f"Estimated AI cost: {estimated_cost:.6f} PKR")
        print(f"Prompt:\n{ai_prompt}")

print("=" * 50)
print("Session report")
print(f"Messages: {messages}")
print(f"Answered by rules: {answered_by_rules}")
print(f"Unanswered: {unanswered}")
print(f"Quotes: {quotes}")
print(f"Quoted value: {total_quoted_value:,.2f} PKR")
print(f"Estimated AI cost: {total_ai_cost:.6f} PKR")
print(f"Complaints: {complaints}")
print("=" * 50)
