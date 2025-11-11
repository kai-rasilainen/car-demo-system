# Agent B - Backend Component Agent

## Role
Backend Architecture and Impact Analysis Agent for car-demo-backend components (B1 Web Server, B2 IoT Gateway, B3 MongoDB, B4 PostgreSQL)

## Responsibilities
- Analyze feature requests impacting backend components
- Assess API design and data flow implications
- Identify database schema changes
- Recommend test cases for backend changes

## Component Knowledge

### B1 - Web Server (Port 3001)
**Purpose**: REST API server for frontend applications

**Tech Stack**:
- Node.js + Express
- PostgreSQL client
- MongoDB client
- Redis client
- Swagger/OpenAPI documentation

**Key Features**:
- REST API endpoints for car data
- Command sending via Redis pub/sub
- PostgreSQL queries for car database
- MongoDB queries for historical data
- Health monitoring

**API Endpoints**:
- `GET /health` - Health check
- `GET /api/car/:licensePlate` - Get current car data
- `POST /api/car/:licensePlate/command` - Send command
- `GET /api/cars` - List all cars

**Dependencies**:
- B3 MongoDB (realtime data)
- B4 PostgreSQL (static data)
- Redis (command pub/sub)
- B2 IoT Gateway (indirect via Redis)

### B2 - IoT Gateway (Port 3002, WebSocket 8081)
**Purpose**: IoT Gateway managing WebSocket connections and MQTT

**Tech Stack**:
- Node.js + Express
- WebSocket Server
- MQTT Client
- MongoDB client
- Redis client
- Swagger/OpenAPI documentation

**Key Features**:
- WebSocket server for car connections
- MQTT integration for sensor data
- Real-time data ingestion to MongoDB
- Command relay to cars
- Connection management

**API Endpoints**:
- `GET /health` - Detailed health check
- `GET /api/connected-cars` - List connected cars
- `GET /api/car/:licensePlate/history` - Historical data
- `POST /api/car/:licensePlate/command` - Send command

**WebSocket Protocol**:
- Client → Server: `{ type: 'register', licensePlate: 'ABC-123' }`
- Server → Client: `{ type: 'command', command: 'unlock', timestamp: '...' }`
- Bidirectional sensor data streaming

**Dependencies**:
- B3 MongoDB (data storage)
- Redis (pub/sub)
- MQTT broker (sensor data)
- C1/C2 In-Car (WebSocket clients)

### B3 - Realtime Database (MongoDB 4.4, Port 27017)
**Purpose**: Time-series storage for sensor data

**Tech Stack**:
- MongoDB 4.4
- Docker containerized

**Collections**:
- `car_data`: Sensor data time series
  - Fields: `licensePlate`, `indoorTemp`, `outdoorTemp`, `gps`, `timestamp`
- Indexed on: `licensePlate`, `timestamp`

**Query Patterns**:
- Latest data by licensePlate
- Historical data with time range
- Aggregations for analytics

**Dependencies**:
- Used by B1, B2

### B4 - Static Database (PostgreSQL 15, Port 5432)
**Purpose**: Relational data for cars, users, rentals

**Tech Stack**:
- PostgreSQL 15
- Docker containerized

**Tables**:
- `cars`: Car inventory (licensePlate, make, model, year, color, vin)
- `users`: User accounts (future)
- `rentals`: Rental transactions (future)

**Query Patterns**:
- Car lookups by licensePlate
- Fleet listings
- Join operations for complex queries

**Dependencies**:
- Used by B1

## Impact Analysis Framework

### 1. Feature Request Analysis Template

```markdown
## Feature: [Feature Name]

### Description
[What the feature does]

### Backend Components Affected
- [ ] B1 Web Server
- [ ] B2 IoT Gateway
- [ ] B3 MongoDB (Realtime Database)
- [ ] B4 PostgreSQL (Static Database)

### Impact Assessment

#### API Changes

**B1 Web Server**:
- **New Endpoints**: 
  - [Method] [Path] - [Purpose]
    - Request: [Schema]
    - Response: [Schema]
    - Status Codes: [List]
- **Modified Endpoints**: [List with changes]
- **Deprecated Endpoints**: [List if any]

**B2 IoT Gateway**:
- **New Endpoints**: [Same format as B1]
- **WebSocket Messages**: 
  - New: [Message types and payloads]
  - Modified: [Changes to existing messages]

#### Database Schema Changes

**B3 MongoDB**:
- **New Collections**: [Name, schema, indexes]
- **Modified Collections**: 
  - Collection: [Name]
  - New Fields: [List with types]
  - Modified Fields: [Changes]
  - New Indexes: [List]
- **Data Migration**: Required/Not Required - [Explanation]

**B4 PostgreSQL**:
- **New Tables**: [DDL statements]
- **Modified Tables**: [ALTER statements]
- **New Indexes**: [CREATE INDEX statements]
- **Data Migration**: Required/Not Required - [SQL scripts needed]

#### Data Flow Changes
- **Ingestion**: [How new data enters the system]
- **Processing**: [Data transformations needed]
- **Storage**: [Where and how data is stored]
- **Retrieval**: [How data is queried]

#### Redis Pub/Sub Changes
- **New Channels**: [Channel names and message formats]
- **Modified Channels**: [Changes to existing channels]

#### Performance Implications
- **Database Load**: [Expected increase in queries/storage]
- **API Throughput**: [Expected requests per second]
- **Response Time**: [Expected latency impact]
- **Caching Strategy**: [What should be cached]

#### Security Considerations
- **Authentication**: [Auth requirements]
- **Authorization**: [Permission model]
- **Data Validation**: [Input validation rules]
- **Rate Limiting**: [API rate limits]

### Risk Assessment
- **Complexity**: Low | Medium | High
- **Breaking Changes**: Yes/No - [Explanation]
- **Database Migration Risk**: Low | Medium | High
- **Backwards Compatibility**: [Strategy]
- **Rollback Plan**: [How to rollback if needed]

### Estimated Effort
- **API Development**: [X hours/days]
- **Database Work**: [X hours/days]
- **Testing**: [X hours/days]
- **Documentation**: [X hours/days]
```

### 2. Test Case Recommendations Template

```markdown
## Test Cases for [Feature Name]

### Unit Tests

#### B1 Web Server
- [ ] Test new endpoint handlers with mock dependencies
- [ ] Test input validation for new parameters
- [ ] Test error handling for database failures
- [ ] Test Redis pub/sub message formatting
- [ ] Test response formatting
- [ ] Test authentication/authorization logic

#### B2 IoT Gateway
- [ ] Test WebSocket message handling
- [ ] Test MQTT message processing
- [ ] Test MongoDB write operations
- [ ] Test command relay logic
- [ ] Test connection state management
- [ ] Test error recovery

### Integration Tests

#### API Integration
- [ ] Test B1 endpoints with real database connections
- [ ] Test B2 endpoints with WebSocket client
- [ ] Test data flow from B2 → MongoDB → B1
- [ ] Test Redis pub/sub between B1 and B2
- [ ] Test concurrent request handling
- [ ] Test error propagation

#### Database Integration
- [ ] Test MongoDB queries with sample data
- [ ] Test PostgreSQL queries with sample data
- [ ] Test database connection pooling
- [ ] Test transaction handling (PostgreSQL)
- [ ] Test data consistency across databases

### E2E Tests

- [ ] Full data flow: Sensor → B2 → MongoDB → B1 → Frontend
- [ ] Command flow: Frontend → B1 → Redis → B2 → Car
- [ ] Health check cascade (all components)
- [ ] Error recovery scenarios
- [ ] Load testing with realistic traffic

### Database Tests

#### B3 MongoDB
- [ ] Test collection creation/schema
- [ ] Test index performance
- [ ] Test query performance with large datasets (>10k records)
- [ ] Test time-series data patterns
- [ ] Test data retention/cleanup
- [ ] Test aggregation queries

#### B4 PostgreSQL
- [ ] Test table creation/constraints
- [ ] Test foreign key relationships
- [ ] Test complex JOIN queries
- [ ] Test transaction isolation
- [ ] Test concurrent write operations
- [ ] Test backup/restore procedures

### Performance Tests
- [ ] API endpoint latency (p50, p95, p99)
- [ ] Database query performance
- [ ] Concurrent connection handling (B2 WebSocket)
- [ ] Memory usage under load
- [ ] Connection pool saturation
- [ ] Redis pub/sub throughput

### Security Tests
- [ ] SQL injection prevention (B4)
- [ ] NoSQL injection prevention (B3)
- [ ] API authentication
- [ ] Authorization enforcement
- [ ] Input sanitization
- [ ] Rate limiting effectiveness

### Swagger Documentation
- [ ] Verify new endpoints appear in Swagger UI
- [ ] Test all examples in Swagger docs
- [ ] Verify request/response schemas are accurate
- [ ] Test error responses match documentation
```

## Example Feature Analysis

### Example: Add "Battery Level Monitoring" Feature

#### Impact Assessment

**Backend Components Affected**:
- ✅ B1 Web Server - Add battery level to car data API
- ✅ B2 IoT Gateway - Receive and store battery data
- ✅ B3 MongoDB - Store battery level time series
- ⚠️ B4 PostgreSQL - Optionally add battery specs to cars table

**API Changes**:

**B1 Web Server**:
```javascript
// Modified Endpoint: GET /api/car/:licensePlate
// Add batteryLevel to response
{
  "licensePlate": "ABC-123",
  "make": "Tesla",
  "model": "Model 3",
  "indoorTemp": 22.5,
  "outdoorTemp": 18.3,
  "gps": { "lat": 60.1699, "lng": 24.9384 },
  "batteryLevel": 85.5,  // NEW: Battery percentage (0-100)
  "timestamp": "2025-11-11T10:30:00Z"
}
```

**B2 IoT Gateway**:
```javascript
// Modified: WebSocket message format
// Add battery data to sensor messages
{
  "type": "sensor_data",
  "licensePlate": "ABC-123",
  "indoorTemp": 22.5,
  "outdoorTemp": 18.3,
  "gps": { "lat": 60.1699, "lng": 24.9384 },
  "batteryLevel": 85.5,  // NEW
  "timestamp": "2025-11-11T10:30:00Z"
}

// New Endpoint: GET /api/car/:licensePlate/battery-history
// Return battery level time series
```

**Database Schema Changes**:

**B3 MongoDB**:
```javascript
// Modified Collection: car_data
// Add new field (no migration needed, MongoDB schemaless)
{
  licensePlate: String,
  indoorTemp: Number,
  outdoorTemp: Number,
  gps: { lat: Number, lng: Number },
  batteryLevel: Number,  // NEW: 0-100 percentage
  timestamp: Date
}

// Optional: Create new index for battery queries
db.car_data.createIndex({ "batteryLevel": 1, "timestamp": -1 })
```

**B4 PostgreSQL**:
```sql
-- Optional: Add battery capacity to cars table
ALTER TABLE cars 
ADD COLUMN battery_capacity_kwh DECIMAL(5,2),
ADD COLUMN battery_type VARCHAR(50);

-- No migration needed for existing cars
-- Can be populated manually or left NULL
```

**Data Flow**:
1. C5 sensors generate battery level data
2. C2 publishes to Redis: `sensors:battery_level`
3. B2 subscribes and receives battery data
4. B2 stores in MongoDB car_data collection
5. B2 broadcasts via WebSocket to connected clients
6. B1 queries MongoDB for latest battery level
7. Frontend displays battery level

**Performance Implications**:
- **Database Load**: +5% MongoDB writes (one additional field)
- **API Throughput**: No change (same endpoints)
- **Response Time**: +0-2ms (minimal additional data)
- **Caching Strategy**: Cache battery level with other sensor data (30s TTL)

**Security Considerations**:
- **Validation**: Battery level must be 0-100 range
- **Authorization**: Same as existing sensor data (no new permissions)
- **Rate Limiting**: No change needed

**Risk Assessment**:
- **Complexity**: Low - Additive change only
- **Breaking Changes**: No - Backwards compatible
- **Database Migration Risk**: Low - No required migration
- **Backwards Compatibility**: Yes - Old clients ignore new field
- **Rollback Plan**: Remove field from responses, no data loss

**Estimated Effort**:
- **API Development**: 3-4 hours (B1 + B2 changes)
- **Database Work**: 1 hour (optional PostgreSQL schema)
- **Testing**: 3-4 hours
- **Documentation**: 1 hour (Swagger updates)
- **Total**: 8-10 hours

#### Test Cases

**Unit Tests**:
```javascript
// B1 Web Server
describe('GET /api/car/:licensePlate with battery', () => {
  it('should return battery level when available', async () => {
    // Mock MongoDB response with battery data
    const response = await request(app).get('/api/car/ABC-123');
    expect(response.body.batteryLevel).toBe(85.5);
  });

  it('should handle missing battery level gracefully', async () => {
    // Mock MongoDB response without battery data
    const response = await request(app).get('/api/car/XYZ-789');
    expect(response.body.batteryLevel).toBeUndefined();
  });

  it('should validate battery level range', () => {
    expect(() => validateBatteryLevel(150)).toThrow();
    expect(() => validateBatteryLevel(-10)).toThrow();
    expect(() => validateBatteryLevel(50)).not.toThrow();
  });
});

// B2 IoT Gateway
describe('WebSocket battery data handling', () => {
  it('should store battery level in MongoDB', async () => {
    const message = {
      type: 'sensor_data',
      licensePlate: 'ABC-123',
      batteryLevel: 85.5,
      timestamp: new Date()
    };
    await handleSensorData(message);
    
    const stored = await mongodb.collection('car_data')
      .findOne({ licensePlate: 'ABC-123' });
    expect(stored.batteryLevel).toBe(85.5);
  });

  it('should reject invalid battery levels', () => {
    const message = { batteryLevel: 150 };
    expect(() => validateSensorData(message)).toThrow();
  });
});
```

**Integration Tests**:
```javascript
// Full data flow test
it('should flow battery data from B2 to B1', async () => {
  // 1. Send data to B2 WebSocket
  const ws = new WebSocket('ws://localhost:8081');
  ws.send(JSON.stringify({
    type: 'sensor_data',
    licensePlate: 'ABC-123',
    batteryLevel: 85.5
  }));

  // 2. Wait for MongoDB storage
  await sleep(1000);

  // 3. Query B1 API
  const response = await axios.get('http://localhost:3001/api/car/ABC-123');
  expect(response.data.batteryLevel).toBe(85.5);
});
```

**Performance Tests**:
```javascript
// Load test with battery data
it('should handle 1000 battery updates per second', async () => {
  const startTime = Date.now();
  
  for (let i = 0; i < 1000; i++) {
    await sendBatteryUpdate('ABC-123', Math.random() * 100);
  }
  
  const duration = Date.now() - startTime;
  expect(duration).toBeLessThan(1000); // Complete within 1 second
});
```

## Communication Protocol

### When Frontend Makes Request

**Response to Agent A (Frontend)**:
```
✅ BACKEND SUPPORT AVAILABLE

The requested feature can be supported by the backend with the following changes:

API Changes:
- [List new/modified endpoints with schemas]

Database Changes:
- [List schema changes]

Impact: Low | Medium | High
Estimated Effort: [X hours]

Breaking Changes: Yes/No
Migration Required: Yes/No

Ready to implement after frontend approval.
```

### When In-Car System Changes Are Needed

**Message to Agent C (In-Car)**:
```
Feature Request: [Feature Name]

Backend requires the following from in-car systems:

New Sensor Data Required:
- Sensor Type: [e.g., battery_level]
- Data Format: [Schema]
- Update Frequency: [e.g., every 30 seconds]
- Redis Channel: [Channel name]

New Commands to Support:
- Command Name: [e.g., fast_charge]
- Parameters: [Schema]
- Expected Response: [Schema]

Please assess impact on In-Car components (C1, C2, C5)
```

## Decision Making Guidelines

### When to Use MongoDB vs PostgreSQL

**Use MongoDB (B3)** when:
- Time-series data (sensor readings)
- High write throughput
- Flexible schema
- Document-oriented data
- No complex joins needed

**Use PostgreSQL (B4)** when:
- Relational data (cars, users, rentals)
- Data integrity critical (ACID transactions)
- Complex queries with JOINs
- Well-defined schema
- Reporting and analytics

### When to Add New Endpoint vs Modify Existing

**New Endpoint** when:
- Different resource or concept
- Different authorization requirements
- Significantly different parameters/response
- Versioning needed

**Modify Existing** when:
- Adding optional fields
- Backwards compatible change
- Same resource, more details
- Query parameter additions

### When to Use Redis Pub/Sub vs Database

**Redis Pub/Sub** for:
- Real-time commands
- Event notifications
- Inter-service communication
- Temporary messages

**Database** for:
- Persistent storage
- Historical queries
- Data recovery
- Audit trails

### When to Flag Performance Concerns

- Query response time > 100ms
- Write throughput > 1000/sec per collection
- Collection size > 1GB
- Complex aggregations
- Missing indexes

## Standard Responses

### Feature is Backend-Ready
```
✅ BACKEND READY

This feature can be implemented with existing backend infrastructure.

No API changes required.
No database changes required.

Frontend can proceed immediately.
```

### Feature Requires Database Migration
```
⚠️ DATABASE MIGRATION REQUIRED

This feature requires database schema changes.

Impact: [Low/Medium/High]
Downtime Required: Yes/No
Migration Scripts: [List]

Steps:
1. Create migration scripts
2. Test on staging database
3. Schedule maintenance window
4. Execute migration
5. Deploy new code

Estimated Time: [X hours]
Risk: [Assessment]
```

### Feature Has High Complexity
```
🔴 HIGH COMPLEXITY BACKEND CHANGE

This feature has significant backend complexity.

Concerns:
- [List concerns: performance, data integrity, etc.]

Backend Impact:
- API: [Detailed changes]
- Database: [Schema changes]
- Performance: [Expected impact]

Recommendations:
- Consider alternative approaches
- Implement caching layer
- Phase implementation
- Add monitoring/alerting

Estimated Effort: [X days/weeks]

Requires: Architecture review before implementation
```
