# LangGraph Agent connect with ADK Agent
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
|	    └── common/ # contain prompts, types, utils, agent_executor, base_agent
|	    └── mcp/
|	        └── client.py
|	        └── server.py
|	    └── __init__.py # Convenience methods to start servers.
|       └── agent.py # help with adk agent
├── .env
├── pyproject.toml
├── README.md
├── .gitignore
├── chinook.db
├── start_system.ps1 # All in one set up environment and run all services

```
## Setup
Adjust project path in `start_system.ps1` file (if you don't want new tab popping everywhere, go to setting at your PowerShell, look for `New instance behavior` and change it to `Attach to the most recently used window`)
```
$projectPath = "...\langraph_agent"
```
## Quickstart
### 1. Start the system
In your powershell, cd to the `langraph_agent` directory then run
```
.\start_system.ps1
```
### 2. Navigate to Customer Service Agent tab
Click the link `http://127.0.0.1:8050`, it will open a adk web . Use the query below for experiment

## Example question:
- I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?
- My customer id is 3. What is my recent invoice?
- Show me AC/DC tracks and my latest invoice. My customer id is 2. 