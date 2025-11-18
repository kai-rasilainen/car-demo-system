#!/bin/bash
# Stop and cleanup Docker containers and images

echo "🧹 Cleaning up Car Demo System Docker environment"
echo "================================================="

# Stop all services
echo "🛑 Stopping all services..."
docker-compose down

# Remove all containers (if any are stuck)
echo "🗑️  Removing containers..."
docker-compose rm -f

# Remove images (optional - uncomment if needed)
# echo "🗑️  Removing images..."
# docker-compose down --rmi all

# Remove volumes (optional - uncomment to reset all data)
# echo "🗑️  Removing volumes (this will DELETE ALL DATA)..."
# docker-compose down --volumes

# Prune unused Docker resources
echo "🧹 Cleaning up unused Docker resources..."
docker system prune -f

echo "✅ Cleanup complete!"
echo ""
echo "🚀 To restart: ./scripts/docker-start.sh"
echo "🛠️  For development: ./scripts/docker-dev.sh"