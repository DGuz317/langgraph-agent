# langgraph-agent
## Requirements
- Python
- uv
## Project Structure
```
├── mcp/
│   └── mcp_server.py
├── root_agent/
│   └── supervisor.py
|   └── invoice_info_agent/
|       └── agent.py
|   └── music_catalog_agent/
|       └── agent.py
└── README.md
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
### 2. Start Aupervisor Agent:
```
uv run .\root_agent\supervisor.py
```
## Example question:
- I like the Rolling Stones. What songs do you recommend by them or by other artists that I might like?
- My customer id is 3. What is my recent invoice?