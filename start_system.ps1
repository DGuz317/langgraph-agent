# =================================================================
# LangGraph Multi-Agent System Launcher
# =================================================================

Write-Host "Starting LangGraph Multi-Agent System..." -ForegroundColor Cyan

# Ensure we are in the correct directory
$projectPath = "C:\Users\nvdung1\Desktop\langraph_agent"
Set-Location -Path $projectPath

# Function to spawn a new PowerShell window, set its title, and run the command
# Function to spawn a new PowerShell window, set its title, setup the venv, and run the command
function Start-ServiceWindow {
    param([string]$Title, [string]$Command)
    
    # 1. The setup commands specifically for the new window (no pip install)
    $envSetup = "conda deactivate 2>`$null; if (Test-Path '.\.venv\Scripts\Activate.ps1') { .\.venv\Scripts\Activate.ps1 }"
    
    # 2. Combine the setup with the actual uv run command
    $fullCommand = "$envSetup; $Command"
    
    # 3. Launch the window
    $arguments = "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle = '$Title'; cd '$projectPath'; $fullCommand"
    Start-Process powershell -ArgumentList $arguments
}

# 1. Start the MCP Server
Write-Host "-> Starting MCP Server..." -ForegroundColor Yellow
$mcpCommand = "uv run -m a2a_mcp --run mcp-server --host localhost --port 10000 --transport streamable-http"
Start-ServiceWindow -Title "MCP Server (Port 10000)" -Command $mcpCommand

# Give the MCP server a quick second to spin up before the agents try to connect
Start-Sleep -Seconds 2

# 2. Start the Agents
Write-Host "-> Starting Invoice Agent..." -ForegroundColor Yellow
$invoiceCommand = "uv run -m a2a_mcp.agents --host localhost --port 8010 --agent-card agent_cards/invoice_info_agent.json"
Start-ServiceWindow -Title "Invoice Agent (Port 8010)" -Command $invoiceCommand

Write-Host "-> Starting Music Agent..." -ForegroundColor Yellow
$musicCommand = "uv run -m a2a_mcp.agents --host localhost --port 8020 --agent-card agent_cards/music_catalog_agent.json"
Start-ServiceWindow -Title "Music Agent (Port 8020)" -Command $musicCommand

Write-Host "-> Starting Planner Agent..." -ForegroundColor Yellow
$plannerCommand = "uv run -m a2a_mcp.agents --host localhost --port 8030 --agent-card agent_cards/langgraph_planner_agent.json"
Start-ServiceWindow -Title "Planner Agent (Port 8030)" -Command $plannerCommand

Write-Host "-> Starting Orchestrator Agent..." -ForegroundColor Yellow
$orchestratorCommand = "uv run -m a2a_mcp.agents --host localhost --port 8040 --agent-card agent_cards/orchestrator_agent.json"
Start-ServiceWindow -Title "Orchestrator Agent (Port 8040)" -Command $orchestratorCommand

Write-Host "All services have been launched in separate windows!" -ForegroundColor Green