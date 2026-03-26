# Powershell
.\.venv\Scripts\Activate.ps1

# Cmd
.\.venv\Scripts\Activate.bat

# Bash
source .venv\bin\activate

# Sync environment
uv pip install -e .

# Start mcp server
uv run -m a2a_mcp --run mcp-server --host localhost --port 10000 --transport streamable-http

# Test mcp client:
uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --tool_name get_tracks_by_artist --tool_input "AC/DC"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --resource "resource://agent_cards/list"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --find_agent "find an agent that handles invoices"

# Start Invoice Agent
uv run -m a2a_mcp.agents --host localhost --port 8010 --agent-card agent_cards/invoice_info_agent.json

# Start Music Agent
uv run -m a2a_mcp.agents --host localhost --port 8020 --agent-card agent_cards/music_catalog_agent.json

# Start Planner Agent
uv run -m a2a_mcp.agents --host localhost --port 8030 --agent-card agent_cards/langgraph_planner_agent.json

# Start Orchestrator Agent
uv run -m a2a_mcp.agents --host localhost --port 8040 --agent-card agent_cards/orchestrator_agent.json

# Test Invoice Agent
uv run test_invoice.py

# Test Music Agent
uv run test_music.py

# Test Orchestrator Agent
uv run test_orchestrator.py




https://bixtech.ai/agent-orchestration-and-agenttoagent-communication-with-langgraph-a-practical-guide/
https://bixtech.ai/ai-agents-explained-the-complete-2025-guide-to-build-deploy-and-scale-autonomous-toolusing-assistants/#frameworks-and-patterns