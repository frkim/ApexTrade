# =============================================================================
# ApexTrade Initial Setup Script (Windows PowerShell)
# =============================================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "=============================================="
Write-Host "ApexTrade Initial Setup"
Write-Host "=============================================="
Write-Host ""

# Function to generate random secret
function New-Secret {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    return [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
}

# Check prerequisites
Write-Host "Checking prerequisites..."
Write-Host ""

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[X] Docker is not installed" -ForegroundColor Red
    Write-Host "    Please install Docker: https://docs.docker.com/get-docker/"
}

# Check Docker Compose
try {
    $composeVersion = docker compose version --short
    Write-Host "[OK] Docker Compose is installed: $composeVersion" -ForegroundColor Green
} catch {
    try {
        $composeVersion = docker-compose --version
        Write-Host "[OK] Docker Compose is installed: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "[X] Docker Compose is not installed" -ForegroundColor Red
        Write-Host "    Please install Docker Compose: https://docs.docker.com/compose/install/"
    }
}

Write-Host ""

# Create .env file
Write-Host "Setting up environment file..."
$CreateEnv = $false

if (Test-Path ".env") {
    Write-Host "[!] .env file already exists" -ForegroundColor Yellow
    $response = Read-Host "    Overwrite with new secrets? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        $CreateEnv = $true
    } else {
        Write-Host "    Keeping existing .env file"
    }
} else {
    $CreateEnv = $true
}

if ($CreateEnv) {
    Write-Host "Generating secrets..."
    $SecretKey = New-Secret
    $JwtSecretKey = New-Secret
    
    $envContent = Get-Content ".env.example"
    $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$SecretKey"
    $envContent = $envContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$JwtSecretKey"
    $envContent | Set-Content ".env"
    
    Write-Host "[OK] Created .env file with generated secrets" -ForegroundColor Green
}

Write-Host ""

# Create necessary directories
Write-Host "Creating directories..."
$directories = @(
    "backend\logs",
    "frontend\logs",
    "data\postgres",
    "data\timescale",
    "data\redis",
    "data\minio"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "[OK] Directories created" -ForegroundColor Green

Write-Host ""

# Pull Docker images
$response = Read-Host "Pull Docker images now? (Y/n)"
if ($response -ne "n" -and $response -ne "N") {
    Write-Host "Pulling Docker images (this may take a while)..."
    try {
        docker compose pull
    } catch {
        docker-compose pull
    }
    Write-Host "[OK] Images pulled" -ForegroundColor Green
} else {
    Write-Host "Skipping image pull"
}

Write-Host ""
Write-Host "=============================================="
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review and update .env file with your settings"
Write-Host "  2. Add your trading API keys (Alpaca, Polygon, etc.)"
Write-Host "  3. Start the development environment:"
Write-Host ""
Write-Host "     .\scripts\dev.ps1"
Write-Host ""
Write-Host "  4. Access the services:"
Write-Host "     - Frontend:  http://localhost:3000"
Write-Host "     - API:       http://localhost:8000"
Write-Host "     - API Docs:  http://localhost:8000/docs"
Write-Host ""
