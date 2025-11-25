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
     |--> B1 (API): New monitoring endpoints needed ⬅️ YOUR WORK
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

### Example Code for B1

```javascript
// File: B1-web-server/routes/monitoring.js
const express = require('express');
const router = express.Router();

// GET /api/monitoring/tire-pressure/:carId
// Returns current tire pressure readings for a specific car
router.get('/tire-pressure/:carId', async (req, res) => {
  try {
    const { carId } = req.params;
    
    // Query B3 (MongoDB) for latest reading
    const reading = await db.collection('tire_pressure_readings')
      .findOne(
        { carId },
        { sort: { timestamp: -1 } }
      );
    
    if (!reading) {
      return res.status(404).json({
        success: false,
        error: 'No tire pressure data found for this car'
      });
    }
    
    // Enrich with car details
    const car = await db.collection('cars').findOne({ carId });
    
    res.json({
      success: true,
      carId,
      licensePlate: car?.licensePlate,
      tirePressure: {
        frontLeft: reading.frontLeft,
        frontRight: reading.frontRight,
        rearLeft: reading.rearLeft,
        rearRight: reading.rearRight
      },
      unit: reading.unit || 'bar',
      timestamp: reading.timestamp,
      lastUpdated: reading.timestamp
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
    
    res.json({
      success: true,
      carId,
      history: result.rows.map(row => ({
        tirePressure: {
          frontLeft: row.front_left,
          frontRight: row.front_right,
          rearLeft: row.rear_left,
          rearRight: row.rear_right
        },
        unit: row.unit,
        timestamp: row.recorded_at
      })),
      pagination: {
        count: result.rows.length,
        limit: parseInt(limit),
        offset: parseInt(offset)
      }
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
    console.error('Error fetching alert history:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch alert history' 
    });
  }
});

module.exports = router;
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

- [x] Review analysis excerpt and understand requirements
- [ ] Adapt the code template to specific feature needs
- [ ] Create `/routes/monitoring.js` with GET endpoints
- [ ] Create `/services/monitoringService.js` for data storage logic
- [ ] Add route to main server.js: `app.use('/api/monitoring', monitoringRouter)`
- [ ] Coordinate with B3 team: ensure `tire_pressure_readings` collection exists with indexes
- [ ] Coordinate with B4 team: ensure `tire_pressure_history` table exists
- [ ] Add unit tests for monitoring endpoints
- [ ] Add integration tests with B3 (MongoDB)
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Test with Postman/curl before A1 integration
- [ ] Add error handling and input validation
- [ ] Add logging for debugging

## Notes

- **Component**: B1 (Web Server API)
- **Effort**: 4 hours
- **Dependencies**: 
  - B3 (MongoDB): Needs `tire_pressure_readings` collection with index on `carId`
  - B4 (PostgreSQL): Needs `tire_pressure_history` table with indexes
  - B2 (WebSocket): Will notify clients via `io.emit()`
  - A1 (Mobile): Will consume these API endpoints
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
     ↓
C2 (Redis) stores latest readings
     ↓
C1 (Cloud Comm) fetches from Redis
     ↓
B2 (WebSocket) receives from C1
     ↓
B1 (YOU!) MonitoringService stores data
     ↓
B3 (MongoDB) stores current readings
     ↓
B4 (PostgreSQL) stores historical data
     ↓
B1 (YOU!) API returns data
     ↓
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

✅ What API endpoints to create  
✅ What data storage logic to implement  
✅ What database queries to write  
✅ What other components depend on you (A1, A2)  
✅ What components you depend on (B2, B3, B4)  
✅ Example code to start from  
✅ Estimated effort (4 hours)  
✅ Clear subtasks to complete  

**You DON'T need to understand**:
- How C5 generates sensor data
- How C2 Redis broker works
- How A1 renders the UI
- The full system architecture

**You ONLY need to focus on**: Your B1 API endpoints and data storage logic.

This is the power of component-level task breakdown! 🎯
