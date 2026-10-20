
"""
Lesson 2.1 - First AI Call

Build an AI tutor using LangChain and Ollama.
"""

import time
from langchain.chat_models import init_chat_model

# Ask the student what they want to learn.
topic = input("Enter a topic: ").strip()
level = input("Enter your level (beginner/intermediate/advanced): ").strip()

if topic == "":
    topic = "Python variables"

if level == "":
    level = "beginner"

# WHY: A system message tells the AI how it should behave.
system_message = f"""
You are a friendly AI tutor.
Explain {topic} to a {level} student.
Use simple English and one practical example.
Keep your answer short.
"""

# WHY: A low temperature helps produce focused, consistent answers.
llm = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.2
)

# Record the start time before calling the model.
start_time = time.time()

response = llm.invoke([
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"Teach me {topic}."}
])

# Calculate how long the AI call took.
end_time = time.time()
execution_time = end_time - start_time

print("\n--- AI Tutor Answer ---")
print(response.content)

# Display token usage when the model provides it.
usage = response.usage_metadata

if usage:
    print("\n--- Token Usage ---")
    print("Input tokens:", usage.get("input_tokens", 0))
    print("Output tokens:", usage.get("output_tokens", 0))
    print("Total tokens:", usage.get("total_tokens", 0))
else:
    print("\nToken usage not available.")

print(f"\nExecution time: {execution_time:.2f} seconds")
