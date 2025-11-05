#!/bin/bash

echo "🚗 Car Demo System - Complete Testing with Python venv"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}1. PYTHON VIRTUAL ENVIRONMENT SETUP:${NC}"
if [ -d "car-demo-venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    source car-demo-venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment activated"
    echo "Python: $(python --version)"
    echo "Location: $(which python)"
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    echo "Run: python3 -m venv car-demo-venv"
    exit 1
fi

echo -e "\n${BLUE}2. INSTALLED PYTHON PACKAGES:${NC}"
pip list --format=table | grep -E "(redis|aiohttp|python-dotenv)"

echo -e "\n${BLUE}3. SYSTEM STATUS CHECK:${NC}"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "Redis: $(redis-cli ping 2>/dev/null || echo 'Not running')"

echo -e "\n${BLUE}4. SERVICE HEALTH CHECKS:${NC}"
if curl -s -f "http://localhost:3001/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} B1 Web Server (port 3001)"
else
    echo -e "${RED}✗${NC} B1 Web Server (port 3001)"
fi

if curl -s -f "http://localhost:3003/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} C2 Central Broker (port 3003)"
else
    echo -e "${RED}✗${NC} C2 Central Broker (port 3003)"
fi

echo -e "\n${BLUE}5. DATA TESTING:${NC}"
echo "Available cars in system:"
curl -s "http://localhost:3003/api/cars" | jq -r '.[] | "  - \(.licensePlate): \(.indoorTemp)°C indoor, \(.outdoorTemp)°C outdoor"' 2>/dev/null || echo "No data available"

echo -e "\n${BLUE}6. PYTHON COMPONENT TESTING:${NC}"
echo "Testing C1 Cloud Communication (will run for 10 seconds)..."
timeout 10 python car-demo-in-car/C1-cloud-communication/test_c2_simulator.py 2>/dev/null &
PID=$!
sleep 12
if kill -0 $PID 2>/dev/null; then
    kill $PID 2>/dev/null
fi

echo -e "\n${YELLOW}Updated car data:${NC}"
curl -s "http://localhost:3003/api/cars" | jq -r '.[] | "  - \(.licensePlate): \(.indoorTemp)°C indoor, \(.outdoorTemp)°C outdoor, Updated: \(.timestamp)"' 2>/dev/null || echo "No updated data"

echo -e "\n${BLUE}7. REDIS DATA VERIFICATION:${NC}"
echo "Redis keys count: $(redis-cli keys "*" | wc -l)"
echo "Sample keys:"
redis-cli keys "*" | head -5

echo -e "\n${BLUE}8. TESTING COMMANDS:${NC}"
echo "=================================="
echo "🔧 MANUAL TESTING:"
echo "curl http://localhost:3001/api/car/ABC-123"
echo "curl http://localhost:3003/api/car/XYZ-789/data"
echo "curl http://localhost:3003/health"
echo ""
echo "🐍 PYTHON COMPONENTS:"
echo "source car-demo-venv/bin/activate"
echo "cd car-demo-in-car/C1-cloud-communication && python cloud_communicator.py"
echo "cd car-demo-in-car/C5-data-sensors && python sensor_simulator.py"
echo ""
echo "📊 MONITORING:"
echo "redis-cli monitor    # Watch real-time Redis activity"
echo "redis-cli keys '*'   # List all stored keys"
echo "=================================="

echo -e "\n${GREEN}🎉 System testing complete!${NC}"