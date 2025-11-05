#!/bin/bash

echo "🚗 Car Demo System Testing Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not responding"
        return 1
    fi
}

# Function to check if port is open
check_port() {
    local port=$1
    local name=$2
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $name (port $port) is listening"
        return 0
    else
        echo -e "${RED}✗${NC} $name (port $port) is not listening"
        return 1
    fi
}

echo -e "\n${YELLOW}1. Checking Prerequisites:${NC}"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not installed')"
echo "Redis: $(redis-cli ping 2>/dev/null || echo 'Not running')"

echo -e "\n${YELLOW}2. Checking Service Ports:${NC}"
check_port 3001 "B1 Web Server"
check_port 3002 "B2 IoT Gateway"
check_port 3003 "C2 Central Broker"
check_port 6379 "Redis"

echo -e "\n${YELLOW}3. Testing Service Health:${NC}"
check_service "http://localhost:3001/health" "B1 Web Server API"
check_service "http://localhost:3002/health" "B2 IoT Gateway"
check_service "http://localhost:3003/health" "C2 Central Broker"

echo -e "\n${YELLOW}4. Testing Data Endpoints:${NC}"
check_service "http://localhost:3003/api/cars" "C2 Car Data"
check_service "http://localhost:3001/api/car/ABC-123" "B1 Car API"

echo -e "\n${YELLOW}5. Quick Data Test:${NC}"
echo "Testing Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is responding"
    
    # Test basic Redis operations
    redis-cli set test-key "test-value" > /dev/null
    if [ "$(redis-cli get test-key)" = "test-value" ]; then
        echo -e "${GREEN}✓${NC} Redis read/write working"
        redis-cli del test-key > /dev/null
    else
        echo -e "${RED}✗${NC} Redis read/write failed"
    fi
else
    echo -e "${RED}✗${NC} Redis not responding"
fi

echo -e "\n${YELLOW}6. System Status Summary:${NC}"
echo "=================================="
echo "Run individual components:"
echo "1. C2 Broker: cd car-demo-system/car-demo-in-car/C2-central-broker && node server.js"
echo "2. B2 IoT:    cd car-demo-system/car-demo-backend/B2-iot-gateway && node server.js"
echo "3. B1 API:    cd car-demo-system/car-demo-backend/B1-web-server && node server.js"
echo ""
echo "Test endpoints:"
echo "- http://localhost:3003/health"
echo "- http://localhost:3003/api/cars"
echo "- curl -X POST http://localhost:3003/api/data -H 'Content-Type: application/json' -d '{\"licensePlate\":\"TEST-001\",\"indoorTemp\":22}'"