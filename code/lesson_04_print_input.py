
"""A simple program to create an AI prompt for a business."""

# WHY: Business-specific details make the generated prompt useful to its owner.
name = input("Your name: ")
business = input("Business type: ")
problem = input("Biggest problem: ")
# WHY: Convert the budget to a number before putting it into the spending limit.
budget = int(input("Monthly budget in PKR: "))

print(f"\nWelcome, {name}!")
print("--- Your AI Prompt ---")


prompt = f"Suggest 3 AI solutions for a {business} that struggles with {problem}. Budget: {budget} PKR per month."

print(prompt)
