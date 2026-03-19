from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.managed.is_last_step import RemainingSteps

class State(TypedDict):
    """Represents the state of our LangGraph agent."""
    # Unique identifier for the current customer
    customer_id: str
    
    # Conversation history (add_messages ensures we append, not overwrite)
    messages: Annotated[List[AnyMessage], add_messages]
    
    # Information from long-term memory
    loaded_memory: str
    
    # LangGraph managed state to prevent infinite loops
    remaining_steps: RemainingSteps