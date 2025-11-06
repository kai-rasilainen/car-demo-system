# Car Demo System - Main Orchestration

Main orchestration repository for the car demo system.

## Architecture

The system is split into focused repositories:

- **car-demo-frontend**: A1 (Mobile) + A2 (Web) applications
- **car-demo-backend**: B1-B4 backend services and databases
- **car-demo-in-car**: C1-C5 in-car systems and sensors
- **car-demo-system**: This orchestration repository

## Quick Start

### Clone All Repositories
```bash
git clone --recursive https://github.com/kai-rasilainen/car-demo-orchestration.git
cd car-demo-orchestration
./scripts/setup-all.sh
./scripts/start-all.sh
```

### Individual Components
```bash
# Backend only
git clone https://github.com/kai-rasilainen/car-demo-backend.git
cd car-demo-backend && ./scripts/dev-start.sh

# Frontend only  
git clone https://github.com/kai-rasilainen/car-demo-frontend.git
cd car-demo-frontend && ./scripts/dev-start.sh

# In-car only
git clone https://github.com/kai-rasilainen/car-demo-in-car.git
cd car-demo-in-car && ./scripts/start-all.sh
```

## Service URLs

- **A1 Mobile**: http://localhost:19006 (Expo)
- **A2 Web**: http://localhost:3000
- **B1 API**: http://localhost:3001
- **B2 IoT**: http://localhost:3002
- **C2 Broker**: http://localhost:3003

## Container Management

### Start Containers
```bash
# Start all database containers
./scripts/start-all.sh

# Or manually
docker compose up -d
```

### Stop Containers
```bash
# Stop containers only (preserves data)
./stop-all.sh

# Stop and remove volumes (deletes all data)
./stop-all.sh --volumes

# Stop and clean everything (containers + volumes + images)
./stop-all.sh --all
```
