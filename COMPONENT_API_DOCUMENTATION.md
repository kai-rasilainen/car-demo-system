# Car Demo System - Component API Documentation

## Overview

This document describes the APIs and communication protocols between all components in the Car Demo System.

## Architecture Diagram

```
┌─────────────────┐
│  A1 Car User    │ (React Native Mobile App)
│     App         │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐     ┌─────────────────┐
│  A2 Rental      │────►│  B1 Web Server  │
│   Staff App     │     │    (Port 3001)  │
└─────────────────┘     └────────┬────────┘
        HTTP/REST                │
                                 │ MongoDB  PostgreSQL  Redis
                    ┌────────────┼────────────┼──────────┤
                    │            │            │          │
              ┌─────▼─────┐ ┌───▼────┐ ┌────▼────┐ ┌──▼────┐
              │ B2 IoT    │ │   B3   │ │   B4    │ │  C2   │
              │  Gateway  │ │ MongoDB│ │PostgreSQL│ │ Redis │
              │(Port 3002)│ │(27017) │ │  (5432) │ │(6379) │
              └─────┬─────┘ └────────┘ └─────────┘ └───┬───┘
                    │                                   │
              WebSocket                           Pub/Sub
              (Port 8081)                              │
                    │                                   │
              ┌─────▼─────────────────────────────────▼─────┐
              │         In-Car Components                    │
              │  C1 Cloud Comm  │  C5 Data Sensors          │
              └──────────────────────────────────────────────┘
```

---

## 1. Frontend to Backend Communication

### A2 Rental Staff App → B1 Web Server

**Base URL:** `http://localhost:3001`

#### Get Car Data
```http
GET /api/car/{licensePlate}
```

**Request:**
- Path Parameter: `licensePlate` (string) - e.g., "ABC-123"

**Response 200:**
```json
{
  "licensePlate": "ABC-123",
  "owner": "John Doe",
  "lastService": "2024-10-15",
  "indoorTemp": 23.5,
  "outdoorTemp": 14.2,
  "gps": {
    "lat": 60.1699,
    "lng": 24.9384
  },
  "lastUpdated": "2025-11-07T06:49:35.014Z"
}
```

**Response 404:**
```json
{
  "error": "Car not found"
}
```

---

#### Send Command to Car
```http
POST /api/car/{licensePlate}/command
Content-Type: application/json
```

**Request:**
```json
{
  "command": "start_ac"
}
```

**Available Commands:**
- `start_ac` - Start air conditioning
- `stop_ac` - Stop air conditioning
- `lock_doors` - Lock all doors
- `unlock_doors` - Unlock all doors
- `start_engine` - Start engine remotely
- `stop_engine` - Stop engine

**Response 200:**
```json
{
  "message": "Command sent successfully",
  "command": "start_ac",
  "licensePlate": "ABC-123"
}
```

---

#### Get All Cars (List)
```http
GET /api/cars
```

**Response 200:**
```json
[
  {
    "licensePlate": "ABC-123",
    "owner": "John Doe",
    "lastService": "2024-10-15"
  },
  {
    "licensePlate": "XYZ-789",
    "owner": "Jane Smith",
    "lastService": "2024-11-01"
  }
]
```

---

#### Health Check
```http
GET /health
```

**Response 200:**
```json
{
  "server": "ok",
  "mongodb": "connected",
  "postgresql": "connected",
  "redis": "connected",
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

---

## 2. Backend Component Communication

### B1 Web Server → B3 MongoDB

**Connection:** `mongodb://admin:password@localhost:27017`
**Database:** `cardata`
**Collection:** `car_data`

#### Read Real-time Car Data
```javascript
db.collection('car_data').findOne(
  { licensePlate: "ABC-123" },
  { sort: { timestamp: -1 } }
)
```

**Document Structure:**
```json
{
  "_id": "ObjectId",
  "licensePlate": "ABC-123",
  "indoorTemp": 23.5,
  "outdoorTemp": 14.2,
  "gps": {
    "lat": 60.1699,
    "lng": 24.9384
  },
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

---

### B1 Web Server → B4 PostgreSQL

**Connection:** `postgresql://postgres:password@localhost:5432/carinfo`

#### Get Static Car Information
```sql
SELECT * FROM cars WHERE license_plate = $1
```

**Table Structure:**
```
cars (
  id SERIAL PRIMARY KEY,
  license_plate VARCHAR(20) UNIQUE NOT NULL,
  owner_name VARCHAR(255) NOT NULL,
  owner_phone VARCHAR(20),
  owner_email VARCHAR(255),
  make VARCHAR(100) NOT NULL,
  model VARCHAR(100) NOT NULL,
  year INTEGER NOT NULL,
  color VARCHAR(50),
  vin VARCHAR(17) UNIQUE,
  last_service DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

---

### B1 Web Server → C2 Redis (Command Publishing)

**Connection:** `redis://localhost:6379`

#### Publish Command to Car
```javascript
redisClient.publish(
  `car:${licensePlate}:commands`,
  JSON.stringify({
    licensePlate: "ABC-123",
    command: "start_ac",
    timestamp: "2025-11-07T08:00:00.000Z"
  })
)
```

**Channel Pattern:** `car:{licensePlate}:commands`

---

## 3. In-Car Component Communication

### C5 Data Sensors → B2 IoT Gateway

**Protocol:** WebSocket
**Endpoint:** `ws://localhost:8081`

#### Send Sensor Data
```json
{
  "type": "sensor_data",
  "licensePlate": "ABC-123",
  "indoorTemp": 23.5,
  "outdoorTemp": 14.2,
  "gps": {
    "lat": 60.1699,
    "lng": 24.9384
  },
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

**Alternative: HTTP POST**
```http
POST http://localhost:3002/api/car-data
Content-Type: application/json
```

---

### B2 IoT Gateway → B3 MongoDB

**Connection:** `mongodb://admin:password@localhost:27017`
**Database:** `cardata`
**Collection:** `car_data`

#### Store Sensor Data
```javascript
db.collection('car_data').insertOne({
  licensePlate: "ABC-123",
  indoorTemp: 23.5,
  outdoorTemp: 14.2,
  gps: { lat: 60.1699, lng: 24.9384 },
  timestamp: new Date()
})
```

---

### B2 IoT Gateway → C2 Redis

**Connection:** `redis://localhost:6379`

#### Subscribe to Commands
```javascript
redisClient.subscribe('car:*:commands', (message, channel) => {
  const command = JSON.parse(message);
  // Forward to car via WebSocket
})
```

#### Publish Real-time Updates
```javascript
redisClient.publish('car:updates', JSON.stringify({
  licensePlate: "ABC-123",
  status: "data_received",
  timestamp: new Date()
}))
```

---

### C1 Cloud Communication → C2 Redis

**Connection:** `redis://localhost:6379`

#### Subscribe to Commands for Specific Car
```python
pubsub = redis_client.pubsub()
pubsub.subscribe(f'car:{license_plate}:commands')

for message in pubsub.listen():
    if message['type'] == 'message':
        command_data = json.loads(message['data'])
        # Execute command on car
```

#### Publish Status Updates
```python
redis_client.publish(
    f'car:{license_plate}:status',
    json.dumps({
        'licensePlate': license_plate,
        'status': 'command_executed',
        'command': 'start_ac',
        'timestamp': datetime.now().isoformat()
    })
)
```

---

## 4. C2 Central Broker APIs

### C2 Central Broker (Node.js/Express + Redis)

**Base URL:** `http://localhost:3003`

#### Health Check
```http
GET /health
```

**Response 200:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "uptime": 206.168681252,
  "timestamp": "2025-11-07T08:49:38.959Z",
  "redis_info": {
    "version": "7.4.7",
    "connected_clients": 3,
    "used_memory": "1048576"
  }
}
```

---

## 5. Message Formats and Protocols

### Redis Pub/Sub Channels

| Channel Pattern | Publisher | Subscriber | Purpose |
|----------------|-----------|------------|---------|
| `car:{plate}:commands` | B1 Web Server | C1 Cloud Comm | Send commands to cars |
| `car:{plate}:status` | C1 Cloud Comm | B2 IoT Gateway | Car status updates |
| `car:updates` | B2 IoT Gateway | Dashboard | Real-time data updates |
| `sensor:data:{plate}` | C5 Sensors | B2 IoT Gateway | Raw sensor readings |

---

### WebSocket Messages (Port 8081)

#### Client → Server (Sensor Data)
```json
{
  "type": "sensor_data",
  "licensePlate": "ABC-123",
  "data": {
    "indoorTemp": 23.5,
    "outdoorTemp": 14.2,
    "gps": { "lat": 60.1699, "lng": 24.9384 }
  },
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

#### Server → Client (Command)
```json
{
  "type": "command",
  "licensePlate": "ABC-123",
  "command": "start_ac",
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

#### Server → Client (Acknowledgment)
```json
{
  "type": "ack",
  "messageId": "msg-12345",
  "status": "received"
}
```

---

## 6. Authentication & Security

### Current Implementation
- **No authentication** - Development/demo environment
- **CORS enabled** - All origins allowed
- **Plain text passwords** - In `.env` files (gitignored)

### Production Recommendations
- Implement JWT authentication for REST APIs
- Use TLS/SSL for all connections
- Enable Redis AUTH
- Use connection pooling for databases
- Implement rate limiting
- Add API key authentication for IoT devices

---

## 7. Error Handling

### HTTP Error Codes
- `200` - Success
- `400` - Bad Request (missing parameters)
- `404` - Resource Not Found
- `500` - Internal Server Error

### WebSocket Error Messages
```json
{
  "type": "error",
  "code": "INVALID_DATA",
  "message": "Invalid sensor data format",
  "timestamp": "2025-11-07T08:00:00.000Z"
}
```

---

## 8. Data Flow Examples

### Example 1: Getting Car Data
```
User (Browser)
  → GET /api/car/ABC-123 → B1 Web Server
      → MongoDB: Get real-time data (temp, GPS)
      → PostgreSQL: Get static data (owner, service)
      → Combine data
  ← JSON Response (combined data)
```

### Example 2: Sending Command
```
User (Browser)
  → POST /api/car/ABC-123/command {"command": "start_ac"} → B1 Web Server
      → Redis: PUBLISH car:ABC-123:commands
          → C1 Cloud Comm (subscribed)
              → Execute command on car
              → Redis: PUBLISH car:ABC-123:status "executed"
  ← JSON Response "Command sent"
```

### Example 3: Sensor Data Flow
```
C5 Sensors (Python)
  → WebSocket: Send sensor data → B2 IoT Gateway
      → MongoDB: Store data in car_data collection
      → Redis: PUBLISH car:updates (notify subscribers)
  ← WebSocket: ACK message
```

---

## 9. Testing APIs

### Using Swagger UI
B1 Web Server has interactive API documentation:
```
http://localhost:3001/api-docs
```

### Using curl
```bash
# Get car data
curl http://localhost:3001/api/car/ABC-123

# Send command
curl -X POST http://localhost:3001/api/car/ABC-123/command \
  -H "Content-Type: application/json" \
  -d '{"command": "start_ac"}'

# Check health
curl http://localhost:3001/health
curl http://localhost:3003/health
```

### Using Redis CLI
```bash
# Subscribe to commands
redis-cli SUBSCRIBE "car:*:commands"

# Publish test command
redis-cli PUBLISH "car:ABC-123:commands" '{"command":"start_ac"}'
```

---

## 10. Configuration

### Environment Variables

**B1 Web Server:**
```env
PORT=3001
MONGO_URL=mongodb://admin:password@localhost:27017
MONGO_DB=cardata
PG_USER=postgres
PG_PASSWORD=password
PG_HOST=localhost
PG_DB=carinfo
REDIS_URL=redis://localhost:6379
```

**B2 IoT Gateway:**
```env
PORT=3002
WS_PORT=8081
MONGO_URL=mongodb://admin:password@localhost:27017
MONGO_DB=cardata
REDIS_URL=redis://localhost:6379
```

**C2 Central Broker:**
```env
PORT=3003
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Quick Reference

### Service Ports
- `3000` - A2 Rental Staff App (React)
- `3001` - B1 Web Server (REST API)
- `3002` - B2 IoT Gateway (HTTP + WebSocket)
- `3003` - C2 Central Broker (Node.js + Redis)
- `8081` - WebSocket Server (B2)
- `27017` - MongoDB
- `5432` - PostgreSQL
- `6379` - Redis

### Swagger Documentation
- B1 API Docs: http://localhost:3001/api-docs

### Health Checks
- B1: http://localhost:3001/health
- B2: http://localhost:3002/health
- C2: http://localhost:3003/health
