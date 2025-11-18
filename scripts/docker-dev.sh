#!/bin/bash
# Start all services in development mode

echo "🛠️  Starting Car Demo System (Development Mode)"
echo "================================================"

# Build and start all services with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo ""
echo "🌐 Development Access URLs:"
echo "  • Staff Web App:    http://localhost:3000 (Hot reload enabled)"
echo "  • REST API:         http://localhost:3001/api (Nodemon enabled)"
echo "  • IoT Gateway:      http://localhost:3002 (Nodemon enabled)"
echo "  • MongoDB:          mongodb://localhost:27017"
echo "  • PostgreSQL:       postgresql://localhost:5432"
echo "  • Redis:            redis://localhost:6379"

echo ""
echo "📋 View logs: docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f [service_name]"
echo "🛑 Stop all:  docker-compose -f docker-compose.yml -f docker-compose.dev.yml down"