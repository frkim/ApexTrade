#!/bin/bash
# =============================================================================
# ApexTrade Initial Setup Script
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=============================================="
echo "ApexTrade Initial Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to generate random secret
generate_secret() {
    if command -v openssl &> /dev/null; then
        openssl rand -hex 32
    elif command -v python3 &> /dev/null; then
        python3 -c "import secrets; print(secrets.token_hex(32))"
    elif command -v python &> /dev/null; then
        python -c "import secrets; print(secrets.token_hex(32))"
    else
        # Fallback to /dev/urandom
        head -c 32 /dev/urandom | xxd -p | tr -d '\n'
    fi
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed: $(docker --version)"
else
    echo -e "${RED}✗${NC} Docker is not installed"
    echo "  Please install Docker: https://docs.docker.com/get-docker/"
fi

# Check Docker Compose
if docker compose version &> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose is installed: $(docker compose version --short)"
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is installed: $(docker-compose --version)"
else
    echo -e "${RED}✗${NC} Docker Compose is not installed"
    echo "  Please install Docker Compose: https://docs.docker.com/compose/install/"
fi

# Check Make
if command -v make &> /dev/null; then
    echo -e "${GREEN}✓${NC} Make is installed"
else
    echo -e "${YELLOW}⚠${NC} Make is not installed (optional, but recommended)"
fi

echo ""

# Create .env file
echo "Setting up environment file..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file already exists"
    read -p "  Overwrite with new secrets? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "  Keeping existing .env file"
    else
        CREATE_ENV=true
    fi
else
    CREATE_ENV=true
fi

if [ "$CREATE_ENV" = true ]; then
    echo "Generating secrets..."
    SECRET_KEY=$(generate_secret)
    JWT_SECRET_KEY=$(generate_secret)
    
    cp .env.example .env
    
    # Update secrets in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
        sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=${JWT_SECRET_KEY}/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
        sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=${JWT_SECRET_KEY}/" .env
    fi
    
    echo -e "${GREEN}✓${NC} Created .env file with generated secrets"
fi

echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p backend/logs
mkdir -p frontend/logs
mkdir -p data/postgres
mkdir -p data/timescale
mkdir -p data/redis
mkdir -p data/minio
echo -e "${GREEN}✓${NC} Directories created"

echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh 2>/dev/null || true
echo -e "${GREEN}✓${NC} Scripts are now executable"

echo ""

# Pull Docker images
read -p "Pull Docker images now? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Skipping image pull"
else
    echo "Pulling Docker images (this may take a while)..."
    if docker compose version &> /dev/null 2>&1; then
        docker compose pull
    else
        docker-compose pull
    fi
    echo -e "${GREEN}✓${NC} Images pulled"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Review and update .env file with your settings"
echo "  2. Add your trading API keys (Alpaca, Polygon, etc.)"
echo "  3. Start the development environment:"
echo ""
echo "     make dev          # or ./scripts/dev.sh"
echo ""
echo "  4. Access the services:"
echo "     - Frontend:  http://localhost:3000"
echo "     - API:       http://localhost:8000"
echo "     - API Docs:  http://localhost:8000/docs"
echo ""
