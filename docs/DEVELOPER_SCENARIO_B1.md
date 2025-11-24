# Developer Scenario: Getting B1 Requirements from Agent Analysis

## Scenario Overview

**Feature Request**: "Add real-time tire pressure alerts to the mobile app"

**Your Role**: Backend Developer (B1 - Web Server API)

**Goal**: Understand what API endpoints, database queries, and business logic you need to implement in the B1 Express server.

---

## Step 1: Run Jenkins Pipeline

### Trigger the AI Analysis

```bash
# Jenkins Pipeline Parameters:
FEATURE_REQUEST: "Add real-time tire pressure alerts to the mobile app"
USE_AI_AGENTS: true
OLLAMA_MODEL: llama3:8b
OUTPUT_FILE: tire-pressure-alerts-analysis.md
```

### What Happens Behind the Scenes

```
User Request: "Add real-time tire pressure alerts to mobile app"
     |
     v
[Agent A] Analyzes frontend impact
     |
     |--> A1 (Mobile): Needs alert notification UI
     |--> A2 (Web): Dashboard might need alert view
     |
     v
[Agent A decides]: Needs backend API → calls Agent B
     |
     v
[Agent B] Analyzes backend impact
     |
     |--> B1 (API): New alert endpoints needed ⬅️ YOUR WORK
     |--> B2 (WebSocket): Real-time push to clients
     |--> B3 (MongoDB): Alert storage and queries
     |--> B4 (PostgreSQL): Alert history/reporting
     |
     v
[Agent B decides]: Needs sensor data → calls Agent C
     |
     v
[Agent C] Analyzes in-car systems
     |
     |--> C5 (Sensors): Tire pressure monitoring
     |--> C2 (Redis): Alert threshold detection
     |--> C1 (Cloud Comm): Send alerts to backend
```

---

## Step 2: Download Your Task File

After Jenkins completes, download:

```
📁 analysis-reports/
  ├── tire-pressure-alerts-analysis.md  (full analysis)
  └── component-tasks/
      └── task-B1.md  ⬅️ YOUR FILE
```

---

## Step 3: Review task-B1.md

### Example Contents of task-B1.md

```markdown
# Task: B1

**Component**: B1  
**Technology**: Node.js/Express (REST API)  
**Effort Estimate**: 6 hours

Generated from analysis: `tire-pressure-alerts-analysis.md`

## Analysis Excerpt

Agent B Analysis - Component B1 (Web Server):
- Create new REST API endpoint: GET /api/alerts/tire-pressure/:carId
- Create new REST API endpoint: POST /api/alerts/tire-pressure/acknowledge
- Add alert filtering: by car, by severity, by time range
- Query B3 (MongoDB) for active alerts
- Query B4 (PostgreSQL) for historical alert data
- Implement alert threshold logic (pressure < 2.0 bar = critical)
- Return JSON with alert details, timestamp, and car info
- Add pagination for alert history (limit 50 per page)
- Integrate with B2 for real-time WebSocket notifications

Dependencies:
- B3 (MongoDB): alerts collection must exist
- B4 (PostgreSQL): alert_history table required
- A1 (Mobile): Will call these endpoints

## Proposed Implementation

### Example Code for B1

```javascript
// File: B1-web-server/routes/alerts.js
const express = require('express');
const router = express.Router();
const { ObjectId } = require('mongodb');

// GET /api/alerts/tire-pressure/:carId
// Returns active tire pressure alerts for a specific car
router.get('/tire-pressure/:carId', async (req, res) => {
  try {
    const { carId } = req.params;
    const { severity, limit = 50, offset = 0 } = req.query;
    
    // Query B3 (MongoDB) for active alerts
    const query = {
      carId,
      alertType: 'tire_pressure',
      status: 'active',
      ...(severity && { severity })
    };
    
    const alerts = await db.collection('alerts')
      .find(query)
      .sort({ timestamp: -1 })
      .skip(parseInt(offset))
      .limit(parseInt(limit))
      .toArray();
    
    // Enrich with car details
    const car = await db.collection('cars').findOne({ carId });
    
    res.json({
      success: true,
      carId,
      licensePlate: car?.licensePlate,
      alerts: alerts.map(alert => ({
        alertId: alert._id,
        severity: alert.severity, // 'warning' | 'critical'
        message: alert.message,
        tirePressure: {
          frontLeft: alert.data.frontLeft,
          frontRight: alert.data.frontRight,
          rearLeft: alert.data.rearLeft,
          rearRight: alert.data.rearRight
        },
        threshold: alert.threshold,
        timestamp: alert.timestamp,
        acknowledged: alert.acknowledged || false
      })),
      pagination: {
        total: await db.collection('alerts').countDocuments(query),
        limit: parseInt(limit),
        offset: parseInt(offset)
      }
    });
    
  } catch (error) {
    console.error('Error fetching alerts:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to fetch alerts' 
    });
  }
});

// POST /api/alerts/tire-pressure/acknowledge
// Mark an alert as acknowledged by the user
router.post('/tire-pressure/acknowledge', async (req, res) => {
  try {
    const { alertId, userId } = req.body;
    
    if (!alertId || !userId) {
      return res.status(400).json({ 
        success: false, 
        error: 'alertId and userId are required' 
      });
    }
    
    // Update alert in B3 (MongoDB)
    const result = await db.collection('alerts').updateOne(
      { _id: new ObjectId(alertId) },
      { 
        $set: { 
          acknowledged: true,
          acknowledgedBy: userId,
          acknowledgedAt: new Date()
        }
      }
    );
    
    if (result.matchedCount === 0) {
      return res.status(404).json({ 
        success: false, 
        error: 'Alert not found' 
      });
    }
    
    // Log to B4 (PostgreSQL) for history
    await pgPool.query(
      `INSERT INTO alert_acknowledgements 
       (alert_id, user_id, acknowledged_at) 
       VALUES ($1, $2, NOW())`,
      [alertId, userId]
    );
    
    // Notify via B2 (WebSocket) that alert was acknowledged
    io.emit('alert:acknowledged', { alertId, userId });
    
    res.json({
      success: true,
      alertId,
      message: 'Alert acknowledged successfully'
    });
    
  } catch (error) {
    console.error('Error acknowledging alert:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to acknowledge alert' 
    });
  }
});

// GET /api/alerts/tire-pressure/history/:carId
// Get historical alerts from B4 (PostgreSQL)
router.get('/tire-pressure/history/:carId', async (req, res) => {
  try {
    const { carId } = req.params;
    const { startDate, endDate, limit = 100 } = req.query;
    
    const query = `
      SELECT 
        ah.alert_id,
        ah.car_id,
        ah.severity,
        ah.message,
        ah.tire_data,
        ah.created_at,
        ah.resolved_at,
        aa.user_id as acknowledged_by,
        aa.acknowledged_at
      FROM alert_history ah
      LEFT JOIN alert_acknowledgements aa ON ah.alert_id = aa.alert_id
      WHERE ah.car_id = $1
        AND ah.alert_type = 'tire_pressure'
        ${startDate ? 'AND ah.created_at >= $2' : ''}
        ${endDate ? 'AND ah.created_at <= $3' : ''}
      ORDER BY ah.created_at DESC
      LIMIT $${startDate && endDate ? 4 : startDate || endDate ? 3 : 2}
    `;
    
    const params = [carId];
    if (startDate) params.push(startDate);
    if (endDate) params.push(endDate);
    params.push(limit);
    
    const result = await pgPool.query(query, params);
    
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

### Additional: Alert Creation Logic (Background Process)

```javascript
// File: B1-web-server/services/alertService.js
// This runs when B2 receives new sensor data from C1

class AlertService {
  constructor(db, io) {
    this.db = db;
    this.io = io; // WebSocket for real-time notifications
    this.CRITICAL_THRESHOLD = 2.0; // bar
    this.WARNING_THRESHOLD = 2.2; // bar
  }
  
  async checkTirePressure(carData) {
    const { carId, licensePlate, tirePressure, timestamp } = carData;
    
    // Check each tire against thresholds
    const alerts = [];
    
    for (const [position, pressure] of Object.entries(tirePressure)) {
      if (pressure < this.CRITICAL_THRESHOLD) {
        alerts.push({
          carId,
          licensePlate,
          alertType: 'tire_pressure',
          severity: 'critical',
          position,
          pressure,
          threshold: this.CRITICAL_THRESHOLD,
          message: `Critical: ${position} tire pressure ${pressure} bar (< ${this.CRITICAL_THRESHOLD})`,
          timestamp: new Date(timestamp)
        });
      } else if (pressure < this.WARNING_THRESHOLD) {
        alerts.push({
          carId,
          licensePlate,
          alertType: 'tire_pressure',
          severity: 'warning',
          position,
          pressure,
          threshold: this.WARNING_THRESHOLD,
          message: `Warning: ${position} tire pressure ${pressure} bar (< ${this.WARNING_THRESHOLD})`,
          timestamp: new Date(timestamp)
        });
      }
    }
    
    // Store alerts in B3 (MongoDB) if any found
    if (alerts.length > 0) {
      for (const alert of alerts) {
        // Check if alert already exists (avoid duplicates)
        const existing = await this.db.collection('alerts').findOne({
          carId: alert.carId,
          position: alert.position,
          status: 'active'
        });
        
        if (!existing) {
          const result = await this.db.collection('alerts').insertOne({
            ...alert,
            status: 'active',
            acknowledged: false,
            createdAt: new Date()
          });
          
          // Emit real-time notification via B2 WebSocket
          this.io.emit('alert:new', {
            alertId: result.insertedId,
            ...alert
          });
          
          console.log(`[ALERT] Created ${alert.severity} alert for ${carId} - ${alert.position}`);
        }
      }
    }
    
    return alerts;
  }
  
  async resolveAlert(alertId) {
    // Mark alert as resolved when pressure returns to normal
    await this.db.collection('alerts').updateOne(
      { _id: new ObjectId(alertId) },
      { 
        $set: { 
          status: 'resolved',
          resolvedAt: new Date()
        }
      }
    );
    
    this.io.emit('alert:resolved', { alertId });
  }
}

module.exports = AlertService;
```

## Suggested Subtasks

- [x] Review analysis excerpt and understand requirements
- [ ] Adapt the code template to specific feature needs
- [ ] Create `/routes/alerts.js` with GET and POST endpoints
- [ ] Create `/services/alertService.js` for alert logic
- [ ] Add route to main server.js: `app.use('/api/alerts', alertsRouter)`
- [ ] Coordinate with B3 team: ensure `alerts` collection exists with indexes
- [ ] Coordinate with B4 team: ensure `alert_history` and `alert_acknowledgements` tables exist
- [ ] Add unit tests for alert endpoints
- [ ] Add integration tests with B3 (MongoDB)
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Test with Postman/curl before A1 integration
- [ ] Add error handling and input validation
- [ ] Add logging for debugging

## Notes

- **Component**: B1 (Web Server API)
- **Effort**: 6 hours
- **Dependencies**: 
  - B3 (MongoDB): Needs `alerts` collection with indexes on `carId`, `status`, `timestamp`
  - B4 (PostgreSQL): Needs `alert_history` and `alert_acknowledgements` tables
  - B2 (WebSocket): Will notify clients via `io.emit()`
  - A1 (Mobile): Will consume these API endpoints
- **API Endpoints**:
  - `GET /api/alerts/tire-pressure/:carId` - Get active alerts
  - `POST /api/alerts/tire-pressure/acknowledge` - Acknowledge alert
  - `GET /api/alerts/tire-pressure/history/:carId` - Get alert history
- **Data Models**:
  - MongoDB `alerts` collection (active alerts)
  - PostgreSQL `alert_history` table (historical data)
  - PostgreSQL `alert_acknowledgements` table (user actions)
```

---

## Step 4: What You Need to Do

### As a B1 Developer:

1. **Read the task file** (`task-B1.md`)
2. **Copy the example code** as a starting point
3. **Coordinate with other teams**:
   - Ask B3 team: "Do we have the `alerts` collection?"
   - Ask B4 team: "Can you create the alert tables?"
   - Ask B2 team: "Can I emit `alert:new` events?"
4. **Implement the endpoints** in your B1 codebase
5. **Write tests** for your endpoints
6. **Create a small PR** focused only on B1 changes
7. **Update API docs** so A1 team knows how to call your endpoints

### Your Deliverables:

- `B1-web-server/routes/alerts.js` - API endpoints
- `B1-web-server/services/alertService.js` - Business logic
- `B1-web-server/tests/alerts.test.js` - Unit tests
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
B1 (YOU!) AlertService checks thresholds
     ↓
B3 (MongoDB) stores active alerts
     ↓
B1 (YOU!) API returns alerts
     ↓
A1 (Mobile) displays to user
```

### Your Touch Points:

- **Upstream (you receive from)**:
  - B2 sends you real-time sensor data via `alertService.checkTirePressure()`
  
- **Downstream (you send to)**:
  - B3: You store alerts in MongoDB
  - B4: You log history in PostgreSQL
  - B2: You emit WebSocket events for real-time updates
  - A1: You provide REST API endpoints

---

## Summary

**As a B1 developer, you now know**:

✅ What API endpoints to create  
✅ What business logic to implement  
✅ What database queries to write  
✅ What other components depend on you (A1, A2)  
✅ What components you depend on (B2, B3, B4)  
✅ Example code to start from  
✅ Estimated effort (6 hours)  
✅ Clear subtasks to complete  

**You DON'T need to understand**:
- How C5 generates sensor data
- How C2 Redis broker works
- How A1 renders the UI
- The full system architecture

**You ONLY need to focus on**: Your B1 API endpoints and alert logic.

This is the power of component-level task breakdown! 🎯
