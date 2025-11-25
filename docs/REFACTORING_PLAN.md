# Car Demo System - Multi-Repository Refactoring Plan

## 📁 Proposed Repository Structure

### 1. Main Orchestration Repository
**Repo**: `car-demo-system` (current repo, refactored)
- Contains overall system documentation
- Docker compose files for all databases
- Cross-component integration scripts
- Quick-start scripts for the entire system
- Submodule references to all component repos

### 2. Component A - Frontend Applications
**Repo**: `car-demo-frontend`
```
car-demo-frontend/
|--- A1-car-user-app/          # React Native mobile app
|--- A2-rental-staff-app/      # React web app
|--- docker-compose.yml        # Optional: containerized frontends
|--- README.md                 # Frontend-specific setup
|--- .gitignore
`--- scripts/
    |--- build-all.sh
    `--- dev-start.sh
```

### 3. Component B - Backend Services & Databases
**Repo**: `car-demo-backend`
```
car-demo-backend/
|--- B1-web-server/           # Express.js API
|--- B2-iot-gateway/          # Node.js IoT gateway
|--- B3-realtime-database/    # MongoDB setup & queries
|--- B4-static-database/      # PostgreSQL setup & queries
|--- docker-compose.yml       # All backend databases
|--- README.md               # Backend-specific setup
|--- .gitignore
`--- scripts/
    |--- setup-databases.sh
    `--- start-services.sh
```

### 4. Component C - In-Car Systems
**Repo**: `car-demo-in-car`
```
car-demo-in-car/
|--- C1-cloud-communication/   # Python cloud comm
|--- C2-central-broker/        # Redis + Node.js broker
|--- C3-dashboard-ui/          # Future: React dashboard
|--- C4-climate-control/       # Future: Python climate
|--- C5-data-sensors/          # Python sensor simulators
|--- requirements.txt          # Combined Python deps
|--- docker-compose.yml        # Redis and other services
|--- README.md                # In-car systems setup
|--- .gitignore
`--- scripts/
    |--- setup-python.sh
    `--- start-simulators.sh
```

## 🔗 Inter-Repository Communication

### API Endpoints (Production Ready)
- **A1, A2** -> **B1**: `http://car-demo-backend.local:3001`
- **B1, B2** -> **B3, B4**: Internal database connections
- **All** -> **C2**: `http://car-demo-in-car.local:3003`

### Development Endpoints (localhost)
- **A1, A2** -> **B1**: `http://localhost:3001`
- **B1, B2** -> **B3**: `mongodb://localhost:27017`
- **B1, B2** -> **B4**: `postgresql://localhost:5432`
- **All** -> **C2**: `redis://localhost:6379`, `http://localhost:3003`

## 📋 Migration Benefits

### ✅ Advantages
1. **Independent Development**: Teams can work on components separately
2. **Focused CI/CD**: Each repo has its own build/test pipeline
3. **Technology Alignment**: Frontend (JS/React), Backend (Node.js), In-Car (Python)
4. **Scalable Deployment**: Deploy components independently
5. **Clear Ownership**: Each team owns their repository
6. **Version Management**: Independent versioning per component

### ⚠️ Considerations
1. **Integration Testing**: Need cross-repo testing strategy
2. **Dependency Management**: API versioning between components
3. **Setup Complexity**: More repos to clone and setup
4. **Documentation**: Must maintain API contracts between repos

## 🚀 Migration Strategy

### Phase 1: Repository Creation
1. Create 4 new repositories
2. Copy component code to respective repos
3. Set up individual build systems
4. Create component-specific documentation

### Phase 2: Integration Setup
1. Update API endpoints for cross-component communication
2. Create Docker compose files for easy local development
3. Set up environment variable management
4. Create integration testing framework

### Phase 3: Main Orchestration
1. Convert main repo to orchestration-only
2. Add git submodules for all components
3. Create master quick-start scripts
4. Set up development environment automation

## 🛠️ Repository Templates

Each repository will include:
- **README.md**: Component-specific setup and API docs
- **docker-compose.yml**: Local development environment
- **package.json/requirements.txt**: Dependencies
- **.gitignore**: Technology-specific ignores
- **.env.example**: Environment variable templates
- **scripts/**: Setup and development scripts
- **docs/**: API documentation and architecture

## 📦 Dependency Management

### Shared Configuration
- Common environment variables (Redis URLs, database connections)
- Shared Docker networks for local development
- Standardized port assignments
- API versioning strategy

### Technology Stacks
- **Frontend**: Node.js 16+, React, React Native, Expo
- **Backend**: Node.js 16+, Express.js, MongoDB, PostgreSQL
- **In-Car**: Python 3.8+, Redis, asyncio, Docker

## 🔄 Development Workflow

### Local Development
```bash
# Clone all repositories
git clone --recursive https://github.com/user/car-demo-system.git
cd car-demo-system

# Start all components
./scripts/dev-start-all.sh

# Or start individual components
cd frontend && ./scripts/dev-start.sh
cd backend && ./scripts/dev-start.sh
cd in-car && ./scripts/dev-start.sh
```

### Production Deployment
- Each repository has its own CI/CD pipeline
- Main repo orchestrates deployment via docker-compose
- Environment-specific configuration management
- Health checks and monitoring per component

This structure provides maximum flexibility while maintaining integration capabilities!