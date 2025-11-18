# Docker Containerization Guide

## Overview

The Car Demo System is now **fully containerized** using Docker and Docker Compose. All application components run in isolated containers with proper networking, health checks, and environment management.

## Containerized Components

### ✅ **Frontend Services**
- **A2-rental-staff-app**: React web application served via Nginx
  - Port: `3000:80`
  - Multi-stage build (Node.js build + Nginx production)
  - Health checks and security headers

### ✅ **Backend Services**  
- **B1-web-server**: Node.js REST API server
  - Port: `3001:3001`
  - Express.js with MongoDB/PostgreSQL/Redis connections
  
- **B2-iot-gateway**: Node.js WebSocket/IoT gateway
  - Port: `3002:3002`
  - Real-time communication with in-car systems

### ✅ **Database Services**
- **MongoDB**: Real-time data storage
  - Port: `27017:27017`
  - Pre-configured with init scripts
  
- **PostgreSQL**: Transactional data storage  
  - Port: `5432:5432`
  - Pre-configured with init scripts
  
- **Redis**: Message broker and caching
  - Port: `6379:6379`
  - Persistent data with append-only file

### ✅ **In-Car System Services**
- **C1-cloud-communication**: Python cloud integration
  - No external port (internal network only)
  - Connects to IoT gateway and Redis
  
- **C5-data-sensors**: Python sensor simulation
  - No external port (internal network only)
  - Publishes sensor data to Redis

## Quick Start

### Production Mode
```bash
# Start all services
./scripts/docker-start.sh

# View status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down
```

### Development Mode
```bash
# Start with hot reload and volume mounts
./scripts/docker-dev.sh

# Stop development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

### Cleanup
```bash
# Clean up containers and unused resources
./scripts/docker-cleanup.sh
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: car-network             │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer:                                            │
│  ┌─────────────────┐                                        │
│  │ rental-staff-app│ :3000 (Nginx + React)                 │
│  └─────────────────┘                                        │
├─────────────────────────────────────────────────────────────┤
│  Backend Layer:                                             │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ web-server  │  │ iot-gateway │                          │
│  │    :3001    │  │    :3002    │                          │
│  └─────────────┘  └─────────────┘                          │
├─────────────────────────────────────────────────────────────┤
│  Data Layer:                                                │
│  ┌─────────┐ ┌────────────┐ ┌─────────┐                    │
│  │ mongodb │ │ postgresql │ │  redis  │                    │
│  │  :27017 │ │   :5432    │ │  :6379  │                    │
│  └─────────┘ └────────────┘ └─────────┘                    │
├─────────────────────────────────────────────────────────────┤
│  In-Car Layer:                                              │
│  ┌───────────────────┐ ┌─────────────────┐                 │
│  │ cloud-communication│ │  data-sensors   │                 │
│  │    (internal)     │ │   (internal)    │                 │
│  └───────────────────┘ └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Environment Configuration

### Production Environment Variables
- `NODE_ENV=production`
- Database connection strings with container hostnames
- Service-to-service communication via internal network

### Development Environment Variables  
- `NODE_ENV=development`
- Hot reload enabled with volume mounts
- Debug logging enabled for Python services

## Health Checks

All services include health checks:
- **HTTP services**: HTTP GET to health endpoints
- **Python services**: Redis connection validation
- **React app**: Nginx status check
- **Databases**: Built-in container health checks

## Security Features

- **Non-root users**: All containers run with dedicated non-root users
- **Network isolation**: Services communicate only via internal Docker network
- **Security headers**: Nginx configured with security headers
- **Minimal images**: Alpine-based images where possible

## File Structure

```
├── docker-compose.yml              # Main production configuration
├── docker-compose.dev.yml          # Development overrides
├── scripts/
│   ├── docker-start.sh             # Start production environment
│   ├── docker-dev.sh               # Start development environment
│   └── docker-cleanup.sh           # Cleanup script
├── A-car-demo-frontend/A2-rental-staff-app/
│   ├── Dockerfile                  # React app container
│   ├── nginx.conf                  # Nginx configuration
│   └── .dockerignore
├── B-car-demo-backend/
│   ├── B1-web-server/
│   │   ├── Dockerfile              # REST API container
│   │   └── .dockerignore
│   └── B2-iot-gateway/
│       ├── Dockerfile              # IoT gateway container
│       └── .dockerignore
└── C-car-demo-in-car/
    ├── C1-cloud-communication/
    │   ├── Dockerfile              # Cloud comm container
    │   └── .dockerignore
    └── C5-data-sensors/
        ├── Dockerfile              # Sensors container
        └── .dockerignore
```

## AI Agent Integration

The containerized system fully supports the AI Agent Coordinator:

- All agents (A1, A2, B1-B4, C1-C5) now have their corresponding containerized services
- Agent coordination works across the containerized network
- Generated code examples reflect the containerized architecture
- Jenkins pipeline can build and test containerized components

## Benefits

1. **Consistency**: Identical environments across development, testing, and production
2. **Isolation**: Each service runs in its own container with defined dependencies
3. **Scalability**: Easy to scale individual services with Docker Swarm/Kubernetes
4. **CI/CD Ready**: Jenkins can build, test, and deploy containerized services
5. **Development Experience**: Hot reload and volume mounts for rapid development
6. **Health Monitoring**: Built-in health checks for all services
7. **Security**: Non-root users and network isolation

## Next Steps

- Configure container orchestration (Docker Swarm or Kubernetes)
- Set up container registry for image distribution  
- Add monitoring and logging aggregation
- Configure automated backup for persistent volumes
- Implement container security scanning in CI/CD