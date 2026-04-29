---
type: "query"
date: "2026-04-28T04:10:10.192984+00:00"
question: "What is the exact relationship between A2A Server (Planner) and A2A Server (Services)? (path trace)"
contributor: "graphify"
source_nodes: ["A2A Server (Planner)", "Orchestrator Agent", "A2A Server (Services)"]
---

# Q: What is the exact relationship between A2A Server (Planner) and A2A Server (Services)? (path trace)

## Answer

Most supported relationship path is: A2A Server (Planner) -> Orchestrator Agent -> A2A Server (Services), where both edges are EXTRACTED references from assets/MultiAgentSystem.png with confidence 1.0. This indicates Planner and Services are sibling/peer A2A servers connected operationally through the Orchestrator Agent, not via a proven direct dependency. Alternative EXTRACTED path also goes through MCP Server: Planner -> Orchestrator -> MCP Server -> Services. The direct Planner <-> Services edge exists but remains AMBIGUOUS (conceptually_related_to, 0.28).

## Source Nodes

- A2A Server (Planner)
- Orchestrator Agent
- A2A Server (Services)