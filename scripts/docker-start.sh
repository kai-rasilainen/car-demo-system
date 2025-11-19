#!/bin/bash
# Start all services in production mode

echo "🚀 Starting Car Demo System (Production Mode)"
echo "================================================"

# Build and start all services
docker-compose up --build -d

echo ""
echo "[OK] Services starting..."
echo ""
echo "[INFO] Service Status:"
docker-compose ps

echo ""
echo "🌐 Access URLs:"
echo "  • Staff Web App:    http://localhost:3000"
echo "  • REST API:         http://localhost:3001/api"
echo "  • IoT Gateway:      http://localhost:3002"
echo "  • MongoDB:          mongodb://localhost:27017"
echo "  • PostgreSQL:       postgresql://localhost:5432"
echo "  • Redis:            redis://localhost:6379"

echo ""
echo "📋 View logs: docker-compose logs -f [service_name]"
echo "🛑 Stop all:  docker-compose down"