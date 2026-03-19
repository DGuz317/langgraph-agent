import os
import sys
import uuid
import logging
import uvicorn
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from supervisor_prompt import supervisor_prompt
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage

# Subagents as tools
from invoice_info_agent.agent import get_invoice_infomation
from music_catalog_agent.agent import get_music_information


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

supervisor_subagent = create_agent(
    model=llm,                          
    tools=[get_invoice_infomation, get_music_information],            
    name="supervisor_subagent", 
    system_prompt=supervisor_prompt, 
    # state_schema=State,             
    # checkpointer=checkpointer,      
    # store = in_memory_store         
)

thread_id = uuid.uuid4()

query = "I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?"

# Set up the configuration with the thread ID.
config = {"configurable": {"thread_id": thread_id}}

for step in supervisor_subagent.stream(
    {"messages": [{"role": "user", "content": query}]},
    config,
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()