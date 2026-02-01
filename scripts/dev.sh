#!/bin/bash
# =============================================================================
# ApexTrade Development Start Script
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=============================================="
echo "ApexTrade Development Environment"
echo "=============================================="
echo ""

# Parse arguments
DETACHED=true
BUILD=false
LOGS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --attach|-a)
            DETACHED=false
            shift
            ;;
        --build|-b)
            BUILD=true
            shift
            ;;
        --logs|-l)
            LOGS=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -a, --attach   Run in foreground (attached mode)"
            echo "  -b, --build    Build images before starting"
            echo "  -l, --logs     Follow logs after starting (detached mode only)"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env file. Please update with your settings."
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Determine docker-compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Build if requested
if [ "$BUILD" = true ]; then
    echo "Building containers..."
    $DOCKER_COMPOSE build --parallel
    echo ""
fi

# Start services
if [ "$DETACHED" = true ]; then
    echo "Starting services in detached mode..."
    $DOCKER_COMPOSE up -d
    
    echo ""
    echo "=============================================="
    echo "Services Started Successfully!"
    echo "=============================================="
    echo ""
    echo "Available services:"
    echo "  - Frontend:     http://localhost:3000"
    echo "  - API:          http://localhost:8000"
    echo "  - API Docs:     http://localhost:8000/docs"
    echo "  - Grafana:      http://localhost:3001 (admin/admin)"
    echo "  - Prometheus:   http://localhost:9090"
    echo "  - MinIO:        http://localhost:9001 (minioadmin/minioadmin)"
    echo ""
    echo "Useful commands:"
    echo "  make logs       # View all logs"
    echo "  make logs-api   # View API logs"
    echo "  make down       # Stop all services"
    echo "  make status     # Check service status"
    echo ""
    
    if [ "$LOGS" = true ]; then
        echo "Following logs (Ctrl+C to exit)..."
        $DOCKER_COMPOSE logs -f
    fi
else
    echo "Starting services in attached mode..."
    echo "(Press Ctrl+C to stop)"
    echo ""
    $DOCKER_COMPOSE up
fi
