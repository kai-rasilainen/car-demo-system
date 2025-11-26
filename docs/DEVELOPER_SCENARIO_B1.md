# Developer Scenario: Getting B1 Requirements from Agent Analysis

## Scenario Overview

**Feature Request**: "Add real-time tire pressure monitoring to the mobile app"

**Your Role**: Backend Developer (B1 - Web Server API)

**Goal**: Understand what API endpoints, database queries, and business logic you need to implement in the B1 Express server.

---

## Step 1: Run Jenkins Pipeline

### Trigger the AI Analysis

```bash
# Jenkins Pipeline Parameters:
FEATURE_REQUEST: "Add real-time tire pressure monitoring to the mobile app"
USE_AI_AGENTS: true
OLLAMA_MODEL: llama3:8b
OUTPUT_FILE: tire-pressure-monitoring-analysis.md
```

### What Happens Behind the Scenes

```
User Request: "Add real-time tire pressure monitoring to mobile app"
     |
     v
[Agent A] Analyzes frontend impact
     |
     |--> A1 (Mobile): Needs pressure display UI
     |--> A2 (Web): Dashboard might need monitoring view
     |
     v
[Agent A decides]: Needs backend API -> calls Agent B
     |
     v
[Agent B] Analyzes backend impact
     |
     |--> B1 (API): New monitoring endpoints needed <-- YOUR WORK
     |--> B2 (WebSocket): Real-time push to clients
     |--> B3 (MongoDB): Current readings storage
     |--> B4 (PostgreSQL): Historical data storage
     |
     v
[Agent B decides]: Needs sensor data -> calls Agent C
     |
     v
[Agent C] Analyzes in-car systems
     |
     |--> C5 (Sensors): Tire pressure monitoring
     |--> C2 (Redis): Real-time data caching
     |--> C1 (Cloud Comm): Send data to backend
```

---

## Step 2: Download Your Task File

After Jenkins completes, download:

```
analysis-reports/
  |-- tire-pressure-monitoring-analysis.md  (full analysis)
  `-- component-tasks/
      `-- task-B1.md  <-- YOUR FILE
```

---

## Step 3: Review task-B1.md

### Example Contents of task-B1.md

```markdown
# Task: B1

**Component**: B1  
**Technology**: Node.js/Express (REST API)  
**Effort Estimate**: 4 hours

Generated from analysis: `tire-pressure-monitoring-analysis.md`

## Analysis Excerpt

Agent B Analysis - Component B1 (Web Server):
- Create new REST API endpoint: GET /api/monitoring/tire-pressure/:carId
- Create new REST API endpoint: GET /api/monitoring/tire-pressure/:carId/history
- Query B3 (MongoDB) for current tire pressure readings
- Query B4 (PostgreSQL) for historical pressure data
- Return JSON with pressure values, timestamp, and car info
- Add time range filtering for historical data
- Add pagination for history (limit 100 per page)
- Integrate with B2 for real-time WebSocket updates

Dependencies:
- B3 (MongoDB): tire_pressure_readings collection must exist
- B4 (PostgreSQL): tire_pressure_history table required
- A1 (Mobile): Will call these endpoints

## Proposed Implementation

### Mock Pressure Provider (for development)

```javascript
// File: B1-web-server/utils/mockPressureProvider.js
// Use this for testing when database is not available

class MockPressureProvider {
  constructor() {
    // Normal pressure range: 2.2-2.5 bar
    this.baselinePressures = {
      'ABC-123': { frontLeft: 2.3, frontRight: 2.4, rearLeft: 2.3, rearRight: 2.4 },
      'XYZ-789': { frontLeft: 2.2, frontRight: 2.3, rearLeft: 2.2, rearRight: 2.3 },
      'DEF-456': { frontLeft: 2.4, frontRight: 2.4, rearLeft: 2.5, rearRight: 2.5 },
    };
  }
  
  // Generate realistic pressure readings with small variations
  getCurrentPressure(carId) {
    const baseline = this.baselinePressures[carId] || {
      frontLeft: 2.3,
      frontRight: 2.3,
      rearLeft: 2.3,
      rearRight: 2.3
    };
    
    // Add small random variation (+/- 0.1 bar)
    const addVariation = (value) => {
      const variation = (Math.random() - 0.5) * 0.2;
      return Math.max(1.8, Math.min(2.8, value + variation));
    };
    
    return {
      carId,
      licensePlate: carId,
      tirePressure: {
        frontLeft: parseFloat(addVariation(baseline.frontLeft).toFixed(1)),
        frontRight: parseFloat(addVariation(baseline.frontRight).toFixed(1)),
        rearLeft: parseFloat(addVariation(baseline.rearLeft).toFixed(1)),
        rearRight: parseFloat(addVariation(baseline.rearRight).toFixed(1))
      },
      unit: 'bar',
      timestamp: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
      isMockData: true // Flag to indicate this is test data
    };
  }
  
  // Generate historical data for testing
  getHistoricalPressure(carId, days = 7) {
    const history = [];
    const now = new Date();
    
    for (let i = 0; i < days * 4; i++) { // 4 readings per day
      const timestamp = new Date(now - i * 6 * 60 * 60 * 1000); // Every 6 hours
      const reading = this.getCurrentPressure(carId);
      
      history.push({
        tirePressure: reading.tirePressure,
        unit: 'bar',
        timestamp: timestamp.toISOString()
      });
    }
    
    return history;
  }
}

module.exports = new MockPressureProvider();
```

### Example Code for B1 (with mock data fallback)

```javascript
// File: B1-web-server/routes/monitoring.js
const express = require('express');
const router = express.Router();
const mockPressureProvider = require('../utils/mockPressureProvider');

// Environment flag to enable/disable mock data
const USE_MOCK_DATA = process.env.USE_MOCK_DATA === 'true';

// GET /api/monitoring/tire-pressure/:carId
// Returns current tire pressure readings for a specific car
router.get('/tire-pressure/:carId', async (req, res) => {
  try {
    const { carId } = req.params;
    
    // Try to get real data from database first
    let reading = null;
    let usedMockData = false;
    
    if (!USE_MOCK_DATA) {
      try {
        reading = await db.collection('tire_pressure_readings')
          .findOne(
            { carId },
            { sort: { timestamp: -1 } }
          );
      } catch (dbError) {
        console.warn('Database unavailable, falling back to mock data:', dbError.message);
      }
    }
    
    // Fallback to mock data if database is unavailable or flag is set
    if (!reading) {
      console.log(`[MOCK] Using mock tire pressure data for ${carId}`);
      reading = mockPressureProvider.getCurrentPressure(carId);
      usedMockData = true;
    }
    
    // Enrich with car details (skip if using mock data)
    let licensePlate = reading.licensePlate || carId;
    if (!usedMockData) {
      const car = await db.collection('cars').findOne({ carId });
      licensePlate = car?.licensePlate || carId;
    }
    
    res.json({
      success: true,
      carId,
      licensePlate,
      tirePressure: {
        frontLeft: reading.tirePressure?.frontLeft || reading.frontLeft,
        frontRight: reading.tirePressure?.frontRight || reading.frontRight,
        rearLeft: reading.tirePressure?.rearLeft || reading.rearLeft,
        rearRight: reading.tirePressure?.rearRight || reading.rearRight
      },
      unit: reading.unit || 'bar',
      timestamp: reading.timestamp,
      lastUpdated: reading.timestamp,
      isMockData: usedMockData // Let frontend know this is test data
    });
    
  } catch (error) {
    console.error('Error fetching tire pressure:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch tire pressure data' 
    });
  }
});

});

// GET /api/monitoring/tire-pressure/:carId/history
// Get historical tire pressure readings from B4 (PostgreSQL)
router.get('/tire-pressure/:carId/history', async (req, res) => {
  try {
    const { carId } = req.params;
    const { startDate, endDate, limit = 100, offset = 0 } = req.query;
    
    let history = [];
    let usedMockData = false;
    
    // Try to get real data from database first
    if (!USE_MOCK_DATA) {
      try {
        let query = `
          SELECT 
            car_id,
            front_left,
            front_right,
            rear_left,
            rear_right,
            unit,
            recorded_at
          FROM tire_pressure_history
          WHERE car_id = $1
        `;
        
        const params = [carId];
        let paramIndex = 2;
        
        if (startDate) {
          query += ` AND recorded_at >= $${paramIndex}`;
          params.push(startDate);
          paramIndex++;
        }
        
        if (endDate) {
          query += ` AND recorded_at <= $${paramIndex}`;
          params.push(endDate);
          paramIndex++;
        }
        
        query += ` ORDER BY recorded_at DESC LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;
        params.push(parseInt(limit), parseInt(offset));
        
        const result = await pgPool.query(query, params);
        
        history = result.rows.map(row => ({
          tirePressure: {
            frontLeft: row.front_left,
            frontRight: row.front_right,
            rearLeft: row.rear_left,
            rearRight: row.rear_right
          },
          unit: row.unit,
          timestamp: row.recorded_at
        }));
        
      } catch (dbError) {
        console.warn('Database unavailable for history, falling back to mock data:', dbError.message);
        usedMockData = true;
      }
    } else {
      usedMockData = true;
    }
    
    // Fallback to mock data if database is unavailable
    if (usedMockData || history.length === 0) {
      console.log(`[MOCK] Using mock historical tire pressure data for ${carId}`);
      history = mockPressureProvider.getHistoricalPressure(carId, 7);
      
      // Apply pagination to mock data
      const start = parseInt(offset);
      const end = start + parseInt(limit);
      history = history.slice(start, end);
    }
    
    res.json({
      success: true,
      carId,
      history,
      pagination: {
        count: history.length,
        limit: parseInt(limit),
        offset: parseInt(offset)
      },
      isMockData: usedMockData
    });
    
  } catch (error) {
    console.error('Error fetching pressure history:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch pressure history' 
    });
  }
});

module.exports = router;
```
    
    res.json({
      success: true,
      carId,
      history: result.rows,
      count: result.rows.length
    });
    
  } catch (error) {
    console.error('Error fetching pressure history:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch pressure history' 
    });
  }
});

module.exports = router;
```

### How to Enable Mock Data

```bash
# In your .env file or environment variables:
USE_MOCK_DATA=true

# Start your B1 server:
npm start

# Mock data will be used automatically when:
# 1. USE_MOCK_DATA=true is set
# 2. Database connection fails
# 3. No data exists for the requested carId
```

### Testing with Mock Data

```bash
# Test current pressure endpoint:
curl http://localhost:3001/api/monitoring/tire-pressure/ABC-123

# Expected response with mock data:
{
  "success": true,
  "carId": "ABC-123",
  "licensePlate": "ABC-123",
  "tirePressure": {
    "frontLeft": 2.4,
    "frontRight": 2.3,
    "rearLeft": 2.2,
    "rearRight": 2.5
  },
  "unit": "bar",
  "timestamp": "2024-11-26T10:30:00.000Z",
  "lastUpdated": "2024-11-26T10:30:00.000Z",
  "isMockData": true
}

# Test historical data endpoint:
curl http://localhost:3001/api/monitoring/tire-pressure/ABC-123/history?limit=10

# You'll get 10 historical readings with realistic variations
```

### Additional: Data Storage Logic (Background Process)

```javascript
// File: B1-web-server/services/monitoringService.js
// This runs when B2 receives new sensor data from C1

class MonitoringService {
  constructor(db, pgPool, io) {
    this.db = db;
    this.pgPool = pgPool;
    this.io = io; // WebSocket for real-time notifications
  }
  
  async storeTirePressure(carData) {
    const { carId, licensePlate, tirePressure, timestamp } = carData;
    
    try {
      // Store current reading in B3 (MongoDB) - for latest value
      await this.db.collection('tire_pressure_readings').updateOne(
        { carId },
        {
          $set: {
            carId,
            licensePlate,
            frontLeft: tirePressure.frontLeft,
            frontRight: tirePressure.frontRight,
            rearLeft: tirePressure.rearLeft,
            rearRight: tirePressure.rearRight,
            unit: 'bar',
            timestamp: new Date(timestamp),
            updatedAt: new Date()
          }
        },
        { upsert: true }
      );
      
      // Store in B4 (PostgreSQL) for historical analysis
      await this.pgPool.query(
        `INSERT INTO tire_pressure_history 
         (car_id, front_left, front_right, rear_left, rear_right, unit, recorded_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [
          carId,
          tirePressure.frontLeft,
          tirePressure.frontRight,
          tirePressure.rearLeft,
          tirePressure.rearRight,
          'bar',
          new Date(timestamp)
        ]
      );
      
      // Emit real-time update via B2 WebSocket
      this.io.emit('tire-pressure:update', {
        carId,
        licensePlate,
        tirePressure,
        timestamp
      });
      
      console.log(`[MONITORING] Stored tire pressure for ${carId}`);
      
    } catch (error) {
      console.error('Error storing tire pressure:', error);
      throw error;
    }
  }
}

module.exports = MonitoringService;
```

## Suggested Subtasks

- [X] Review analysis excerpt and understand requirements
- [ ] Create `/utils/mockPressureProvider.js` for development testing
- [ ] Adapt the code template to specific feature needs
- [ ] Create `/routes/monitoring.js` with GET endpoints and mock data fallback
- [ ] Add `USE_MOCK_DATA` environment variable to .env file
- [ ] Test endpoints with mock data (no database required)
- [ ] Create `/services/monitoringService.js` for data storage logic
- [ ] Add route to main server.js: `app.use('/api/monitoring', monitoringRouter)`
- [ ] Coordinate with B3 team: ensure `tire_pressure_readings` collection exists with indexes
- [ ] Coordinate with B4 team: ensure `tire_pressure_history` table exists
- [ ] Switch from mock data to real database integration
- [ ] Add unit tests for monitoring endpoints
- [ ] Add integration tests with B3 (MongoDB)
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Test with Postman/curl before A1 integration
- [ ] Add error handling and input validation
- [ ] Add logging for debugging

## Notes

- **Component**: B1 (Web Server API)
- **Effort**: 4 hours
- **Mock Data**: Available for testing without Agent C or database
  - Set `USE_MOCK_DATA=true` to always use mock data
  - Automatic fallback if database is unavailable
  - Mock provider generates realistic pressure values (2.0-2.6 bar)
  - Historical data includes 28 readings (7 days x 4 per day)
  - Response includes `isMockData: true` flag
- **Dependencies**: 
  - B3 (MongoDB): Needs `tire_pressure_readings` collection with index on `carId` (optional with mock data)
  - B4 (PostgreSQL): Needs `tire_pressure_history` table with indexes (optional with mock data)
  - B2 (WebSocket): Will notify clients via `io.emit()`
  - A1 (Mobile): Will consume these API endpoints
  - **NO dependency on Agent C for development** - mock data provider replaces sensor data
- **API Endpoints**:
  - `GET /api/monitoring/tire-pressure/:carId` - Get current pressure readings
  - `GET /api/monitoring/tire-pressure/:carId/history` - Get historical data
- **Data Models**:
  - MongoDB `tire_pressure_readings` collection (current readings)
  - PostgreSQL `tire_pressure_history` table (historical data)
```

## Step 4: What You Need to Do

### As a B1 Developer:

1. **Read the task file** (`task-B1.md`)
2. **Copy the example code** as a starting point
3. **Coordinate with other teams**:
   - Ask B3 team: "Do we have the `tire_pressure_readings` collection?"
   - Ask B4 team: "Can you create the `tire_pressure_history` table?"
   - Ask B2 team: "Can I emit `tire-pressure:update` events?"
4. **Implement the endpoints** in your B1 codebase
5. **Write tests** for your endpoints
6. **Create a small PR** focused only on B1 changes
7. **Update API docs** so A1 team knows how to call your endpoints

### Your Deliverables:

- `B1-web-server/routes/monitoring.js` - API endpoints
- `B1-web-server/services/monitoringService.js` - Data storage logic
- `B1-web-server/tests/monitoring.test.js` - Unit tests
- Updated `API_DOCS.md` with new endpoints

---

## Step 5: Integration with Other Components

### Data Flow (for your understanding):

```
C5 (Sensors) generates pressure data
     |
C2 (Redis) stores latest readings
     |
C1 (Cloud Comm) fetches from Redis
     |
B2 (WebSocket) receives from C1
     |
B1 (YOU!) MonitoringService stores data
     |
B3 (MongoDB) stores current readings
     |
B4 (PostgreSQL) stores historical data
     |
B1 (YOU!) API returns data
     |
A1 (Mobile) displays to user
```

### Your Touch Points:

- **Upstream (you receive from)**:
  - B2 sends you real-time sensor data via `monitoringService.storeTirePressure()`
  
- **Downstream (you send to)**:
  - B3: You store current readings in MongoDB
  - B4: You store historical data in PostgreSQL
  - B2: You emit WebSocket events for real-time updates
  - A1: You provide REST API endpoints

---

## Summary

**As a B1 developer, you now know**:

[X] What API endpoints to create  
[X] What data storage logic to implement  
[X] What database queries to write  
[X] What other components depend on you (A1, A2)  
[X] What components you depend on (B2, B3, B4)  
[X] Example code to start from  
[X] Estimated effort (4 hours)  
[X] Clear subtasks to complete  

**You DON'T need to understand**:
- How C5 generates sensor data
- How C2 Redis broker works
- How A1 renders the UI
- The full system architecture

**You ONLY need to focus on**: Your B1 API endpoints and data storage logic.

This is the power of component-level task breakdown! [*]
