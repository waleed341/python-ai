
"""
Lesson 2.4 - Batch Product Writer

Generate one-sentence AI descriptions for business services.
Skip services without a price and track tokens and time.
"""

import time

from langchain.chat_models import init_chat_model


# WHY: Keep all service prices in one dictionary.
products = {
    "Website Development": 30000,
    "AI Chatbot": 20000,
    "Business Automation": 15000,
    "Landing Page": 10000,
    "Old Service": 0,
}

# WHY: Create the model only once instead of loading it in every loop.
llm = init_chat_model(
    model="ollama:llama3.2",
    temperature=0.2,
)

results = []

# WHY: Accumulators track total AI usage across all descriptions.
total_tokens = 0
total_seconds = 0.0

for name, price in products.items():

    # WHY: A price of zero means this service should be skipped.
    if price == 0:
        print(f"Skipping {name} (no price)")
        continue

    prompt = (
        "You are a marketing writer for a software company. "
        f"Write exactly one short sentence describing {name}. "
        f"The service costs {price} PKR. "
        "Do not invent features or guarantees. "
        "Return only the description."
    )

    start_time = time.perf_counter()

    response = llm.invoke(prompt)

    seconds = time.perf_counter() - start_time

    tokens = 0

    if response.usage_metadata:
        tokens = response.usage_metadata.get("total_tokens", 0)

    total_tokens += tokens
    total_seconds += seconds

    # WHY: Store structured results so they can be printed later.
    results.append({
        "item": name,
        "price": price,
        "text": response.text.strip(),
    })


print("=" * 50)

# WHY: enumerate() creates menu numbers starting from 1.
for number, product in enumerate(results, start=1):
    print(
        f"{number}. {product['item']} "
        f"({product['price']} PKR)"
    )
    print(f"   {product['text']}")

print("=" * 50)

print(
    f"{len(results)} descriptions, "
    f"{total_tokens} tokens, "
    f"{total_seconds:.1f} seconds"
)
