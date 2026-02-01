#!/bin/bash
# =============================================================================
# ApexTrade Build Script
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=============================================="
echo "ApexTrade Build Script"
echo "=============================================="
echo ""

# Parse arguments
NO_CACHE=""
PARALLEL="--parallel"
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --no-parallel)
            PARALLEL=""
            shift
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --no-cache     Build without using cache"
            echo "  --no-parallel  Build services sequentially"
            echo "  --service NAME Build specific service only"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Determine docker-compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "Using: $DOCKER_COMPOSE"
echo ""

# Build
if [ -n "$SERVICE" ]; then
    echo "Building service: $SERVICE"
    $DOCKER_COMPOSE build $PARALLEL $NO_CACHE "$SERVICE"
else
    echo "Building all services..."
    $DOCKER_COMPOSE build $PARALLEL $NO_CACHE
fi

echo ""
echo "=============================================="
echo "Build completed successfully!"
echo "=============================================="
echo ""
echo "To start the services, run:"
echo "  make dev        # Development mode"
echo "  make prod       # Production mode"
