# Graph Report - /home/dguz317/Desktop/langgraph_tutorial/langgraph-agent  (2026-05-06)

## Corpus Check
- Corpus is ~5,743 words - fits in a single context window. You may not need a graph.

## Summary
- 103 nodes · 105 edges · 30 communities (25 shown, 5 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Database & MCP Server Tools|Database & MCP Server Tools]]
- [[_COMMUNITY_Agent Prompts & Configuration|Agent Prompts & Configuration]]
- [[_COMMUNITY_Multi-Agent System Architecture|Multi-Agent System Architecture]]
- [[_COMMUNITY_Agent Builder Patterns|Agent Builder Patterns]]
- [[_COMMUNITY_Integration Tests|Integration Tests]]
- [[_COMMUNITY_Refund Agent Flow|Refund Agent Flow]]
- [[_COMMUNITY_Main Entry Point|Main Entry Point]]
- [[_COMMUNITY_Refund Agent Implementation|Refund Agent Implementation]]
- [[_COMMUNITY_Database Engine Setup|Database Engine Setup]]
- [[_COMMUNITY_Main Function|Main Function]]
- [[_COMMUNITY_QA Chain-of-Thought Prompt|QA Chain-of-Thought Prompt]]

## God Nodes (most connected - your core abstractions)
1. `LangChain SQLDatabase wrapper` - 8 edges
2. `MCP Server (FastMCP)` - 7 edges
3. `get_invoices_by_customer_sorted_by_date()` - 5 edges
4. `get_invoices_sorted_by_unit_price()` - 5 edges
5. `get_employee_by_invoice_and_customer()` - 5 edges
6. `get_albums_by_artist()` - 5 edges
7. `get_tracks_by_artist()` - 5 edges
8. `get_songs_by_genre()` - 5 edges
9. `check_for_songs()` - 5 edges
10. `ResponseFormat` - 5 edges

## Surprising Connections (you probably didn't know these)
- `Refund Agent (Google ADK)` --rationale_for--> `LangGraph Multi-Agent Customer Support System`  [INFERRED]
  src/agent_app/agents/refund_agent.py → README.md
- `ResponseFormat` --semantically_similar_to--> `ResponseFormat`  [INFERRED] [semantically similar]
  src/agent_app/agents/invoice_agent/agent.py → src/agent_app/agents/music_agent/agent.py
- `get_invoices_by_customer_sorted_by_date()` --references--> `LangChain SQLDatabase wrapper`  [INFERRED]
  src/agent_app/mcp_server/server.py → src/agent_app/database/get_database.py
- `get_invoices_sorted_by_unit_price()` --references--> `LangChain SQLDatabase wrapper`  [INFERRED]
  src/agent_app/mcp_server/server.py → src/agent_app/database/get_database.py
- `get_employee_by_invoice_and_customer()` --references--> `LangChain SQLDatabase wrapper`  [INFERRED]
  src/agent_app/mcp_server/server.py → src/agent_app/database/get_database.py

## Hyperedges (group relationships)
- **MCP Invoice Tools** — mcp_server_server_get_invoices_by_customer_sorted_by_date, mcp_server_server_get_invoices_sorted_by_unit_price, mcp_server_server_get_employee_by_invoice_and_customer [EXTRACTED 1.00]
- **MCP Music Tools** — mcp_server_server_get_albums_by_artist, mcp_server_server_get_tracks_by_artist, mcp_server_server_get_songs_by_genre, mcp_server_server_check_for_songs [EXTRACTED 1.00]
- **LangChain-based Specialized Agents** — planner_agent_agent_build_planner_agent, invoice_agent_agent_build_invoice_agent, music_agent_agent_build_music_agent, aggregator_agent_agent_build_aggregator_agent [INFERRED 0.95]
- **Agent Response Format Models** — planner_agent_agent_responseformat, invoice_agent_agent_responseformat, music_agent_agent_responseformat, aggregator_agent_agent_responseformat [INFERRED 0.95]
- **Test Suite Fixtures and Tests** — conftest_runtime, conftest_agents, test_planner_test_planner_single_intent, test_orchestrator_test_full_pipeline, test_invoice_test_invoice_agent_single, test_music_test_music_agent_single [EXTRACTED 1.00]
- **Multi-Agent Customer Support Architecture** — planner_agent_agent_build_planner_agent, invoice_agent_agent_build_invoice_agent, music_agent_agent_build_music_agent, aggregator_agent_agent_build_aggregator_agent, refund_agent_refund_agent, langgraphagent_architecture [INFERRED 0.85]

## Communities (30 total, 5 thin omitted)

### Community 0 - "Database & MCP Server Tools"
Cohesion: 0.16
Nodes (20): LangChain SQLDatabase wrapper, Chinook SQLAlchemy engine, get_engine_for_chinook_db, Invoice Agent allowed tool names, check_for_songs(), get_albums_by_artist(), get_employee_by_invoice_and_customer(), get_invoices_by_customer_sorted_by_date() (+12 more)

### Community 1 - "Agent Prompts & Configuration"
Cohesion: 0.21
Nodes (10): build_invoice_agent(), Response to user using this format, ResponseFormat, build_music_agent(), Response to user using this format, ResponseFormat, Aggregator Agent Prompt, Invoice Agent Prompt (+2 more)

### Community 2 - "Multi-Agent System Architecture"
Cohesion: 0.18
Nodes (12): A2A Server (Task Agents), A2A Server (Planner), Agent Cards, Database, Invoice Agent, MCP Server, MCP Tools, Music Agent (+4 more)

### Community 3 - "Agent Builder Patterns"
Cohesion: 0.33
Nodes (7): build_aggregator_agent(), ResponseFormat, BaseModel, build_planner_agent(), Structured plan produced by the planner agent., ResponseFormat, Task

### Community 4 - "Integration Tests"
Cohesion: 0.33
Nodes (6): agents pytest fixture, runtime pytest fixture, test_invoice_agent_single, test_music_agent_single, test_full_pipeline, test_planner_single_intent

### Community 5 - "Refund Agent Flow"
Cohesion: 0.4
Nodes (5): LangGraph Multi-Agent Customer Support System, Approval Agent (Google ADK), process_refund, Refund Agent (Google ADK), Root agent for refund module

## Knowledge Gaps
- **32 isolated node(s):** `Look up all invoices for a customer using their ID.     The invoices are sorted`, `Use this tool when the customer wants to know the details of one of their invoic`, `This tool will take in an invoice ID and a customer ID and return the employee i`, `Get albums by an artist.          Args:         artist (str): Name of the artist`, `Get all songs for customer using artist name.          Args:         artist (str` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `build_music_agent()` connect `Agent Prompts & Configuration` to `Database & MCP Server Tools`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `Music Agent allowed tool names` connect `Database & MCP Server Tools` to `Agent Prompts & Configuration`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `build_invoice_agent()` connect `Agent Prompts & Configuration` to `Database & MCP Server Tools`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `LangChain SQLDatabase wrapper` (e.g. with `get_invoices_by_customer_sorted_by_date()` and `get_invoices_sorted_by_unit_price()`) actually correct?**
  _`LangChain SQLDatabase wrapper` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Look up all invoices for a customer using their ID.     The invoices are sorted`, `Use this tool when the customer wants to know the details of one of their invoic`, `This tool will take in an invoice ID and a customer ID and return the employee i` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._