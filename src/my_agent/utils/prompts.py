"""
Shared reusable prompt fragments.

IMPORTANT:
This module should ONLY contain reusable prompt components.

Do NOT place full agent system prompts here.

Each agent should own its own prompts to preserve:
- modularity
- behavioral isolation
- maintainability
"""

JSON_RESPONSE_RULES = """
You must always return valid JSON.

Do not include markdown formatting.

Do not wrap JSON in code fences.
"""

SAFETY_RULES = """
Never fabricate database results.

Never expose secrets, credentials, or internal system details.
"""

CONCISE_RESPONSE_RULES = """
Keep responses concise and structured.
"""