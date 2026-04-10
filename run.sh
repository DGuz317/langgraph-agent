# Window
.\.venv\Scripts\Activate.ps1

# MasOS
.\.venv\Scripts\Activate.bat

# Linux
source .venv\bin\activate


# Start mcp server
uv run -m mcp_server.server --run mcp-server --host localhost --port 10000 --transport streamable-http

# Test mcp client:
uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --tool_name get_tracks_by_artist --tool_input "AC/DC"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --resource "resource://agent_cards/list"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --find_agent "find an agent that handles invoices"

# Start Agents

uv run -m agents --host localhost --port 8010 --agent-card agent_cards/invoice_agent.json

uv run -m agents --host localhost --port 8020 --agent-card agent_cards/music_agent.json

uv run -m agents --host localhost --port 8030 --agent-card agent_cards/refund_agent.json

uv run -m agents --host localhost --port 8040 --agent-card agent_cards/planner_agent.json

uv run -m agents --host localhost --port 8050 --agent-card agent_cards/orchestrator_agent.json

# Test Invoice Agent
uv run test_invoice.py

# Test Music Agent
uv run test_music.py

# Test Orchestrator Agent
uv run test_orchestrator.py
