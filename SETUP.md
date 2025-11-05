# Car Demo System - Complete Setup Guide

This guide walks you through setting up all components of the car demo system.

## Quick Start (Docker Method)

### 1. Start Databases
```bash
# Start MongoDB (B3)
cd component-B/B3-realtime-database
docker-compose up -d

# Start PostgreSQL (B4)  
cd ../B4-static-database
docker-compose up -d

# Start Redis (C2)
cd ../../component-C/C2-central-broker
docker-compose up -d
```

### 2. Install Dependencies
```bash
# B1 - Web server
cd ../../component-B/B1-web-server
npm install

# B2 - IoT gateway
cd ../B2-iot-gateway
npm install

# C2 - Central broker
cd ../../component-C/C2-central-broker
npm install

# Python components
cd ../C1-cloud-communication
pip install -r requirements.txt

cd ../C5-data-sensors
pip install -r requirements.txt
```

### 3. Start Core Services (in separate terminals)

Terminal 1 - Central Broker:
```bash
cd component-C/C2-central-broker
npm start
```

Terminal 2 - Data Sensors:
```bash
cd component-C/C5-data-sensors
python sensor_simulator.py
```

Terminal 3 - IoT Gateway:
```bash
cd component-B/B2-iot-gateway
npm start
```

Terminal 4 - Web Server:
```bash
cd component-B/B1-web-server
npm start
```

Terminal 5 - Cloud Communication:
```bash
cd component-C/C1-cloud-communication
python cloud_communicator.py
```

### 4. Start Frontend Apps

Terminal 6 - User Mobile App:
```bash
cd component-A/A1-car-user-app
npm install
npm start
```

Terminal 7 - Staff Web App:
```bash
cd component-A/A2-rental-staff-app
npm install
npm start
```

## Testing the System

### 1. Check System Health
```bash
# Check databases
curl http://localhost:3003/health  # C2 Redis
curl http://localhost:3001/health  # B1 API
curl http://localhost:3002/health  # B2 IoT Gateway

# Check data flow
curl http://localhost:3003/api/cars  # All cars in C2
curl http://localhost:3001/api/car/ABC-123  # Car data via B1
```

### 2. Test Mobile App (A1)
- Open Expo Go app and scan QR code
- Enter license plate: ABC-123
- View real-time temperature data

### 3. Test Staff App (A2)
- Open http://localhost:3000
- Enter license plate: ABC-123
- View dashboard and send commands

### 4. Test Data Flow
```bash
# Monitor Redis activity
redis-cli monitor

# View car data
curl http://localhost:3003/api/car/ABC-123/data

# Send command
curl -X POST http://localhost:3001/api/car/ABC-123/command \
  -H "Content-Type: application/json" \
  -d '{"command": "start_heating"}'
```

## Component Startup Order

1. **Databases** (B3, B4, C2 Redis)
2. **C2** - Central broker
3. **C5** - Data sensors  
4. **B2** - IoT gateway
5. **B1** - Web server
6. **C1** - Cloud communication
7. **A1, A2** - Frontend apps

## Common Issues

### Redis Connection Error
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis manually
docker run -d -p 6379:6379 redis:alpine
```

### Database Connection Error
```bash
# Check MongoDB
docker ps | grep mongo
cd component-B/B3-realtime-database && docker-compose up -d

# Check PostgreSQL  
docker ps | grep postgres
cd component-B/B4-static-database && docker-compose up -d
```

### Port Conflicts
Default ports used:
- 3001: B1 Web Server
- 3002: B2 IoT Gateway  
- 3003: C2 Central Broker
- 3000: A2 Staff Web App
- 5432: PostgreSQL (B4)
- 27017: MongoDB (B3)
- 6379: Redis (C2)
- 8080: B2 WebSocket
- 8888: C1 Mock Cloud Server

## Test Data

The system includes test cars:
- **ABC-123**: John Doe, Toyota Camry 2022
- **XYZ-789**: Jane Smith, Honda Civic 2021  
- **DEF-456**: Mike Johnson, Ford Focus 2023

## Monitoring

### View Logs
```bash
# Component logs
tail -f /var/log/car-demo/*.log

# Docker logs
docker-compose logs -f mongodb
docker-compose logs -f postgres
docker-compose logs -f redis
```

### System Status
```bash
# Check all services
curl http://localhost:3001/health && echo
curl http://localhost:3002/health && echo  
curl http://localhost:3003/health && echo
```

## Development Mode

For development with auto-reload:

```bash
# Backend services
npm run dev  # Instead of npm start

# Python services  
# Use file watchers or run manually
```

## Production Deployment

See individual component README files for production setup:
- Environment variables
- Database configurations
- SSL/TLS setup
- Load balancing
- Monitoring and logging