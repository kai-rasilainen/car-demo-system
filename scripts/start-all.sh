#!/bin/bash
set -e

echo "Starting complete car demo system..."

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Start databases
echo "Starting databases..."
$DOCKER_COMPOSE up -d
sleep 10

echo "🚀 Databases started! Now start individual components:"
echo ""
echo "Backend:"
echo "  cd B-car-demo-backend && ./scripts/dev-start.sh"
echo ""
echo "In-Car:"
echo "  cd C-car-demo-in-car && ./scripts/start-all.sh"
echo ""
echo "Frontend:"
echo "  cd A-car-demo-frontend && ./scripts/dev-start.sh"
