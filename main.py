import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from agent import get_invoice_agent

load_dotenv()

# def main():
#     checkpointer = MemorySaver()
#     in_memory_store = InMemoryStore()

#     # 2. Initialize Agent
#     agent = get_invoice_agent(checkpointer, in_memory_store)

#     # 3. Run a query
#     config = {"configurable": {"thread_id": "user-123"}}
#     inputs = {
#         "messages": [("user", "Can you find my most recent invoices? I am customer 1.")],
#         "customer_id": "1"
#     }

#     for chunk in agent.stream(inputs, config=config, stream_mode="values"):
#         chunk["messages"][-1].pretty_print()

# if __name__ == "__main__":
#     main()