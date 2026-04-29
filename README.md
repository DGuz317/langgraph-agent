# langgraph-agent
## Requirements
- Python
- uv
## Project Structure
```bash
.
├── assets/
│   └── MultiAgentSystem.png
├── graphify-out/
│   ├── graph.html
│   ├── graph.json
│   ├── GRAPH_REPORT.md
│   └── memory/
├── pyproject.toml
├── README.md
├── run.sh
├── src/
│   └── agent_app/
│       ├── agent_cards/
│       │   ├── invoice_agent.json
│       │   ├── music_agent.json
│       │   ├── orchestrator_agent.json
│       │   ├── planner_agent.json
│       │   └── refund_agent.json
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── invoice_agent_2.py
│       │   ├── invoice_agent.py
│       │   ├── __main__.py
│       │   ├── music_agent_2.py
│       │   ├── music_agent.py
│       │   ├── orchestrator_agent.py
│       │   ├── planner_agent_2.py
│       │   ├── planner_agent.py
│       │   └── refund_agent.py
│       ├── common/
│       │   ├── agent_executor.py
│       │   ├── base_agent.py
│       │   ├── __init__.py
│       │   ├── prompts.py
│       │   ├── types.py
│       │   ├── utils.py
│       │   └── workflow.py
│       ├── database/
│       │   ├── chinook.db
│       │   ├── get_database.py
│       │   └── __init__.py
│       ├── __init__.py
│       └── mcp_server/
│           ├── __init__.py
│           └── server.py
├── start_system.ps1
├── test/
│   ├── test_client.py
│   ├── test_orchestrator.py
│   └── test_refund.py
└── uv.lock
```
## Setup
Adjust project path in start_system.ps1 file (if you don't want new tab popping everywhere, go to setting at your PowerShell, look for `New instance behavior` and change it to `Attach to the most recently used window`)
```bash
$projectPath = "...\langraph_agent"
```
## Quickstart
### 1. Start the system
```bash
.\start_system.ps1
```
### 2. Navigate to Customer Service Agent tab
Click the link http://127.0.0.1:8050, it will open a adk web . Use the query below for experiment
## Example question:
- I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?
- My customer id is 3. What is my recent invoice?
- Show me AC/DC tracks and my latest invoice. My customer id is 2.