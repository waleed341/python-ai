"""Bounded create_agent loop with checkpointer memory and visible tool results."""
from uuid import uuid4
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from .config import MAX_STEPS, MODEL, PROVIDER, make_model
from .tools import BUSINESS_TOOLS, LIVE_TOOLS

SYSTEM = (
    "You assist Sweet Crumbs. Use tools for all business facts, prices, orders and live data. "
    "Never invent facts or owner approval. Call place_order ONLY for an explicit request "
    "to place a new order with item, quantity and customer name supplied. "
    "Introductions and price questions are not order requests. Conversation messages "
    "are valid evidence for personal details: if the user states their name, remember it "
    "and answer name questions directly from that chat history, without using a tool. "
    "Confirm a saved order only if the tool confirms it."
)

def build_agent(live: bool = False):
    """Construct the graph once, with a bounded number of model calls per turn."""
    return create_agent(
        model=make_model(), tools=BUSINESS_TOOLS + (LIVE_TOOLS if live else []),
        system_prompt=SYSTEM,
        middleware=[ModelCallLimitMiddleware(run_limit=MAX_STEPS, exit_behavior="error")],
        checkpointer=InMemorySaver(),
    )

def chat(live: bool = False) -> None:
    """Run an interactive session; reset starts a new checkpoint thread."""
    agent = build_agent(live)
    config = {"configurable":{"thread_id":str(uuid4())}, "recursion_limit":MAX_STEPS * 4 + 4}
    print(f"Sweet Crumbs ({PROVIDER}: {MODEL}). Commands: /reset, bye")
    while True:
        try:
            question = input("You: ").strip()
            if question.lower() == "bye":
                break
            if not question:
                continue
            if question.lower() == "/reset":
                config["configurable"]["thread_id"] = str(uuid4())
                print("Chat memory reset. Orders retained.")
                continue
            result = agent.invoke({"messages":[{"role":"user","content":question}]},config)
            messages = result["messages"]
            start = max(i for i,message in enumerate(messages) if message.type == "human")
            calls = {}
            for message in messages[start:]:
                for call in getattr(message,"tool_calls",[]):
                    calls[call["id"]] = call
                if message.type == "tool":
                    call = calls.get(message.tool_call_id,{"name":message.name,"args":{}})
                    print(f"  [tool] {call['name']}({call['args']}) -> {message.content}")
            print(f"Agent: {messages[-1].text}")
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as error:
            print(f"This turn could not finish: {error}. Check your model connection or settings.")
            # WHY: A fresh thread avoids retaining an incomplete tool-call cycle.
            config["configurable"]["thread_id"] = str(uuid4())
