import os
import sys
import uuid
import logging
import uvicorn
from dotenv import load_dotenv
from .tools import invoice_tools
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from .invoice_subagent_prompt import invoice_subagent_prompt
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

sys.path.insert(1, r'C:\Users\nvdung1\Desktop\langraph_agent\database')
import get_database

api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=api_key,
)

invoice_information_subagent = create_agent(
    model=llm,                          
    tools=invoice_tools,            
    name="invoice_information_subagent", 
    system_prompt=invoice_subagent_prompt, 
    # state_schema=State,             
    # checkpointer=checkpointer,      
    # store = in_memory_store         
)

# Define sub-agent as tool for supervisor-agent
@tool
def get_invoice_infomation(request: str) -> str:
    """Get invoice information using natural language .

    Use this when the user want to retrieve the invoice information.
    Handles retrieves all invoices sorted by invoice date for a customer, retrieves all invoices sorted by unit price for a customer, retrieves the employee information associated with an invoice and a customer  

    Input: Natural language invoice information request (e.g., 'My customer id is 1. What was my most recent invoice, and who was the employee that helped me with it?')
    """
    result = invoice_information_subagent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].text

# thread_id = uuid.uuid4()

# query = "My customer id is 1. What was my most recent invoice, and who was the employee that helped me with it?"

# # Set up the configuration with the thread ID.
# config = {"configurable": {"thread_id": thread_id}}

# for step in invoice_information_subagent.stream(
#     {"messages": [{"role": "user", "content": query}]},
#     config,
# ):
#     for update in step.values():
#         for message in update.get("messages", []):
#             message.pretty_print()