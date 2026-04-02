# Adjust this path
#=======================================================================
$projectPath = "C:\Users\nvdung1\Desktop\langraph_agent"
#=======================================================================

function Setup-LangGraph {
    Write-Host "Setting up LangGraph Agent Environment..." -ForegroundColor Cyan

    Set-Location -Path $projectPath

    # Safely deactivate conda if active
    if ($env:CONDA_DEFAULT_ENV) {
        Write-Host "Deactivating Conda ($env:CONDA_DEFAULT_ENV)..." -ForegroundColor DarkGray
        conda deactivate 2>$null
    }

    # Activate the virtual environment
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        .\.venv\Scripts\Activate.ps1
        Write-Host "Virtual environment activated." -ForegroundColor Green
    } else {
        Write-Warning "Could not find .venv\Scripts\Activate.ps1"
    }

    # Install the package in editable mode ONCE before launching tabs
    Write-Host "Running uv pip install..." -ForegroundColor Cyan
    uv pip install -e .
    
    Write-Host "Setup complete! Launching agents...`n" -ForegroundColor Green
}

function Start-ServiceTab {
    param([string]$Title, [string]$Command)
    
    $tabScript = @"
Write-Host 'Initializing $Title...' -ForegroundColor Cyan
try { conda deactivate 2>`$null } catch {}
if (Test-Path '.\.venv\Scripts\Activate.ps1') { .\.venv\Scripts\Activate.ps1 }
$Command
"@

    $bytes = [System.Text.Encoding]::Unicode.GetBytes($tabScript)
    $encodedCommand = [Convert]::ToBase64String($bytes)
    
    # Launch the new tab passing the encoded command
    $arguments = "-w", "0", "new-tab", "--title", "`"$Title`"", "-d", "`"$projectPath`"", "powershell", "-NoExit", "-EncodedCommand", $encodedCommand
    
    Start-Process wt.exe -ArgumentList $arguments
}

# =================================================================
# Main Execution
# =================================================================

# Prepare the environment and install package
Setup-LangGraph

Write-Host "Starting LangGraph Multi-Agent System in Windows Terminal Tabs..." -ForegroundColor Cyan

# Start the MCP Server
Write-Host "-> Starting MCP Server..." -ForegroundColor Yellow
$mcpCommand = "uv run -m a2a_mcp --run mcp-server --host localhost --port 10000 --transport streamable-http"
Start-ServiceTab -Title "MCP Server (Port 10000)" -Command $mcpCommand
Start-Sleep -Seconds 2

# Start the LangGraph Agents
Write-Host "-> Starting Invoice Agent..." -ForegroundColor Yellow
$invoiceCommand = "uv run -m a2a_mcp.agents --host localhost --port 8010 --agent-card agent_cards/invoice_info_agent.json"
Start-ServiceTab -Title "Invoice Agent (Port 8010)" -Command $invoiceCommand

Write-Host "-> Starting Music Agent..." -ForegroundColor Yellow
$musicCommand = "uv run -m a2a_mcp.agents --host localhost --port 8020 --agent-card agent_cards/music_catalog_agent.json"
Start-ServiceTab -Title "Music Agent (Port 8020)" -Command $musicCommand

Write-Host "-> Starting Planner Agent..." -ForegroundColor Yellow
$plannerCommand = "uv run -m a2a_mcp.agents --host localhost --port 8030 --agent-card agent_cards/langgraph_planner_agent.json"
Start-ServiceTab -Title "Planner Agent (Port 8030)" -Command $plannerCommand

Write-Host "-> Starting Orchestrator Agent..." -ForegroundColor Yellow
$orchestratorCommand = "uv run -m a2a_mcp.agents --host localhost --port 8040 --agent-card agent_cards/orchestrator_agent.json"
Start-ServiceTab -Title "Orchestrator Agent (Port 8040)" -Command $orchestratorCommand

# Start the ADK Agent
Write-Host "-> Starting Customer Service Agent..." -ForegroundColor Yellow
$CustomerServiceCommand = "uvicorn src.a2a_mcp.agents.customer_service_agent:app --port 8050"
Start-ServiceTab -Title "Customer Service Agent (Port 8050)" -Command $CustomerServiceCommand

Write-Host "-> Starting Refund Agent..." -ForegroundColor Yellow
$RefundCommand = "uvicorn src.a2a_mcp.agents.refund_agent:app --port 8060"
Start-ServiceTab -Title "Refund Agent (Port 8060)" -Command $RefundCommand

Write-Host "All services have been launched in separate windows!" -ForegroundColor Green