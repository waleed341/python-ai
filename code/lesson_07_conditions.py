
"""Lesson 1.7: Smart Model Router using operators and decisions."""

task = input("Task (code / private / chat): ").strip().lower()
tokens = int(input("Estimated tokens: "))
paid_user = input("Is this a paid user? (yes/no): ").strip().lower()

# Validate token counts because negative requests do not make sense.
if tokens < 0:
    print("Error: Tokens cannot be negative.")

elif task not in ("code", "private", "chat"):
    print("Error: Choose code, private, or chat.")

elif paid_user not in ("yes", "no"):
    print("Error: Please answer yes or no.")

else:
    # Private data should stay local, so route private tasks to Ollama.
    if task == "private":
        model = "llama3.2 (local, Ollama)"
        price_per_1k = 0.0

    elif task == "code":
        model = "Coding cloud model"
        price_per_1k = 2.0

    else:
        model = "Small cloud chat model"
        price_per_1k = 0.5

    # Calculate estimated cost so users can understand token spending.
    estimated_cost = (tokens / 1000) * price_per_1k

    # Long requests may need shortening to reduce token usage.
    if tokens > 4000:
        warning = "Long request: consider shortening it."
    else:
        warning = "Length is fine."

    # Free users have a smaller token allowance in this demo.
    if paid_user == "no" and tokens > 2000:
        access_message = "Upgrade to send long requests."
    else:
        access_message = "Request allowed."

    print("\n" + "=" * 40)
    print("SMART MODEL ROUTER")
    print("=" * 40)
    print(f"Task: {task}")
    print(f"Chosen model: {model}")
    print(f"Estimated tokens: {tokens:,}")
    print(f"Estimated cost: {estimated_cost:.2f} PKR")
    print(f"Token warning: {warning}")
    print(f"Access: {access_message}")
    print("=" * 40)
