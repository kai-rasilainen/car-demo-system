#!/bin/bash

echo "🚗 Car Demo System - Manual Testing Guide"
echo "=========================================="
echo ""

echo "1. HEALTH CHECKS:"
echo "curl http://localhost:3001/health    # B1 Web Server"
echo "curl http://localhost:3003/health    # C2 Central Broker"
echo "redis-cli ping                       # Redis"
echo ""

echo "2. DATA TESTING:"
echo "# Test cars: ABC-123, XYZ-789, DEF-456"
echo "curl http://localhost:3001/api/car/ABC-123"
echo "curl http://localhost:3001/api/car/XYZ-789"
echo "curl http://localhost:3001/api/car/DEF-456"
echo ""

echo "3. REAL-TIME DATA:"
echo "curl http://localhost:3003/api/cars"
echo "curl http://localhost:3003/api/car/ABC-123/data"
echo ""

echo "4. SYSTEM MONITORING:"
echo "ps aux | grep -E '(node|server\.js)' | grep -v grep"
echo "netstat -tulpn | grep -E ':(3001|3003|6379)'"
echo ""

echo "5. LOGS & DEBUG:"
echo "redis-cli monitor    # Watch Redis activity"
echo "tail -f /var/log/redis/redis-server.log    # Redis logs"
echo ""

echo "=========================================="
echo "🎯 NEXT STEPS TO COMPLETE SYSTEM:"
echo "1. Fix Docker permissions for databases"
echo "2. Start MongoDB & PostgreSQL"
echo "3. Start B2 IoT Gateway"
echo "4. Test frontend applications"
echo "=========================================="