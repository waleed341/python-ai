
"""
Lesson 2.6 - Saved Bot

A business chatbot that:
1. Reads business facts from faq.json.
2. Remembers conversations between runs.
3. Saves chat history after every successful turn.
4. Handles missing or damaged files.
5. Handles Ollama errors without crashing.
"""

import json
from datetime import datetime
from pathlib import Path

import httpx
import ollama
from langchain.chat_models import init_chat_model


# WHY: Use the script's folder so file paths work
# whether Python runs from the root or code folder.
BASE_DIR = Path(__file__).resolve().parent

FAQ_FILE = BASE_DIR / "faq.json"
HISTORY_FILE = BASE_DIR / "chat_history.json"
ERROR_FILE = BASE_DIR / "errors.log"


def load_faq() -> dict:
    """Load business facts from faq.json."""

    try:
        with open(FAQ_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print("Error: faq.json is missing. Please create it first.")
        raise SystemExit(1)

    except (json.JSONDecodeError, UnicodeError):
        print("Error: faq.json is damaged or contains invalid JSON.")
        raise SystemExit(1)

    except OSError:
        print("Error: faq.json could not be read. Check folder permissions.")
        raise SystemExit(1)


def load_history() -> list[dict]:
    """Load old chat messages or start with an empty history."""

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

        # WHY: A JSON file can be valid but contain
        # the wrong structure, so validate it too.
        if not isinstance(history, list):
            raise ValueError("History must be a list.")

        for message in history:
            if (
                not isinstance(message, dict)
                or message.get("role") not in ("user", "assistant")
                or not isinstance(message.get("content"), str)
            ):
                raise ValueError("Invalid chat message.")

        print(f"Loaded {len(history)} old messages.")
        return history

    except FileNotFoundError:
        return []

    except (json.JSONDecodeError, ValueError, UnicodeError):
        print("History file was damaged. Starting a fresh chat.")
        return []

    except OSError:
        print("History file could not be read. Starting a fresh chat.")
        return []


def save_history(history: list[dict]) -> None:
    """Save chat messages as readable JSON."""

    try:
        temporary = HISTORY_FILE.with_suffix(".tmp")
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
        temporary.replace(HISTORY_FILE)
    except OSError as error:
        log_error(error)
        print("Bot: Your chat is in memory, but could not be saved. Check folder permissions.")


def log_error(error: Exception) -> None:
    """Append an error and timestamp to errors.log."""

    timestamp = datetime.now().isoformat(timespec="seconds")

    try:
        with open(ERROR_FILE, "a", encoding="utf-8") as file:
            file.write(f"{timestamp} | {type(error).__name__}: {error}\n")
    except OSError:
        print("Bot: The local error log could not be written.")


# Load business information.
facts = load_faq()
if not isinstance(facts, dict) or not isinstance(facts.get("prices"), dict):
    print("Error: faq.json must contain business facts and a prices dictionary.")
    raise SystemExit(1)

# WHY: The bot reads facts from JSON rather than
# hardcoding business prices in Python.
system_message = (
    "You are a helpful customer support assistant.\n"
    "Answer questions using these business facts:\n"
    f"{json.dumps(facts, ensure_ascii=False, indent=2)}\n"
    "Do not invent prices, products, or policies.\n"
    "If information is missing, say you do not know.\n"
    "Remember details the customer shares in conversation."
)


# Create the Ollama model once.
llm = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.2
)


# Load any previous conversation.
history = load_history()

print(
    f"{facts.get('business_name', 'Business')} Bot: "
    "Ask me anything. Commands: /reset, /export, bye"
)


while True:
    try:
        question = input("You: ").strip()

    except (KeyboardInterrupt, EOFError):
        print("\nBot: Goodbye! Your chat is saved.")
        break

    if not question:
        continue

    if question.lower() == "bye":
        print("Bot: Goodbye! Your chat is saved.")
        break

    if question.lower() == "/export":
        try:
            with (BASE_DIR / "transcript.txt").open("w", encoding="utf-8") as file:
                for entry in history:
                    file.write(f"{entry['role']}: {entry['content']}\n")
            print("Bot: Exported transcript.txt.")
        except OSError as error:
            log_error(error)
            print("Bot: Transcript could not be exported.")
        continue

    if question.lower() == "/reset":
        history.clear()
        save_history(history)

        print("Bot: Chat history cleared.")
        continue

    # WHY: Add the user question before calling the model
    # so the AI can see the current message.
    history.append({
        "role": "user",
        "content": question
    })

    try:
        messages = [
            {"role": "system", "content": system_message},
            *history
        ]

        response = llm.invoke(messages)
        answer = response.text

        history.append({
            "role": "assistant",
            "content": answer
        })

        # WHY: Saving after every successful turn
        # keeps memory available after restarting.
        save_history(history)

        print("Bot:", answer)

    except (httpx.TransportError, ollama.ResponseError, ConnectionError) as error:
        log_error(error)

        # WHY: Remove the unanswered question
        # so the saved conversation stays consistent.
        history.pop()

        print(
            "Bot: I am offline right now. "
            "Please open the Ollama app and try again."
        )
