import os
import sys
import uuid
import logging
import uvicorn
from dotenv import load_dotenv
from tools import music_tools
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from catalog_subagent_prompt import catalog_subagent_prompt
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

music_catalog_information_subagent = create_agent(
    model=llm,                          
    tools=music_tools,            
    name="music_catalog_information_subagent", 
    system_prompt=catalog_subagent_prompt, 
    # state_schema=State,             
    # checkpointer=checkpointer,      
    # store = in_memory_store         
)

# Define sub-agent as tool for supervisor-agent
@tool
def get_music_information(request: str) -> str:
    


# thread_id = uuid.uuid4() # Generate a new unique thread ID for this test conversation.

# # Define a sample question for the music catalog sub-agent.
# question = "I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?"

# Set up the configuration with the thread ID.
# config = {"configurable": {"thread_id": thread_id}}

# for step in invoice_information_subagent.stream(
#     {"messages": [{"role": "user", "content": query}]},
#     config,
# ):
#     for update in step.values():
#         for message in update.get("messages", []):
#             message.pretty_print()

