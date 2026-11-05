"""Lesson 2.4 stretch: compare six business-rule answers with a local AI model."""
from langchain.chat_models import init_chat_model

facts = {"name":"Sweet Crumbs","city":"Lahore","hours":"Daily, 9 AM-10 PM",
         "prices":{"chocolate cake":1500,"cupcake":250,"brownie":300}}
questions = ["hello", "What are your opening hours?", "Where are you located?",
             "What is the price of cupcake?", "My order is late", "Can I order a wedding cake for Sunday?"]
llm = init_chat_model("ollama:llama3.2",temperature=0.2)
unanswered = 0
for number, question in enumerate(questions, start=1):
    message = question.strip().lower()
    # WHY: Complaints take priority so routine rules cannot hide an unhappy customer.
    if "late" in message.strip(".!?").split() or "complaint" in message:
        rule_answer = "Please contact the business owner for help with this complaint."
    elif message in ("hi","hello","salam"):
        rule_answer = "Hello! Welcome to Sweet Crumbs."
    elif "hours" in message:
        rule_answer = facts["hours"]
    elif "where" in message or "location" in message:
        rule_answer = facts["city"]
    elif "price" in message and "cupcake" in message:
        rule_answer = f"cupcake: {facts['prices']['cupcake']:,} PKR"
    else:
        unanswered += 1
        rule_answer = "I do not know; ask the owner."
    # WHY: Supply facts to compare the AI with rules against the same business data.
    response = llm.invoke([{"role":"system","content":f"Answer briefly using only these business facts: {facts}. Admit missing facts. Do not promise compensation or notifications."},
                           {"role":"user","content":question}])
    print(f"{number}. {question}\n   Rules: {rule_answer}\n   AI: {response.text}")
print(f"Rules could not answer {unanswered} of {len(questions)} questions.")
