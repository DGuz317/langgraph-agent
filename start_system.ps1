# =================================================================
# LangGraph Multi-Agent System Launcher (Tabbed Version)
# =================================================================

$projectPath = "C:\Users\nvdung1\Desktop\langraph_agent"

# =================================================================
# Custom Commands / Setup Environment (Runs ONCE in main window)
# =================================================================

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

# =================================================================
# Tab Launcher Function (Using Encoded Commands for Reliability)
# =================================================================

function Start-ServiceTab {
    param([string]$Title, [string]$Command)
    
    # 1. Write the exact multi-line script we want the new tab to execute
    $tabScript = @"
Write-Host 'Initializing $Title...' -ForegroundColor Cyan
try { conda deactivate 2>`$null } catch {}
if (Test-Path '.\.venv\Scripts\Activate.ps1') { .\.venv\Scripts\Activate.ps1 }
$Command
"@

    # 2. Encode the script to Base64 to bypass all Windows Terminal quoting issues
    $bytes = [System.Text.Encoding]::Unicode.GetBytes($tabScript)
    $encodedCommand = [Convert]::ToBase64String($bytes)
    
    # 3. Launch the new tab passing the encoded command
    $arguments = "-w", "0", "new-tab", "--title", "`"$Title`"", "-d", "`"$projectPath`"", "powershell", "-NoExit", "-EncodedCommand", $encodedCommand
    
    Start-Process wt.exe -ArgumentList $arguments
}

# =================================================================
# Main Execution
# =================================================================

# 1. Prepare the environment and install package
Setup-LangGraph

Write-Host "Starting LangGraph Multi-Agent System in Windows Terminal Tabs..." -ForegroundColor Cyan

# 2. Start the MCP Server
Write-Host "-> Starting MCP Server..." -ForegroundColor Yellow
$mcpCommand = "uv run -m src.a2a_mcp.mcp.server --host localhost --port 10000 --transport streamable-http"
Start-ServiceTab -Title "MCP Server (Port 10000)" -Command $mcpCommand

# Give the MCP server a quick second to spin up
Start-Sleep -Seconds 2

# 3. Start the Agents
Write-Host "-> Starting Invoice Agent..." -ForegroundColor Yellow
$invoiceCommand = "uv run -m a2a_mcp.agents --host localhost --port 8010 --agent-card agent_cards/invoice_info_agent.json"
Start-ServiceTab -Title "Invoice Agent (Port 8010)" -Command $invoiceCommand

Write-Host "-> Starting Music Agent..." -ForegroundColor Yellow
$musicCommand = "uv run -m a2a_mcp.agents --host localhost --port 8020 --agent-card agent_cards/music_catalog_agent.json"
Start-ServiceTab -Title "Music Agent (Port 8020)" -Command $musicCommand

Write-Host "-> Starting Orchestrator Agent..." -ForegroundColor Yellow
$orchestratorCommand = "uv run -m a2a_mcp.agents --host localhost --port 8040 --agent-card agent_cards/orchestrator_agent.json"
Start-ServiceTab -Title "Orchestrator Agent (Port 8040)" -Command $orchestratorCommand

Write-Host "-> Starting Customer Service Agent..." -ForegroundColor Yellow
$CustomerServiceCommand = "uvicorn src.a2a_mcp.agents.customer_service_agent:app --port 8050"
Start-ServiceTab -Title "Customer Service Agent (Port 8050)" -Command $CustomerServiceCommand

Write-Host "All services have been launched successfully!" -ForegroundColor Green