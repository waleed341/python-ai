"""Sweet Crumbs Content Studio: batch descriptions, streamed posts and grounded chat.

Module 2 checkpoint 1 deliberately uses only concepts from lessons 2.1-2.4.
Run: uv run code/project_m2_content_studio.py
"""
import time
from langchain.chat_models import init_chat_model

config = {"model":"ollama:llama3.2", "max_messages":8}
facts = {
    "name":"Sweet Crumbs", "city":"Lahore, Pakistan",
    "hours":"Daily, 9 AM to 10 PM",
    "delivery":"200 PKR in Lahore; free from 3,000 PKR",
    "payment":"Confirm payment terms with the bakery owner",
    "prices":{"chocolate cake":1500,"cupcake":250,
              "brownie":300,"cookie":200,"mango tart":0},
}
tones = {"fun":"friendly and playful", "premium":"calm and professional", "urgent":"energetic, without invented deadlines or discounts"}
# WHY: creative copy benefits from variety; customer answers need consistency.
precise = init_chat_model(config["model"], temperature=0.2)
creative = init_chat_model(config["model"], temperature=0.8)
system = {"role":"system", "content":f"You assist Sweet Crumbs. Business facts: {facts}. For business questions use only these facts; say you do not know if business information is absent. Price 0 means coming soon, NOT available: never advertise it as available. For personal questions, use the user's details from this conversation: remember and directly state their name if they provided it. Never invent prices, claims, offers or deadlines."}
messages = [system]
chat_answers = menu_descriptions = posts = price_answers = total_tokens = 0
total_seconds = 0.0
print("=" * 50)
print("Sweet Crumbs AI Content Studio")
print("/menu | /post fun|premium|urgent | /price <item> | /reset | bye")
while True:
    text = input("You: ").strip()
    command = text.lower()
    if not text:
        continue
    if command == "bye":
        break
    if command == "/reset":
        messages = [system]
        print("Memory reset.")
        continue
    # WHY: exact prices come from Python and need no AI tokens.
    if command == "/price" or command.startswith("/price "):
        item = command[6:].strip()
        price = facts["prices"].get(item)
        if price is None:
            print("Not on our menu.")
        elif price == 0:
            print("Coming soon.")
        else:
            print(f"{item}: {price:,} PKR")
        price_answers += 1
        continue
    if command == "/menu":
        menu = []
        for item, price in facts["prices"].items():
            # WHY: unavailable products must not consume model calls.
            if price == 0:
                print(f"Skipping {item}: coming soon.")
                continue
            started = time.perf_counter()
            response = creative.invoke([system, {"role":"user","content":f"Write one sentence describing {item}."}])
            total_seconds += time.perf_counter() - started
            total_tokens += (response.usage_metadata or {}).get("total_tokens", 0)
            menu.append({"item":item,"price":price,"description":response.text})
            menu_descriptions += 1
        for number, item in enumerate(menu, 1):
            print(f"{number}. {item['item']} ({item['price']:,} PKR)\n   {item['description']}")
        continue
    if command == "/post" or command.startswith("/post "):
        tone = tones.get(command[5:].strip(), tones["premium"])
        print(f"Studio ({tone}):")
        started = time.perf_counter()
        combined = None
        for chunk in creative.stream([system, {"role":"user","content":f"Write a short social post in this tone: {tone}."}]):
            print(chunk.text, end="", flush=True)
            combined = chunk if combined is None else combined + chunk
        print()
        if combined is not None:
            total_tokens += (combined.usage_metadata or {}).get("total_tokens", 0)
        total_seconds += time.perf_counter() - started
        posts += 1
        continue
    messages.append({"role":"user","content":text})
    # WHY: retain system rules and complete recent turns before the new question.
    messages = [system] + messages[1:][-(config["max_messages"] + 1):]
    started = time.perf_counter()
    response = precise.invoke(messages)
    total_seconds += time.perf_counter() - started
    usage = response.usage_metadata or {}
    total_tokens += usage.get("total_tokens", 0)
    messages.append({"role":"assistant","content":response.text})
    messages = [system] + messages[1:][-config["max_messages"]:]
    chat_answers += 1
    print(response.text)
    print(f"Memory: {len(messages)} messages; sent {usage.get('input_tokens', 0)} tokens")
print("Goodbye!\n" + "=" * 50)
print(f"Chat answers: {chat_answers} | Menu descriptions: {menu_descriptions} | Posts: {posts} | Price answers: {price_answers}")
print(f"AI usage: {total_tokens:,} tokens in {total_seconds:.1f} seconds (local Ollama: no API fee)")
