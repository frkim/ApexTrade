# =============================================================================
# ApexTrade Build Script (Windows PowerShell)
# =============================================================================

param(
    [switch]$NoCache,
    [switch]$NoParallel,
    [string]$Service = "",
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "=============================================="
Write-Host "ApexTrade Build Script"
Write-Host "=============================================="
Write-Host ""

if ($Help) {
    Write-Host "Usage: .\build.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -NoCache     Build without using cache"
    Write-Host "  -NoParallel  Build services sequentially"
    Write-Host "  -Service     Build specific service only"
    Write-Host "  -Help        Show this help message"
    exit 0
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

Write-Host "Using: $DockerCompose"
Write-Host ""

# Build arguments
$BuildArgs = @()
if (-not $NoParallel) {
    $BuildArgs += "--parallel"
}
if ($NoCache) {
    $BuildArgs += "--no-cache"
}

# Build
if ($Service) {
    Write-Host "Building service: $Service"
    if ($DockerCompose -eq "docker compose") {
        & docker compose build @BuildArgs $Service
    } else {
        & docker-compose build @BuildArgs $Service
    }
} else {
    Write-Host "Building all services..."
    if ($DockerCompose -eq "docker compose") {
        & docker compose build @BuildArgs
    } else {
        & docker-compose build @BuildArgs
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=============================================="
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "To start the services, run:"
Write-Host "  .\scripts\dev.ps1      # Development mode"
Write-Host "  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d  # Production"
