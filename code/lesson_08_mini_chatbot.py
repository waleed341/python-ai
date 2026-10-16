
"""Lesson 1.8: Rule-based Business Helper Bot for City Mart."""

BOT = "City Mart Bot"

print("=" * 45)
print("WELCOME TO CITY MART")
print("=" * 45)
print(f"{BOT}: Hello! I can help with prices, hours, location, orders, and complaints.")
print(f"{BOT}: Type 'bye' to exit or 'human' to request assistance.")

# WHY: Remember the customer's name throughout the conversation.
name = input(f"{BOT}: What is your name? ").strip().title()

if name == "":
    name = "Friend"

print(f"{BOT}: Nice to meet you, {name}!")

message_count = 0
unanswered_count = 0
complaint_count = 0

# WHY: A loop allows multiple questions without restarting the chatbot.
while True:
    try:
        message = input(f"{name}: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{BOT}: Goodbye, {name}!")
        break

    message_count += 1

    if message in ("bye", "exit"):
        print(f"{BOT}: Goodbye, {name}! Thanks for visiting.")
        break

    elif message == "":
        print(f"{BOT}: Please type a question.")

    # WHY: Requests for human assistance take priority over automatic replies.
    elif "human" in message.split() or "agent" in message.split():
        print(f"{BOT}: Connecting you to a human...")
        break

    # WHY: Complaints must come before orders, because an order may be late.
    elif any(word in message for word in ("refund", "complaint", "late", "damaged")):
        complaint_count += 1
        print(f"{BOT}: Sorry about that, {name}.")
        print(f"{BOT}: Please contact the shop manager for assistance.")

    elif any(word in message for word in ("hour", "open", "time")):
        print(f"{BOT}: Our demo shop is open daily from 9 AM to 10 PM.")

    elif any(word in message for word in ("price", "cost", "how much")):
        print(f"{BOT}: Example prices: Milk 250 PKR, Bread 180 PKR, Eggs 350 PKR.")

    elif any(word in message for word in ("where", "location", "address")):
        print(f"{BOT}: Our demo shop is based in Lahore, Pakistan.")

    elif "order" in message or "delivery" in message:
        print(f"{BOT}: {name}, you can place an order at the shop.")
        print(f"{BOT}: Ask the manager about delivery options.")

    elif message in ("hi", "hello", "hey", "salam") or message.startswith("assalam"):
        print(f"{BOT}: Hello again, {name}! How can I help?")

    else:
        unanswered_count += 1

        # WHY: Unanswered questions can become prompts for an LLM in Module 2.
        ai_prompt = (
            f"You are a helpful customer support assistant for City Mart. "
            f"Answer {name}'s question politely in 2 short sentences. "
            f"Do not invent prices, policies, or contact details. "
            f"Question: {message}"
        )

        print(f"{BOT}: Sorry {name}, I don't have an answer yet.")
        print(f"{BOT}: Future AI prompt:")
        print(ai_prompt)

print("\n" + "=" * 45)
print("CHAT SUMMARY")
print("=" * 45)
print(f"Customer: {name}")
print(f"Total messages: {message_count}")
print(f"Unanswered questions: {unanswered_count}")
print(f"Complaints received: {complaint_count}")
print("=" * 45)
