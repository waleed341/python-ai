
"""Lesson 1.6: Prompt Cleaner."""

# Ask for user details because AI prompts need personalized input.
raw_name = input("Enter your name: ")
raw_question = input("Enter your question: ")

# Clean messy input to remove extra spaces and normalize capitalization.
name = raw_name.strip().title()
question = raw_question.strip().capitalize()

# Replace an unwanted word before building the prompt.
question = question.replace("stupid", "***")

# Count characters and estimate tokens using a rough approximation.
characters = len(question)
estimated_tokens = round(characters / 4)

# Check for the Python keyword regardless of capitalization.
mentions_python = "python" in question.lower()

# Limit the question to 150 characters to control prompt length.
short_question = question[:150]

# Example price for practice, not actual API pricing.
price_per_1k_tokens = 0.5
estimated_cost = (estimated_tokens / 1000) * price_per_1k_tokens

# Build a personalized multi-line prompt using an f-string.
prompt = f"""You are a helpful Python tutor.
Greet the student by name: {name}.
Answer in 3 short sentences.
Student question: {short_question}"""

print("\n" + "=" * 40)
print("PROMPT CLEANER")
print("=" * 40)
print(f"Name: {name}")
print(f"Cleaned Question: {question}")
print(f"Characters: {characters}")
print(f"Estimated Tokens: {estimated_tokens}")
print(f"Mentions Python: {mentions_python}")
print(f"Estimated Cost: {estimated_cost:.2f} PKR")
print("=" * 40)
print("FINAL AI PROMPT")
print(prompt)
