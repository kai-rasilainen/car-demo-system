# Swagger API Documentation

## Overview

All HTTP API components in the car demo system now have comprehensive Swagger/OpenAPI 3.0 documentation. The Swagger UI provides interactive API documentation with the ability to test endpoints directly from the browser.

## Components with Swagger Documentation

### 1. B1 Web Server (Port 3001)
**Swagger UI**: http://localhost:3001/api-docs

**Purpose**: REST API for car data retrieval and command sending

**Endpoints**:
- `GET /health` - Service health check
- `GET /api/car/:licensePlate` - Get current car data
- `POST /api/car/:licensePlate/command` - Send command to car
- `GET /api/cars` - List all cars from PostgreSQL database

**Tags**:
- Health
- Car Data
- Commands

### 2. B2 IoT Gateway (Port 3002)
**Swagger UI**: http://localhost:3002/api-docs

**Purpose**: IoT Gateway managing WebSocket connections and MQTT communication

**Endpoints**:
- `GET /health` - Health check with detailed component status
- `GET /api/connected-cars` - List currently connected cars via WebSocket
- `GET /api/car/:licensePlate/history` - Retrieve historical sensor data from MongoDB
- `POST /api/car/:licensePlate/command` - Send command via Redis and WebSocket

**Tags**:
- Health
- Car Data
- WebSocket

### 3. C2 Central Broker (Port 3003)
**Swagger UI**: http://localhost:3003/api-docs

**Purpose**: In-car central broker managing Redis pub/sub communication

**Endpoints**:
- `GET /health` - Health check with Redis connection info
- `GET /api/car/:licensePlate/data` - Get latest sensor data from Redis
- `GET /api/car/:licensePlate/sensors/:sensorType` - Get specific sensor data
- `POST /api/car/:licensePlate/command` - Send command via Redis pub/sub
- `GET /api/car/:licensePlate/commands` - Get command history
- `GET /api/cars` - List all active cars

**Tags**:
- Health
- Car Data
- Commands

## Components Without HTTP APIs

The following components do not have HTTP APIs and therefore no Swagger documentation:

### A1 Car User App
- Mobile application (React Native)
- Uses REST API calls to B1 Web Server
- No server-side HTTP API

### A2 Rental Staff App
- Web application (React)
- Consumes APIs from B1/B2
- No server-side HTTP API

### B3 Realtime Database (MongoDB)
- Database service only
- Accessed via MongoDB client libraries
- No HTTP API layer

### B4 Static Database (PostgreSQL)
- Database service only
- Accessed via PostgreSQL client libraries
- No HTTP API layer

### C1 Cloud Communication
- Python service communicating with B2 IoT Gateway
- WebSocket client, not server
- No HTTP API endpoints

### C5 Data Sensors
- Python sensor simulator
- Publishes data via Redis pub/sub
- No HTTP API endpoints

## Using Swagger UI

### Accessing Documentation
1. Start the system: `cd car-demo-system && ./scripts/start-complete.sh`
2. Navigate to the Swagger UI URL for each component
3. Explore endpoints organized by tags

### Testing Endpoints
1. Click on an endpoint to expand details
2. Click "Try it out"
3. Enter required parameters
4. Click "Execute"
5. View response below

### Example: Testing B1 Web Server

```bash
# Start the system
cd car-demo-system
./scripts/start-complete.sh

# Open browser to http://localhost:3001/api-docs

# Try the health check:
GET /health

# Try fetching car data:
GET /api/car/ABC-123

# Try sending a command:
POST /api/car/ABC-123/command
Body: { "command": "unlock" }
```

## API Documentation Features

Each endpoint includes:
- **Summary**: Brief description of the endpoint
- **Description**: Detailed explanation of functionality
- **Tags**: Category for organization
- **Parameters**: Path, query, and body parameters with types and examples
- **Request Body**: Schema for POST/PUT requests
- **Responses**: All possible response codes with schemas
- **Examples**: Sample values for testing

## OpenAPI Specification

All components use OpenAPI 3.0.0 specification with:
- Detailed schemas for request/response bodies
- Parameter validation
- Example values for testing
- Error response documentation
- Server URL configuration

## Dependencies

Swagger documentation is implemented using:
- `swagger-ui-express`: Serves Swagger UI interface
- `swagger-jsdoc`: Generates OpenAPI spec from JSDoc comments

Install in any Node.js component:
```bash
npm install swagger-ui-express swagger-jsdoc
```

## Future Enhancements

Potential improvements:
1. Add authentication/authorization documentation
2. Include WebSocket protocol documentation
3. Add request/response examples from actual usage
4. Create combined API gateway documentation
5. Add API versioning
6. Include rate limiting documentation
7. Add postman collection exports
