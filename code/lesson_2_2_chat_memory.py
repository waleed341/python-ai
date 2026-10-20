
"""
Lesson 2.2 - Personal Tutor with Memory

A Python AI tutor that remembers recent conversations.
"""

from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.2
)

# WHY: The system message sets the tutor's role and answer length.
system_message = {
    "role": "system",
    "content": "You are a friendly AI tutor. Answer in 2 to 3 short sentences."
}

messages = [system_message]

print("Tutor: Ask me anything. Commands: /reset, /count, bye")

while True:
    question = input("You: ").strip()

    if question == "":
        continue

    if question.lower() == "bye":
        print("Tutor: Goodbye!")
        break

    elif question.lower() == "/reset":
        # WHY: Keep the system message so the tutor retains its instructions.
        messages = [messages[0]]
        print("Tutor: Memory cleared.")
        continue

    elif question.lower() == "/count":
        print(f"Tutor: {len(messages)} messages in memory.")
        continue

    # WHY: Save user questions so the AI understands follow-up questions.
    messages.append({
        "role": "user",
        "content": question
    })

    response = llm.invoke(messages)

    print("Tutor:", response.text)

    # WHY: Save the AI reply as well as the user's question.
    messages.append({
        "role": "assistant",
        "content": response.text
    })

    # WHY: Limit memory to avoid sending unlimited conversation history.
    if len(messages) > 9:
        messages = [messages[0]] + messages[1:][-8:]

    if response.usage_metadata:
        tokens_sent = response.usage_metadata["input_tokens"]
        print(f"       (tokens sent: {tokens_sent})")
