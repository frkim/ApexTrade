# =============================================================================
# ApexTrade Development Start Script (Windows PowerShell)
# =============================================================================

param(
    [switch]$Attach,
    [switch]$Build,
    [switch]$Logs,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "=============================================="
Write-Host "ApexTrade Development Environment"
Write-Host "=============================================="
Write-Host ""

if ($Help) {
    Write-Host "Usage: .\dev.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Attach    Run in foreground (attached mode)"
    Write-Host "  -Build     Build images before starting"
    Write-Host "  -Logs      Follow logs after starting (detached mode only)"
    Write-Host "  -Help      Show this help message"
    exit 0
}

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..."
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file. Please update with your settings."
    } else {
        Write-Host "Error: .env.example not found" -ForegroundColor Red
        exit 1
    }
}

# Check for Docker
try {
    docker --version | Out-Null
} catch {
    Write-Host "Error: Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Determine docker-compose command
$DockerCompose = $null
try {
    docker compose version | Out-Null
    $DockerCompose = "docker compose"
} catch {
    try {
        docker-compose --version | Out-Null
        $DockerCompose = "docker-compose"
    } catch {
        Write-Host "Error: Docker Compose is not installed" -ForegroundColor Red
        exit 1
    }
}

# Build if requested
if ($Build) {
    Write-Host "Building containers..."
    if ($DockerCompose -eq "docker compose") {
        & docker compose build --parallel
    } else {
        & docker-compose build --parallel
    }
    Write-Host ""
}

# Start services
if (-not $Attach) {
    Write-Host "Starting services in detached mode..."
    if ($DockerCompose -eq "docker compose") {
        & docker compose up -d
    } else {
        & docker-compose up -d
    }
    
    Write-Host ""
    Write-Host "=============================================="
    Write-Host "Services Started Successfully!" -ForegroundColor Green
    Write-Host "=============================================="
    Write-Host ""
    Write-Host "Available services:"
    Write-Host "  - Frontend:     http://localhost:3000"
    Write-Host "  - API:          http://localhost:8000"
    Write-Host "  - API Docs:     http://localhost:8000/docs"
    Write-Host "  - Grafana:      http://localhost:3001 (admin/admin)"
    Write-Host "  - Prometheus:   http://localhost:9090"
    Write-Host "  - MinIO:        http://localhost:9001 (minioadmin/minioadmin)"
    Write-Host ""
    Write-Host "Useful commands:"
    Write-Host "  docker compose logs -f       # View all logs"
    Write-Host "  docker compose down          # Stop all services"
    Write-Host "  docker compose ps            # Check service status"
    Write-Host ""
    
    if ($Logs) {
        Write-Host "Following logs (Ctrl+C to exit)..."
        if ($DockerCompose -eq "docker compose") {
            & docker compose logs -f
        } else {
            & docker-compose logs -f
        }
    }
} else {
    Write-Host "Starting services in attached mode..."
    Write-Host "(Press Ctrl+C to stop)"
    Write-Host ""
    if ($DockerCompose -eq "docker compose") {
        & docker compose up
    } else {
        & docker-compose up
    }
}
