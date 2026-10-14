
"""A simple program to create an AI prompt for a business."""

name = input("Your name: ")
business = input("Business type: ")
problem = input("Biggest problem: ")
budget = int(input("Monthly budget in PKR: "))

print(f"\nWelcome, {name}!")
print("--- Your AI Prompt ---")


prompt = f"Suggest 3 AI solutions for a {business} that struggles with {problem}. Budget: {budget} PKR per month."

print(prompt)
