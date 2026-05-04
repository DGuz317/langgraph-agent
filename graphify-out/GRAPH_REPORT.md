# Graph Report - langgraph-agent  (2026-05-04)

## Corpus Check
- 27 files · ~13,343 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 213 nodes · 319 edges · 15 communities detected
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]

## God Nodes (most connected - your core abstractions)
1. `BaseAgent` - 22 edges
2. `OrchestratorAgent` - 16 edges
3. `TaskList` - 15 edges
4. `WorkflowGraph` - 14 edges
5. `InvoiceAgent` - 12 edges
6. `MusicAgent` - 12 edges
7. `GenericAgentExecutor` - 11 edges
8. `WorkflowNode` - 11 edges
9. `LangGraphPlannerAgent` - 11 edges
10. `ServerConfig` - 9 edges

## Surprising Connections (you probably didn't know these)
- `AgentExecutor used by invoice agents and music agent` --uses--> `BaseAgent`  [INFERRED]
  src/agent_app/common/agent_executor.py → src/agent_app/common/base_agent.py
- `Initialize the API key for Google Generative AI.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Configure basic logging.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Logger specific config, avoiding clutter in enabling all loggging.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py
- `Get the MCP server configuration.` --uses--> `ServerConfig`  [INFERRED]
  src/agent_app/common/utils.py → src/agent_app/common/types.py

## Hyperedges (group relationships)
- **Quickstart Usage Flow** — readme_start_system_ps1, readme_customer_service_agent_tab, readme_local_url_127_0_0_1_8050, readme_adk_web [EXTRACTED 1.00]
- **Example Query Set** — readme_music_recommendation_query, readme_invoice_query, readme_combined_query [EXTRACTED 1.00]
- **Service Agents Exposed by A2A** — multiagentsystem_refund_agent, multiagentsystem_music_agent, multiagentsystem_invoice_agent [EXTRACTED 0.97]

## Communities

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (20): ABC, InvoiceAgent, Respond to the user in this format., InvoiceAgent - specialized for retrieving and processing invoice information., ResponseFormat, Respond to the user in this format., ResponseFormat, Response to user using this format (+12 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (11): OrchestratorAgent, Add a node to the graph., Execute and stream response., # TODO: Make the graph dynamically iterable over edges, Represents a graph of workflow nodes., Represents the status of a workflow and its associated node., Represents a single node in a workflow graph.      Each node encapsulates a spec, Status (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.15
Nodes (9): AgentExecutor, get_agent(), main(), Get the agent, given an agent card., Starts an Agent server., MusicAgent, MusicAgent - specifically is to focused on helping customers discover and learn, GenericAgentExecutor (+1 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (16): cli(), find_agent(), find_resource(), get_invoices_by_customer_sorted_by_date(), get_tracks_by_artist(), init_session(), main(), Reads a resource from the connected MCP server.      Args:         session: The (+8 more)

### Community 4 - "Community 4"
Cohesion: 0.17
Nodes (11): Server Confgiguration., ServerConfig, config_logger(), config_logging(), get_mcp_server_config(), init_api_key(), Initialize the API key for Google Generative AI., Configure basic logging. (+3 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (14): check_for_songs(), get_albums_by_artist(), get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date(), get_invoices_sorted_by_unit_price(), get_songs_by_genre(), get_tracks_by_artist(), Get albums by an artist.          Args:         artist (str): Name of the artist (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.15
Nodes (15): ADK web interface, agent_cards directory, Combined tracks and invoice example query, Customer Service Agent tab, Recent invoice example query, langgraph-agent, http://127.0.0.1:8050, mcp/client.py (+7 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (12): A2A Server (Planner), A2A Server (Services), Agent Cards, Database, Invoice Agent, MCP Server, MCP tools, Music Agent (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (10): check_for_songs(), get_albums_by_artist(), get_songs_by_genre(), get_tracks_by_artist(), Check if a song exists by its name.          Args:         song_title (str): Nam, Response to user using this format, Get albums by an artist.          Args:         artist (str): Name of the artist, Get all songs for customer using artist name.          Args:         artist (str (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (9): build_agent_card_embeddings(), generate_embeddings(), load_agent_cards(), main(), Loads agent cards, generates embeddings for them, and returns a DataFrame., Initializes and runs the Agent Cards MCP server.      Args:         host: The ho, Generates embeddings for the given text using local Ollama API.      Args:, Loads agent card data from JSON files within a specified directory.      Returns (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.22
Nodes (8): get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date(), get_invoices_sorted_by_unit_price(), Response to user using this format, Look up all invoices for a customer using their ID.     The invoices are sorted, Use this tool when the customer wants to know the details of one of their invoic, This tool will take in an invoice ID and a customer ID and return the employee i, ResponseFormat

### Community 11 - "Community 11"
Cohesion: 0.48
Nodes (3): LangGraphPlannerAgent, Planner Agent backed by LangGraph., BaseAgent

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (2): main(), send_message()

### Community 14 - "Community 14"
Cohesion: 0.67
Nodes (2): process_refund(), Processes a refund for a customer. This is a sensitive action!

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (2): get_engine_for_chinook_db(), Pull SQL file, populate in-memory database, and create engine.          Download

## Ambiguous Edges - Review These
- `A2A Server (Planner)` → `A2A Server (Services)`  [AMBIGUOUS]
  assets/MultiAgentSystem.png · relation: conceptually_related_to

## Knowledge Gaps
- **48 isolated node(s):** `Initializes and manages an MCP ClientSession based on the specified transport.`, `Calls the 'find_agent' tool on the connected MCP server.      Args:         sess`, `Reads a resource from the connected MCP server.      Args:         session: The`, `Calls the 'get_tracks_by_artist' tool on the connected MCP server.      Args:`, `Calls the 'get_invoices_by_customer_sorted_by_date' tool on the connected MCP se` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (3 nodes): `main()`, `test_orchestrator.py`, `send_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (3 nodes): `process_refund()`, `Processes a refund for a customer. This is a sensitive action!`, `refund_agent.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (3 nodes): `get_engine_for_chinook_db()`, `Pull SQL file, populate in-memory database, and create engine.          Download`, `get_database.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `A2A Server (Planner)` and `A2A Server (Services)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `BaseAgent` connect `Community 0` to `Community 1`, `Community 2`, `Community 11`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **Why does `OrchestratorAgent` connect `Community 1` to `Community 0`, `Community 2`, `Community 11`, `Community 4`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `WorkflowNode` connect `Community 1` to `Community 3`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `BaseAgent` (e.g. with `GenericAgentExecutor` and `AgentExecutor used by invoice agents and music agent`) actually correct?**
  _`BaseAgent` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `OrchestratorAgent` (e.g. with `Get the agent, given an agent card.` and `Starts an Agent server.`) actually correct?**
  _`OrchestratorAgent` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `TaskList` (e.g. with `ResponseFormat` and `InvoiceAgent`) actually correct?**
  _`TaskList` has 12 INFERRED edges - model-reasoned connections that need verification._