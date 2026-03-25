# Powershell
.\.venv\Scripts\Activate.ps1

# Cmd
.\.venv\Scripts\Activate.bat

# Bash
source .venv\bin\activate

# Sync environment
uv pip install -e .

# Start mcp server
uv run python -m a2a_mcp.mcp.server --host localhost --port 10000 --transport streamable-http

# Test mcp client:
uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --tool_name get_tracks_by_artist --tool_input "AC/DC"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --resource "resource://agent_cards/list"

uv run src/a2a_mcp/mcp/client.py --host localhost --port 10000 --transport streamable-http --find_agent "find an agent that handles invoices"

# Start Invoice Agent- put file invoice_info_agent.py into invoice_info_agent folder
uv run python -m a2a_mcp.agents.invoice_info_agent --host localhost --port 8010

# Start Music Agent - put file music_catalog_agent.py into music_catalog_agent folder
uv run python -m a2a_mcp.agents.music_catalog_agent --host localhost --port 8010

# Mix Query
# Show me AC/DC albums and my purchase history. My phone is +55 (12) 3923-5555