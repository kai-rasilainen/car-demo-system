# Inter-Agent API Communication Protocol

## Overview

This document describes the API communication protocol between independent agents and their subcomponents when processing a user feature request. 

**Communication Architecture**: Strict hierarchical layering (A -> B -> C)
- **Agent A** only communicates with **Agent B**
- **Agent B** communicates with **Agent A** (upstream) and **Agent C** (downstream)
- **Agent C** only communicates with **Agent B**
- **Agent A never directly contacts Agent C**

The agents communicate via RESTful APIs or message queues to perform independent analysis and consolidate results.

## Agent and Component Hierarchy

### Agent A - Frontend (Entry Point)
- **A1**: Car User Mobile App (React Native)
- **A2**: Rental Staff Web App (React)
- **Communication**: Can only talk to Agent B

### Agent B - Backend (Middle Layer Orchestrator)
- **B1**: Web Server (Node.js/Express REST API)
- **B2**: IoT Gateway (WebSocket + REST)
- **B3**: Realtime Database (MongoDB)
- **B4**: Static Database (PostgreSQL)
- **Communication**: Can talk to Agent A (upstream) and Agent C (downstream)

### Agent C - In-Car Systems (Leaf Layer)
- **C1**: Cloud Communication (Python async)
- **C2**: Central Broker (Redis pub/sub)
- **C5**: Data Sensors (Python simulation)
- **Communication**: Can only talk to Agent B

## Component Communication Map

```
+-------------------------------------------------------------+
|                    Frontend Layer (Agent A)                 |
+-------------------------------------------------------------+
|  A1: Car User App          A2: Rental Staff App            |
|  (React Native)            (React Web)                      |
|       |                         |                           |
|       +-------------+-----------+                           |
+---------------------+---------------------------------------+
                      | REST API calls
+---------------------v---------------------------------------+
|                             Backend Layer (Agent B)         |
+-------------------------------------------------------------+
|  B1: Web Server (REST API) <---> B3: MongoDB (Realtime)    |
|  Port 3001                 |     Port 27017                |
|       |                    |                                |
|       +---> B4: PostgreSQL (Static)                        |
|            Port 5432                                        |
|                                                             |
|  B2: IoT Gateway (WebSocket) <---> B3: MongoDB (Cache)     |
|  Port 3002                   |                             |
|       |                      |                             |
+-------+----------------------+-----------------------------+
        | WebSocket            | Redis pub/sub
+-------v----------------------v-----------------------------+
|                             In-Car Layer (Agent C)          |
+-------------------------------------------------------------+
|  C1: Cloud Communication                                    |
|  (Python async, WebSocket client)                          |
|       |                                                     |
|       v get_latest_data_from_c2()                          |
|  C2: Central Broker (Redis pub/sub)                        |
|  Port 6379                                                  |
|  Channels: sensors:*, vehicle:*, commands:*                |
|       ^                                                     |
|       | publish sensor data                                |
|  C5: Data Sensors (Python simulation)                      |
|  (Temperature, GPS, Battery, Speed, Tire Pressure)         |
+-------------------------------------------------------------+
```

## Agent Endpoints

### Agent A - Frontend Analysis (Entry Point)
**Base URL**: `https://agent-a.example.com/api/v1`

**Components**: A1 (Mobile), A2 (Web)

### Agent B - Backend Analysis
**Base URL**: `https://agent-b.example.com/api/v1`

**Components**: B1 (REST), B2 (IoT), B3 (Mongo), B4 (Postgres)

### Agent C - In-Car Systems Analysis
**Base URL**: `https://agent-c.example.com/api/v1`

**Components**: C1 (Cloud Comm), C2 (Broker), C5 (Sensors)

---

## API Flow Sequence

```
User Request
     |
     v
[1] POST /feature-request -> Agent A
     |
     v
[2] POST /analyze-backend -> Agent B
     |
     v
[3] Agent B determines if C needed
     |
     +--[4] POST /analyze-incar -> Agent C
             |
             v
        [5] Response <- Agent C
     |
     v
[6] Agent B consolidates (B analysis + C response)
     |
     v
[7] Response <- Agent B (includes C data)
     |
     v
[8] Agent A consolidates (A analysis + B response)
     |
     v
[9] Response -> User
```

**Key Point**: Agent A never directly contacts Agent C. All C interactions go through B.

---

## 1. User Submits Feature Request to Agent A

### Request
```http
POST /api/v1/feature-request
Host: agent-a.example.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "request_id": "req-2025-11-19-001",
  "feature": "Add tire pressure monitoring to car dashboard",
  "priority": "medium",
  "user_id": "user-123",
  "timestamp": "2025-11-19T10:00:00Z"
}
```

### Response (Immediate)
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "request_id": "req-2025-11-19-001",
  "status": "processing",
  "message": "Feature request accepted. Agent A is analyzing...",
  "estimated_completion": "2025-11-19T10:05:00Z",
  "tracking_url": "https://agent-a.example.com/api/v1/status/req-2025-11-19-001"
}
```

---

## 2. Agent A Requests Backend Analysis from Agent B

After Agent A performs its independent frontend analysis (considering A1 and A2 impacts), it determines that backend changes are needed across multiple components.

### Request
```http
POST /api/v1/analyze-backend
Host: agent-b.example.com
Content-Type: application/json
Authorization: Bearer <agent-a-token>
X-Request-ID: req-2025-11-19-001
X-Source-Agent: agent-a
X-Correlation-ID: corr-2025-11-19-001

{
  "request_id": "req-2025-11-19-001",
  "feature": "Add tire pressure monitoring to car dashboard",
  "frontend_analysis": {
    "ui_impact": "medium",
    "components_affected": [
      {
        "component": "A1",
        "name": "Car User Mobile App",
        "changes": ["Add tire pressure gauge widget", "Add alert for low pressure"],
        "effort_hours": 4
      },
      {
        "component": "A2",
        "name": "Rental Staff Web App",
        "changes": ["Add tire pressure to fleet monitoring", "Add maintenance alerts"],
        "effort_hours": 3
      }
    ],
    "frontend_total_effort_hours": 7
  },
  "backend_requirements": {
    "api_changes": {
      "affected_components": ["B1", "B2", "B3"],
      "b1_changes": {
        "endpoint": "GET /api/car/:licensePlate",
        "new_fields": [
          {
            "name": "tirePressure",
            "type": "object",
            "structure": {
              "frontLeft": "number",
              "frontRight": "number",
              "rearLeft": "number",
              "rearRight": "number",
              "timestamp": "ISO8601",
              "unit": "bar"
            },
            "range": "1.5-4.0 bar",
            "update_frequency": "10 seconds"
          }
        ]
      },
      "b2_changes": {
        "websocket_event": "tire-pressure-update",
        "realtime_streaming": true
      },
      "b3_changes": {
        "collection": "cars",
        "new_field": "tirePressure",
        "indexes_needed": true
      }
    },
    "data_source": "C5 sensor data via C2 broker",
    "real_time": true
  },
  "questions": [
    "Can B1 REST API provide this tire pressure data?",
    "Can B2 stream real-time updates via WebSocket?",
    "Will B3 MongoDB handle the write throughput?",
    "Does B4 PostgreSQL need schema changes for historical data?",
    "What is the implementation effort across B1-B4?",
    "Are there any performance concerns?"
  ]
}
```

### Response from Agent B
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-b
X-Response-Time: 2.3s

{
  "request_id": "req-2025-11-19-001",
  "agent": "agent-b",
  "analysis_timestamp": "2025-11-19T10:01:30Z",
  "status": "feasible",
  "impact_level": "medium",
  
  "component_analysis": {
    "b1_web_server": {
      "api_changes": {
        "endpoint": "GET /api/car/:licensePlate",
        "modifications": [
          {
            "change": "Add tirePressure field to response schema",
            "effort_hours": 2,
            "breaking_change": false,
            "requires_version_bump": false
          },
          {
            "change": "Add data validation for tire pressure range",
            "effort_hours": 0.5
          }
        ],
        "data_source": "B3 MongoDB cars collection",
        "testing_effort": 1
      }
    },
    
    "b2_iot_gateway": {
      "changes": [
        {
          "change": "Accept tire_pressure messages from Redis (C2)",
          "effort_hours": 2,
          "message_format": "JSON with frontLeft/frontRight/rearLeft/rearRight"
        },
        {
          "change": "Stream real-time updates via WebSocket to A2",
          "effort_hours": 1.5,
          "event_name": "tire-pressure-update"
        },
        {
          "change": "Cache latest tire pressure in B3",
          "effort_hours": 1
        }
      ],
      "throughput_estimate": "100 msgs/sec per car",
      "testing_effort": 2
    },
    
    "b3_mongodb": {
      "collection": "cars",
      "schema_changes": [
        {
          "field": "tirePressure",
          "type": "Object",
          "structure": {
            "frontLeft": "Number (1.5-4.0)",
            "frontRight": "Number (1.5-4.0)",
            "rearLeft": "Number (1.5-4.0)",
            "rearRight": "Number (1.5-4.0)",
            "timestamp": "Date",
            "unit": "String (default: 'bar')"
          },
          "migration_required": false,
          "effort_hours": 0.5
        }
      ],
      "index_changes": [
        {
          "field": "tirePressure.timestamp",
          "type": "descending",
          "purpose": "Quick retrieval of latest reading",
          "effort_hours": 0.25
        }
      ],
      "performance_impact": "minimal - flexible schema",
      "testing_effort": 1
    },
    
    "b4_postgresql": {
      "changes_needed": false,
      "reason": "Tire pressure is real-time data, stored in B3 only",
      "optional_enhancement": "Could add tire_pressure_history table for analytics",
      "effort_if_implemented": 4
    }
  },
  
  "effort_estimate": {
    "total_hours": 10.75,
    "breakdown": {
      "b1_web_server": 3.5,
      "b2_iot_gateway": 4.5,
      "b3_mongodb": 0.75,
      "b4_postgresql": 0,
      "testing": 2
    }
  },
  
  "dependencies": [
    {
      "agent": "agent-c",
      "requirement": "Tire pressure sensor data from C5 via C2 Redis channel 'sensors:tire_pressure'",
      "critical": true,
      "data_format": "JSON: {carId, frontLeft, frontRight, rearLeft, rearRight, timestamp}"
    }
  ],
  
  "risks": [
    {
      "level": "low",
      "component": "B3",
      "description": "MongoDB storage growth approximately 100 bytes per car per 10 seconds",
      "mitigation": "Implement TTL index (keep 7 days)"
    },
    {
      "level": "low",
      "component": "B2",
      "description": "WebSocket connection load for 1000+ cars",
      "mitigation": "Connection pooling and rate limiting already in place"
    }
  ],
  
  "test_requirements": [
    "B1: Unit tests for API endpoint with tire pressure field",
    "B2: Integration tests for Redis -> B2 -> B3 data flow",
    "B2: WebSocket streaming test",
    "B3: MongoDB write/read performance test",
    "B2: Load testing for real-time updates with 1000+ cars"
  ],
  
  "incar_dependency": {
    "required": true,
    "description": "Need to request sensor data from Agent C",
    "next_action": "Request analysis from Agent C"
  },
  
  "recommendation": "feasible_pending_c_response",
  "notes": "Backend implementation is straightforward. Will proceed to request Agent C analysis for sensor data availability."
}
```

---

## 3. Agent B Requests In-Car Analysis from Agent C

**IMPORTANT**: Agent B (not Agent A) determines that in-car sensor data is needed and requests analysis from Agent C.

### Request
```http
POST /api/v1/analyze-incar
Host: agent-c.example.com
Content-Type: application/json
Authorization: Bearer <agent-b-token>
X-Request-ID: req-2025-11-19-001
X-Source-Agent: agent-b
X-Correlation-ID: corr-2025-11-19-001

{
  "request_id": "req-2025-11-19-001",
  "feature": "Add tire pressure monitoring to car dashboard",
  "requesting_agent": "agent-b",
  "backend_context": {
    "data_needed": "tire_pressure sensor data",
    "consuming_component": "B2 IoT Gateway",
    "storage_component": "B3 MongoDB",
    "api_endpoint": "GET /api/car/:licensePlate"
  },
  "sensor_requirements": {
  },
  "sensor_requirements": {
    "sensor_type": "tire_pressure",
    "data_points": ["frontLeft", "frontRight", "rearLeft", "rearRight"],
    "data_type": "number",
    "unit": "bar",
    "range": "1.5-4.0",
  "sensor_requirements": {
    "sensor_type": "tire_pressure",
    "data_points": ["frontLeft", "frontRight", "rearLeft", "rearRight"],
    "data_type": "number",
    "unit": "bar",
    "range": "1.5-4.0",
    "update_frequency": "10 seconds",
    "communication_flow": "C5 -> C2 (Redis) -> C1 -> B2",
    "redis_channel": "sensors:tire_pressure",
    "target_backend_component": "B2 IoT Gateway"
  },
  "questions": [
    "Can C5 sensors provide tire pressure data?",
    "Is sensor hardware available or needs simulation?",
    "Can C2 broker handle additional sensor channel?",
    "Can C1 cloud communication relay to B2?",
    "What is the implementation effort across C1, C2, C5?",
    "Any vehicle compatibility issues?"
  ]
}
```

### Response from Agent C to Agent B
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-c
X-Response-Time: 1.8s

{
  "request_id": "req-2025-11-19-001",
  "agent": "agent-c",
  "responding_to": "agent-b",
  "analysis_timestamp": "2025-11-19T10:02:15Z",
  "status": "feasible",
  "impact_level": "low-medium",
        "task": "Subscribe to tire pressure sensor channel",
  "analysis_timestamp": "2025-11-19T10:02:15Z",
  "status": "feasible",
  "impact_level": "low-medium",
  
  "component_analysis": {
    "c5_data_sensors": {
      "task": "Add tire pressure sensor simulation",
      "details": [
        "Implement TirePressureSensor class",
        "Generate realistic values (2.0-2.5 bar normal range)",
        "Add random fluctuation ±0.1 bar",
        "Simulate slow leak scenario (-0.01 bar/minute)",
        "Publish to C2 Redis every 10 seconds"
      ],
      "effort_hours": 3,
      "language": "Python",
      "file_location": "C-car-demo-in-car/C5-data-sensors/sensors/tire_pressure.py",
      "testing": "pytest with sensor mock"
    },
    
    "c2_central_broker": {
      "task": "Add tire pressure channel subscription",
      "details": [
        "Subscribe to 'sensors:tire_pressure' channel",
        "Aggregate tire pressure data from all 4 sensors",
        "Forward aggregated data to C1 via existing mechanism",
        "Add channel to pub/sub configuration"
      ],
      "effort_hours": 1,
      "configuration_change": true,
      "file_location": "C-car-demo-in-car/C2-central-broker/config/channels.js",
      "testing": "Redis pub/sub integration test"
    },
    
    "c1_cloud_communication": {
      "task": "No changes required",
      "details": [
        "Existing get_latest_data_from_c2() already fetches all sensor data from C2",
        "Existing WebSocket connection to B2 handles all sensor types",
        "Data automatically flows: C5 -> C2 -> C1 -> B2"
      ],
      "effort_hours": 0,
      "reason": "Generic sensor data pipeline already in place"
    }
  },
  
  "data_flow": {
    "path": "C5 -> C2 (Redis pub/sub) -> C1 (async fetch) -> B2 (WebSocket)",
    "redis_channel": "sensors:tire_pressure",
    "message_format": {
      "type": "sensor_data",
      "sensor": "tire_pressure",
      "carId": "car-001",
      "licensePlate": "ABC-123",
      "data": {
        "frontLeft": 2.3,
        "frontRight": 2.4,
        "rearLeft": 2.2,
        "rearRight": 2.2
      },
      "timestamp": "2025-11-19T10:02:00Z",
      "unit": "bar"
    },
    "publish_frequency": "10 seconds",
    "data_retention": "Latest value only in C2"
  },
  
  "effort_estimate": {
    "total_hours": 4,
    "breakdown": {
      "c5_simulator": 3,
      "c2_subscription": 1,
      "c1_changes": 0
    },
    "testing": 2
  },
  
  "risks": [
    {
      "level": "low",
      "component": "C5",
      "description": "Simulated data may not reflect real sensor behavior",
      "mitigation": "Add realistic value ranges, temperature correlation, and slow leak patterns"
    },
    {
      "level": "low",
      "component": "C2",
      "description": "Additional Redis channel increases message throughput",
      "mitigation": "Redis handles 100k+ ops/sec easily, no concern"
    }
  ],
  
  "test_requirements": [
    "C5: Unit tests for TirePressureSensor class with pytest",
    "C5: Test realistic value generation and fluctuation",
    "C2: Integration test for sensors:tire_pressure channel",
    "C2: Test message aggregation and forwarding",
    "E2E: Test complete flow C5 -> C2 -> C1 -> B2 -> B1 -> A1"
  ],
  
  "hardware_notes": "For production with real vehicles, requires TPMS (Tire Pressure Monitoring System) integration via CAN bus. Current simulation sufficient for demo.",
  
  "recommendation": "proceed",
  "notes": "Simulation is straightforward. Can be upgraded to real TPMS hardware when available."
}
```

---

## 4. Agent B Consolidates B + C Analysis

Agent B receives Agent C's response and creates a consolidated backend analysis including in-car layer results.

### Consolidated Response from Agent B to Agent A
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-b
X-Consulted-Agents: agent-c
X-Response-Time: 4.5s

{
  "request_id": "req-2025-11-19-001",
  "agent": "agent-b",
  "responding_to": "agent-a",
  "analysis_timestamp": "2025-11-19T10:02:30Z",
  "status": "feasible",
  "impact_level": "medium",
  
  "backend_summary": {
    "b1_api": "Modify GET /api/car/:licensePlate - 2.5 hrs",
    "b2_iot": "Accept sensor data, stream via WebSocket - 4.5 hrs",
    "b3_database": "Add tirePressure field - 0.75 hrs",
    "b4_database": "No changes needed",
    "backend_total": "7.75 hours"
  },
  
  "incar_summary": {
    "data_source_available": true,
    "c5_sensors": "Tire pressure simulation - 3 hrs",
    "c2_broker": "Add Redis channel - 1 hr",
    "c1_communication": "No changes needed",
    "incar_total": "4 hours",
    "data_flow": "C5 -> C2 -> C1 -> B2 -> B3 -> B1"
  },
  
  "complete_backend_effort": {
    "total_hours": 11.75,
    "backend_layer": 7.75,
    "incar_layer": 4.0,
    "testing": 2.0
  },
  
  "recommendation": "proceed",
  "notes": "Complete backend stack (including in-car) can provide tire pressure data. Agent A only needs to consume the REST API - all backend/in-car complexity is handled by Agent B layer."
}
```

---

## 5. Agent A Consolidates and Responds to User

After receiving the consolidated response from Agent B (which includes Agent C's analysis), Agent A creates the final assessment.

**Note**: Agent A never directly contacted Agent C - all in-car information came through Agent B.

### Final Response to User
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-a
X-Consulted-Agents: agent-b
X-Total-Analysis-Time: 5.2s

{
  "request_id": "req-2025-11-19-001",
  "feature": "Add tire pressure monitoring to car dashboard",
  "analysis_timestamp": "2025-11-19T10:03:00Z",
  "status": "feasible",
  "recommendation": "proceed",
  
  "consolidated_assessment": {
    "overall_impact": "medium",
    "feasibility": "high",
    "breaking_changes": false,
    
    "total_effort": {
      "hours": 18.75,
      "days": 2.3,
      "breakdown": {
        "frontend": 7.0,
        "backend_complete": 11.75
      }
    },
    
    "implementation_phases": [
      {
        "phase": 1,
        "name": "Backend & Sensor Implementation",
        "owner": "backend-team",
        "duration_hours": 11.75,
        "components": ["B1", "B2", "B3", "C5", "C2"],
        "blocking": true,
        "reason": "Frontend depends on API availability"
      },
      {
        "phase": 2,
        "name": "Backend Data Pipeline",
        "agent": "agent-b",
        "duration_hours": 4,
        "components": ["B2-iot-gateway", "B1-web-server", "B3-mongodb"],
        "blocking": true,
        "reason": "Frontend depends on API"
      },
      {
        "phase": 3,
        "name": "Frontend UI Implementation",
        "agent": "agent-a",
        "duration_hours": 6,
        "components": ["A1-mobile-app", "A2-staff-web"],
        "blocking": false
      }
    ],
    
    "agent_analyses": {
      "agent_a_frontend": {
        "impact": "medium",
        "effort_hours": 6,
        "components": ["A1-mobile-app", "A2-staff-web"],
        "changes": [
          "Add tire pressure gauge component",
          "Show real-time pressure values",
          "Display warnings for low pressure",
          "Integrate with existing car status API"
        ],
        "risks": []
      },
      
      "agent_b_backend": {
        "impact": "medium",
        "effort_hours": 4,
        "components": ["B1-web-server", "B2-iot-gateway", "B3-mongodb"],
        "changes": [
          "Add tirePressure field to API response",
          "Ingest tire pressure from Redis",
          "Store in MongoDB car_data collection"
        ],
        "risks": [
          {
            "level": "low",
            "description": "Storage growth",
            "mitigation": "7-day retention policy"
          }
        ],
        "dependencies": ["agent-c sensor data"]
      },
      
      "agent_c_incar": {
        "impact": "low-medium",
        "effort_hours": 4,
        "components": ["C5-data-sensors", "C2-central-broker"],
        "changes": [
          "Create tire pressure sensor simulator",
          "Subscribe to sensor channel in broker",
          "Forward to cloud via existing connection"
        ],
        "risks": [
          {
            "level": "low",
            "description": "Simulated data limitations",
            "mitigation": "Realistic value patterns"
          }
        ]
      }
    },
    
    "risks_summary": [
      {
        "level": "low",
        "source": "agent-b",
        "description": "MongoDB storage growth",
        "mitigation": "Implement 7-day data retention"
      },
      {
        "level": "low",
        "source": "agent-c",
        "description": "Simulated sensor data",
        "mitigation": "Use realistic value ranges"
      }
    ],
    
    "test_strategy": {
      "unit_tests": [
        "Frontend component tests (Agent A)",
        "Backend API tests (Agent B)",
        "Sensor simulator tests (Agent C)"
      ],
      "integration_tests": [
        "C5 -> C2 -> C1 data flow (Agent C)",
        "B2 -> B3 data storage (Agent B)",
        "Frontend API integration (Agent A)"
      ],
      "e2e_tests": [
        "Sensor -> Cloud -> API -> UI complete flow",
        "Real-time updates on dashboard",
        "Low pressure warnings"
      ],
      "estimated_test_effort": 2
    },
    
    "timeline": {
      "week_1": {
        "day_1-2": "Agent C implements sensor (4h)",
        "day_2-3": "Agent B implements backend (4h)",
        "day_3-4": "Agent A implements frontend (6h)",
        "day_5": "Integration testing (2h)"
      },
      "total_duration": "5 days"
    }
  },
  
  "code_examples_available": true,
  "code_examples_url": "https://agent-a.example.com/api/v1/code-examples/req-2025-11-19-001",
  
  "implementation_plan_url": "https://agent-a.example.com/api/v1/implementation-plan/req-2025-11-19-001",
  
  "next_steps": [
    "Review consolidated assessment",
    "Approve feature for implementation",
    "Agent C begins sensor implementation",
    "Agent B prepares backend pipeline",
    "Agent A prepares frontend components"
  ]
}
```

---

## 5. Status Polling API

Users can poll the status of their request while agents are processing.

### Request
```http
GET /api/v1/status/req-2025-11-19-001
Host: agent-a.example.com
Authorization: Bearer <token>
```

### Response (During Processing)
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "request_id": "req-2025-11-19-001",
  "status": "processing",
  "progress": {
    "agent_a_analysis": "completed",
    "agent_b_consultation": "in_progress",
    "agent_c_consultation": "in_progress",
    "consolidation": "pending"
  },
  "estimated_completion": "2025-11-19T10:03:00Z"
}
```

---

## Error Handling

### Agent Unavailable
```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json

{
  "request_id": "req-2025-11-19-001",
  "error": "agent_unavailable",
  "agent": "agent-b",
  "message": "Agent B is currently unavailable. Request queued for retry.",
  "retry_after": 30,
  "fallback": "Agent A will provide partial analysis without backend assessment"
}
```

### Invalid Request
```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "invalid_request",
  "message": "Feature description is required",
  "details": {
    "missing_fields": ["feature"]
  }
}
```

### Timeout
```http
HTTP/1.1 504 Gateway Timeout
Content-Type: application/json

{
  "request_id": "req-2025-11-19-001",
  "error": "timeout",
  "message": "Agent C did not respond within 30 seconds",
  "partial_results": {
    "agent_a_analysis": {...},
    "agent_b_analysis": {...}
  },
  "note": "Proceeding with partial analysis. Agent C can be consulted separately."
}
```

---

## Authentication & Authorization

All inter-agent API calls use JWT tokens for authentication:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Payload**:
```json
{
  "agent_id": "agent-a",
  "region": "cloud-region-1",
  "permissions": ["request_analysis", "consolidate_results"],
  "iat": 1700390400,
  "exp": 1700394000
}
```

---

## Rate Limiting

Each agent has rate limits to prevent overload:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700390460
```

**Rate exceeded response**:
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please retry after 60 seconds.",
  "limit": 100,
  "window": "1 minute"
}
```

---

## Webhooks (Optional)

Agents can register webhooks to be notified when analysis is complete:

### Register Webhook
```http
POST /api/v1/webhooks
Host: agent-a.example.com
Content-Type: application/json

{
  "url": "https://client.example.com/webhook/feature-analysis",
  "events": ["analysis_complete", "analysis_failed"],
  "secret": "webhook-secret-key"
}
```

### Webhook Payload
```http
POST /webhook/feature-analysis
Host: client.example.com
Content-Type: application/json
X-Webhook-Signature: sha256=...

{
  "event": "analysis_complete",
  "request_id": "req-2025-11-19-001",
  "timestamp": "2025-11-19T10:03:00Z",
  "result_url": "https://agent-a.example.com/api/v1/results/req-2025-11-19-001"
}
```

---

## Complete Component Data Flow Example

### Tire Pressure Monitoring - End-to-End Flow

**Agent Communication Flow**: User -> A -> B -> C (then back: C -> B -> A -> User)

```
+--------------------------------------------------------------------+
|                      User Layer                                    |
|                                                                    |
|  User opens A1 (Mobile) or A2 (Web) app                           |
|     Requests tire pressure for car "ABC-123"                      |
+--------------------------+-------------------------------------+
                           | HTTP GET /api/car/ABC-123
+--------------------------v-------------------------------------+
|                  Frontend Layer (Agent A)                          |
|              [NO] Cannot talk to Agent C directly                  |
+--------------------------------------------------------------------+
|  A1: Mobile App (React Native)                                     |
|     - Displays tire pressure gauge                                 |
|     - Shows warning if pressure < 2.0 bar                         |
|                                                                    |
|  A2: Staff Web App (React)                                        |
|     - Fleet monitoring dashboard                                   |
|     - Real-time alerts for all vehicles                           |
+--------------------------+-------------------------------------+
                           | API Call: GET /api/car/ABC-123
                           | (Agent A only talks to Agent B)
+--------------------------v-------------------------------------+
|                   Backend Layer (Agent B)                          |
|         [YES] Can talk to Agent A (up) and Agent C (down)          |
+--------------------------------------------------------------------+
|  B1: Web Server (Express) Port 3001                               |
|     - Receives API request from A                                  |
|     - Queries B3 for car data                                      |
|     - Returns JSON with tirePressure field                         |
|          |                                                         |
|          v MongoDB query                                           |
|  B3: MongoDB Port 27017                                           |
|     - Collection: cars                                             |
|     - Document: {                                                  |
|         licensePlate: "ABC-123",                                   |
|         tirePressure: {                                            |
|           frontLeft: 2.3,                                          |
|           frontRight: 2.4,                                         |
|           rearLeft: 2.2,                                           |
|           rearRight: 2.2,                                          |
|           timestamp: "2025-11-19T10:02:00Z"                       |
|         }                                                          |
|       }                                                            |
|                                                                    |
|  B2: IoT Gateway (WebSocket) Port 3002                            |
|     - Receives sensor data from C1                                 |
|     - Updates B3 MongoDB in real-time                             |
|     - Streams updates to A2 via WebSocket                         |
|          ^ WebSocket connection from C1                            |
+----------+----------------------------------------------------------+
           | sensor data stream (B requests from C)
+----------v----------------------------------------------------------+
|                  In-Car Layer (Agent C)                            |
|              [NO] Cannot talk to Agent A directly                  |
|              [YES] Only responds to Agent B requests               |
|                  In-Car Layer (Agent C)                            |
+--------------------------------------------------------------------+
|  C1: Cloud Communication (Python async)                           |
|     - get_latest_data_from_c2() every 10 sec                      |
|     - Reads from C2 Redis                                          |
|     - Sends to B2 via WebSocket                                    |
|          ^                                                         |
|          | Redis GET                                               |
|  C2: Central Broker (Redis) Port 6379                             |
|     - Pub/Sub channels:                                            |
|       - sensors:tire_pressure                                      |
|     - Stores latest tire pressure data                             |
|     - Key: sensors:tire_pressure:ABC-123                          |
|          ^                                                         |
|          | PUBLISH                                                 |
|  C5: Data Sensors (Python simulation)                             |
|     - TirePressureSensor class                                     |
|     - Generates realistic data every 10 sec:                       |
|       {                                                            |
|         carId: "car-001",                                          |
|         licensePlate: "ABC-123",                                   |
|         frontLeft: 2.3,  <- Random 2.0-2.5 bar                    |
|         frontRight: 2.4, <- +/-0.1 bar fluctuation                |
|         rearLeft: 2.2,   <- Slow leak simulation                  |
|         rearRight: 2.2,                                            |
|         timestamp: ISO8601                                         |
|       }                                                            |
|     - Publishes to Redis channel                                   |
+--------------------------------------------------------------------+

Data Flow Summary:
  C5 (generate) -> C2 (Redis pub/sub) -> C1 (async fetch) -> 
  B2 (WebSocket) -> B3 (MongoDB store) -> B1 (REST API) -> 
  A1/A2 (display)

Agent Communication Flow (strict hierarchy):
  User -> A -> B -> C (for analysis)
  C -> B -> A -> User (for response)
  
  [NO] A never directly contacts C
  [YES] All C interactions go through B

Update Frequency: Every 10 seconds
Latency: < 100ms from C5 to A1/A2
```

---

## Summary

This API protocol enables:

1. [YES] **Strict Hierarchical Architecture**: A -> B -> C (no A to C direct communication)
2. [YES] **Distributed Components**: Agents operate independently with specialized subcomponents (A1/A2, B1-B4, C1/C2/C5)
3. [YES] **Layered Orchestration**: Agent B acts as middle layer orchestrator between A and C
4. [YES] **Consolidated Results**: Agent B consolidates C response, Agent A consolidates B response
5. [YES] **Clear Data Flow**: Well-defined paths from sensors through backend to frontend
6. [YES] **Separation of Concerns**: Frontend (A) doesn't need to know about in-car complexity (C)
7. [YES] **Error Resilience**: Graceful degradation when agents are unavailable
8. [YES] **Security**: JWT authentication and rate limiting
9. [YES] **Traceability**: Request IDs and correlation IDs for debugging

The protocol supports the strict hierarchical model where:
- **Agent A** (A1, A2) is the user entry point and only talks to Agent B
- **Agent B** (B1, B2, B3, B4) is the orchestration layer, talks to A (upstream) and C (downstream)
- **Agent C** (C1, C2, C5) handles in-car systems and only responds to Agent B
- All communication follows the chain: A <-> B <-> C (never A <-> C)
- Agent B shields Agent A from in-car complexity
- Results flow back through the same hierarchy