
"""A simple tool to create AI prompts for small businesses."""

# Get business details to make the prompts more useful.
name = input("Business name: ")
business = input("Business type: ")
city = input("City: ")
customers = input("Main customers: ")
budget = int(input("Monthly budget (PKR): "))

# Show which business these prompts are for.
print("\n====================================")
print(f"AI Prompt Kit for {name}")
print("====================================")

# WHY: A role, audience and clear task make the marketing prompt reproducible.
prompt1 = f"Write a short Instagram post for {name}, a {business} in {city}. The target customers are {customers}. Keep the tone friendly and add a call to action."


prompt2 = f"You are the manager of {name}. Write a polite reply to an unhappy customer whose order was late. Say sorry and offer a small discount."

prompt3 = f"Suggest 3 low-cost AI ideas for a {business} in {city} to attract {customers}. The monthly budget is {budget} PKR."

prompt4 = f"Write a short and friendly WhatsApp auto-reply for {name}, a {business} in {city}. Thank the customer for messaging and tell them we will reply soon."

print("\n[1] Marketing")
print(prompt1)

print("\n------------------------------")
print("[2] Customer Service")
print(prompt2)

print("\n------------------------------")
print("[3] Growth")
print(prompt3)

print("\n------------------------------")
print("[4] WhatsApp Auto-Reply")
print(prompt4)

# Module 2.1 stretch: explicitly opt in to a real AI answer for Prompt 1.
import sys
if "--ai" in sys.argv:
    from langchain.chat_models import init_chat_model
    model = init_chat_model("ollama:llama3.2", temperature=0.2)
    print("\nAI Marketing Answer:")
    print(model.invoke(prompt1).text)
