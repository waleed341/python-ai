
"""
Lesson 2.5 - AI Skills Toolkit

A reusable AI toolkit for a software business.
Skills: summarize text, translate text, and reply to reviews.
"""

from langchain.chat_models import init_chat_model


# WHY: Create both models once and reuse them in every skill.
precise_model = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.2
)

creative_model = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.8
)


def ask_ai(
    prompt: str,
    system: str = "You are a helpful AI assistant.",
    creative_mode: bool = False
) -> str:
    """Send a prompt to the selected AI model and return its answer."""

    # WHY: Creative tasks benefit from a higher temperature.
    model = creative_model if creative_mode else precise_model

    response = model.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ])

    return response.text


def summarize(text: str) -> str:
    """Summarize text into two short, clear sentences."""

    return ask_ai(
        prompt=f"Summarize this text in two short sentences:\n{text}",
        system="You summarize business information accurately and clearly."
    )


def translate(text: str, language: str = "Urdu") -> str:
    """Translate text into the selected language, Urdu by default."""

    return ask_ai(
        prompt=f"Translate this text into {language}:\n{text}",
        system="You are a professional translator. Return only the translation."
    )


def reply_to_review(review: str) -> str:
    """Write a polite business response to a customer review."""

    return ask_ai(
        prompt=f"Write a short reply to this customer review:\n{review}",
        system=(
            "You represent Zentrox Software Studio, a software business. "
            "Thank the customer, acknowledge concerns, and stay professional. "
            "Do not promise refunds or invent business policies."
        ),
        creative_mode=True
    )


def estimate_tokens(text: str) -> int:
    """Estimate token count using roughly four characters per token."""

    # WHY: This estimate works without calling the AI model.
    if not text:
        return 0

    return (len(text) + 3) // 4


# WHY: Test the helper function before starting the interactive menu.
assert estimate_tokens("") == 0
assert estimate_tokens("abcd") == 1
assert estimate_tokens("abcdefgh") == 2


usage = {
    "summarize": 0,
    "translate": 0,
    "reply": 0
}


print(
    "Zentrox AI Toolkit. "
    "Commands: /summarize, /translate, /reply, bye"
)


while True:
    command = input("Command: ").strip().lower()

    if command == "bye":
        break

    elif command == "/summarize":
        text = input("Text to summarize: ").strip()

        if not text:
            print("Please enter some text.")
            continue

        result = summarize(text)
        usage["summarize"] += 1

        print("AI:", result)

    elif command == "/translate":
        text = input("Text to translate: ").strip()

        if not text:
            print("Please enter some text.")
            continue

        language = input("Language (Enter for Urdu): ").strip()

        # WHY: Pressing Enter uses the function's default language.
        if language:
            result = translate(text, language)
        else:
            result = translate(text)

        usage["translate"] += 1

        print("AI:", result)

    elif command == "/reply":
        review = input("Customer review: ").strip()

        if not review:
            print("Please enter a customer review.")
            continue

        result = reply_to_review(review)
        usage["reply"] += 1

        print("AI:", result)
        print(f"    (review was about {estimate_tokens(review)} tokens)")

    else:
        print(
            "Unknown command. Try /summarize, "
            "/translate, /reply or bye."
        )


print("\nSkills used today:")

# WHY: A loop displays usage for every skill automatically.
for skill, count in usage.items():
    print(f"  {skill}: {count}")
