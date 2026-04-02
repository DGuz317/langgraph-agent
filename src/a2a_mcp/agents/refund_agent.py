import os
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent

from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()
logger = logging.getLogger(__name__)

def process_refund(customer_id: int, track_name: str, amount: float) -> str:
    """Processes a refund for a customer. This is a sensitive action!"""
    logger.info(f"Processing refund of ${amount} for customer {customer_id} on track '{track_name}'")
    return f"Successfully processed ${amount} refund for customer {customer_id}."

Approval_Agent = Agent(
    name="Approval_Agent",
    model="gemini-2.5-flash",
    description="Agent for confirming critical actions like refunds with a human approver.",
    instruction="""
    You are an Approval Agent. Your task is to act as a security checkpoint.
    When another agent (like the Refund Agent) delegates to you for a refund:
    1. Present the details of the refund (customer, track, amount) to the human user clearly.
    2. Ask the human user for their explicit 'Yes' or 'No' approval to proceed.
    3. Conclude your execution and explicitly return the human's decision back to the delegator agent.
    """,
    tools=[],
)

Refund_Agent = Agent(
    name="Refund_Agent",
    model="gemini-2.5-flash",
    description="Agent that exclusively processes refunds.",
    instruction="""
    You handle processing refunds. Whenever you are invoked to process a refund, you MUST call the Approval_Agent to get human approval. 
    After getting human approval, you MUST call the process_refund tool.
    """,
    tools=[process_refund],
    sub_agents=[Approval_Agent],
)

root_agent = Refund_Agent

app = to_a2a(root_agent, port=8060)
