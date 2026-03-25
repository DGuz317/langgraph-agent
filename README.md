# langgraph-agent
## Requirements
- Python
- uv
## Project Structure
```
├── agent_cards/  # (store agent-card.json)
|   └── invoice_info_agent.json
|   └── orchestrator_agent.json
|   └──..	
├── src/
|   └── a2a_mcp/
|   	└── agents/ # contain all agents
|	    └── common/ # contain prompts, types, utils, workflow, agent_executor, base_agent
|	    └── mcp/
|	        └── client.py
|	        └── server.py
|	    └── __init__.py # Convenience methods to start servers.
├── .env
├── pyproject.toml
├── README.md
├── Other files
```
## Setup
Install all dependencies:
```
uv sync
```
## Quickstart
### 1. Start MCP Server:
```
uv run .\mcp\mcp_server.py
```
### 2. Start Supervisor Agent:
```
uv run .\root_agent\supervisor.py
```
## Example question:
- I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?
- My customer id is 3. What is my recent invoice?