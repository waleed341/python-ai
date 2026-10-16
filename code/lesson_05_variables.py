
"""Lesson 1.5: AI Model Profile Card."""

# Use actual model information verified through Ollama.
model_name = "gemma3:270m"
context_window = 32768
price_per_1k_tokens = 0.0
runs_locally = True

# Display model information and verify each variable's data type.
print("=== AI Model Profile Card ===")

print(f"Model: {model_name} | Type: {type(model_name)}")
print(f"Context Window: {context_window} | Type: {type(context_window)}")
print(f"Price per 1K Tokens: {price_per_1k_tokens} | Type: {type(price_per_1k_tokens)}")
print(f"Runs Locally: {runs_locally} | Type: {type(runs_locally)}")

# Convert input to int because input() returns a string.
tokens_used = int(input("\nEnter tokens used per chat: "))

# Calculate the estimated cost using the price per 1000 tokens.
estimated_cost = (tokens_used / 1000) * price_per_1k_tokens

print("\n=== Token Cost Estimate ===")
print(f"Tokens Used: {tokens_used}")
print(f"Estimated Cost: {estimated_cost:.2f} PKR")

# Ask for daily chats to estimate monthly token usage.
chats_per_day = int(input("\nEnter chats per day: "))

# Assume each chat uses the same number of tokens entered above.
monthly_tokens = chats_per_day * tokens_used * 30
monthly_cost = (monthly_tokens / 1000) * price_per_1k_tokens

print("\n=== 30-Day Cost Estimate ===")
print(f"Chats Per Day: {chats_per_day}")
print(f"Monthly Tokens: {monthly_tokens}")
print(f"Estimated Monthly Cost: {monthly_cost:.2f} PKR")
