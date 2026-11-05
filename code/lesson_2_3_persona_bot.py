
"""
Lesson 2.3 - Persona Bot with Real Facts

An AI business assistant with three personalities,
verified prices, and conversation memory.
"""

from langchain.chat_models import init_chat_model


# WHY: Keep model settings together so they are easy to change.
config = {
    "model": "ollama:llama3.2",
    "temperature": 0.2,
    "memory_size": 8
}

# Sample business facts for this assignment.
facts = {
    "name": "Sweet Crumbs",
    "city": "Lahore",
    "business_type": "Bakery",
    "working_hours": "Daily, 9 AM to 10 PM",
    "contact": "Ask the bakery owner during opening hours",
    "products": "Cakes, cupcakes, brownies and cookies",
    "prices": {
        "chocolate cake": 1500,
        "cupcake": 250,
        "brownie": 300
    }
}

personas = {
    "friendly": "warm and cheerful, uses simple words",
    "formal": "professional and polite",
    "sales": "enthusiastic and suggests relevant products"
}

current_persona = "friendly"


def build_system_message(persona_name):
    style = personas.get(persona_name, personas["friendly"])

    return (
        f"You are the assistant for {facts['name']}.\n"
        f"Your speaking style is: {style}.\n"
        f"Business facts: {facts}\n"
        "Only use these facts when answering business questions. "
        "Never invent prices, products, or business details. "
        "If information is missing, politely say you do not know. "
        "Keep answers short."
    )


llm = init_chat_model(
    model=config["model"],
    temperature=config["temperature"]
)

messages = [
    {
        "role": "system",
        "content": build_system_message(current_persona)
    }
]

print("Bot ready. Commands: /persona friendly|formal|sales, /price <item>, /add <item> <price>, bye")

while True:
    question = input("You: ").strip()

    if not question:
        continue

    if question.lower() == "bye":
        print("Bot: Goodbye!")
        break

    if question.lower().startswith("/persona "):
        requested_persona = question.split(maxsplit=1)[1].strip().lower()

        # WHY: .get() prevents errors when a persona does not exist.
        style = personas.get(requested_persona, personas["friendly"])

        current_persona = (
            requested_persona
            if requested_persona in personas
            else "friendly"
        )

        messages[0]["content"] = build_system_message(current_persona)

        print(f"Bot: Style changed to: {style}")
        continue

    if question.lower().startswith("/add "):
        # WHY: Rebuild the system facts so the model sees the owner's new price.
        parts = question[5:].rsplit(maxsplit=1)
        if len(parts) != 2 or not parts[1].isdigit():
            print("Bot: Use /add <item> <nonnegative whole PKR price>.")
            continue
        item, price_text = parts
        facts["prices"][item.strip().lower()] = int(price_text)
        messages[0]["content"] = build_system_message(current_persona)
        print(f"Bot: Added {item.strip().lower()} at {int(price_text):,} PKR.")
        continue

    if question.lower() == "/price" or question.lower().startswith("/price "):
        item = question[6:].strip().lower()

        # WHY: Read exact prices directly instead of asking AI to guess.
        price = facts["prices"].get(item)

        if price is not None:
            print(f"Bot: {item.title()} costs {price} PKR.")
        else:
            print(f"Bot: Sorry, {item} is not on our menu.")

        continue

    messages.append({
        "role": "user",
        "content": question
    })

    response = llm.invoke(messages)

    print("Bot:", response.text)

    messages.append({
        "role": "assistant",
        "content": response.text
    })

    # WHY: Keep recent messages without growing memory forever.
    if len(messages) > config["memory_size"] + 1:
        messages = (
            [messages[0]]
            + messages[1:][-config["memory_size"]:]
        )
