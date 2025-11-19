# Inter-Agent API Communication Protocol

## Overview

This document describes the API communication protocol between geographically distributed agents when processing a user feature request. The agents communicate via RESTful APIs or message queues to perform independent analysis and consolidate results.

## Agent Endpoints

### Agent A - Frontend Analysis (Entry Point)
**Location**: Cloud Region 1 (e.g., AWS us-east-1)
**Base URL**: `https://agent-a.cloud-region-1.example.com/api/v1`

### Agent B - Backend Analysis
**Location**: Cloud Region 2 (e.g., AWS us-west-2)
**Base URL**: `https://agent-b.cloud-region-2.example.com/api/v1`

### Agent C - In-Car Systems Analysis
**Location**: Edge Infrastructure (Vehicle/Simulator)
**Base URL**: `https://agent-c.edge.example.com/api/v1`

---

## API Flow Sequence

```
User Request
     |
     v
[1] POST /feature-request -> Agent A
     |
     +--[2] POST /analyze-backend -> Agent B
     |       |
     |       v
     |  [3] Response <- Agent B
     |
     +--[4] POST /analyze-incar -> Agent C
             |
             v
        [5] Response <- Agent C
     |
     v
[6] Consolidation by Agent A
     |
     v
[7] Response -> User
```

---

## 1. User Submits Feature Request to Agent A

### Request
```http
POST /api/v1/feature-request
Host: agent-a.cloud-region-1.example.com
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
  "tracking_url": "https://agent-a.cloud-region-1.example.com/api/v1/status/req-2025-11-19-001"
}
```

---

## 2. Agent A Requests Backend Analysis from Agent B

After Agent A performs its independent frontend analysis, it determines that backend changes are needed.

### Request
```http
POST /api/v1/analyze-backend
Host: agent-b.cloud-region-2.example.com
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
    "components_affected": ["A1-mobile-app", "A2-staff-web"],
    "frontend_effort_hours": 6
  },
  "backend_requirements": {
    "api_changes": {
      "endpoint": "GET /api/car/:licensePlate",
      "new_fields": [
        {
          "name": "tirePressure",
          "type": "object",
          "structure": {
            "frontLeft": "number",
            "frontRight": "number",
            "rearLeft": "number",
            "rearRight": "number"
          },
          "range": "1.5-4.0 bar",
          "update_frequency": "10 seconds"
        }
      ]
    },
    "data_source": "sensor_data",
    "real_time": true
  },
  "questions": [
    "Can backend provide this tire pressure data?",
    "What is the data source?",
    "What is the implementation effort?",
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
  
  "backend_analysis": {
    "api_changes": {
      "endpoint": "GET /api/car/:licensePlate",
      "modifications": [
        {
          "component": "B1-web-server",
          "change": "Add tirePressure field to response schema",
          "effort_hours": 2,
          "breaking_change": false
        }
      ]
    },
    
    "data_ingestion": {
      "component": "B2-iot-gateway",
      "changes": [
        {
          "change": "Accept tire_pressure messages from Redis",
          "effort_hours": 2
        }
      ]
    },
    
    "database_changes": {
      "component": "B3-mongodb",
      "changes": [
        {
          "collection": "car_data",
          "field": "tirePressure",
          "schema": {
            "frontLeft": {"type": "Number", "required": true},
            "frontRight": {"type": "Number", "required": true},
            "rearLeft": {"type": "Number", "required": true},
            "rearRight": {"type": "Number", "required": true},
            "timestamp": {"type": "Date", "required": true}
          },
          "migration_required": false,
          "effort_hours": 0.5
        }
      ]
    },
    
    "effort_estimate": {
      "total_hours": 4,
      "breakdown": {
        "B1_api": 2,
        "B2_ingestion": 2,
        "B3_database": 0
      }
    },
    
    "dependencies": [
      {
        "agent": "agent-c",
        "requirement": "Tire pressure sensor data via Redis channel 'sensors:tire_pressure'",
        "critical": true
      }
    ],
    
    "risks": [
      {
        "level": "low",
        "description": "MongoDB storage growth approximately 100 bytes per car per 10 seconds",
        "mitigation": "Implement data retention policy (keep 7 days)"
      }
    ],
    
    "test_requirements": [
      "Unit tests for API endpoint",
      "Integration tests for B2 -> B3 data flow",
      "Load testing for real-time updates"
    ]
  },
  
  "recommendation": "proceed",
  "notes": "Backend implementation is straightforward. Main dependency is on Agent C providing sensor data."
}
```

---

## 3. Agent A Requests In-Car Analysis from Agent C

After receiving Agent B's response, Agent A also sends a request to Agent C.

### Request
```http
POST /api/v1/analyze-incar
Host: agent-c.edge.example.com
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
    "components_affected": ["A1-mobile-app", "A2-staff-web"],
    "frontend_effort_hours": 6
  },
  "backend_requirements": {
    "data_needed": "tire_pressure",
    "format": "JSON via Redis",
    "frequency": "every 10 seconds"
  },
  "sensor_requirements": {
    "sensor_type": "tire_pressure",
    "data_points": [
      "frontLeft",
      "frontRight",
      "rearLeft",
      "rearRight"
    ],
    "data_type": "number",
    "unit": "bar",
    "range": "1.5-4.0",
    "update_frequency": "10 seconds",
    "redis_channel": "sensors:tire_pressure"
  },
  "questions": [
    "Can in-car systems provide tire pressure sensor data?",
    "Is sensor hardware available or needs simulation?",
    "What is the implementation effort?",
    "Any vehicle compatibility issues?"
  ]
}
```

### Response from Agent C
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-c
X-Response-Time: 1.8s

{
  "request_id": "req-2025-11-19-001",
  "agent": "agent-c",
  "analysis_timestamp": "2025-11-19T10:02:15Z",
  "status": "feasible",
  "impact_level": "low-medium",
  
  "incar_analysis": {
    "sensor_availability": {
      "hardware_available": false,
      "simulation_required": true,
      "component": "C5-data-sensors"
    },
    
    "implementation": [
      {
        "component": "C5-data-sensors",
        "task": "Create tire pressure sensor simulator",
        "details": [
          "Simulate 4 tire pressure values",
          "Generate realistic fluctuations (±0.1 bar)",
          "Publish to Redis channel every 10 seconds",
          "Include low pressure alerts (<1.9 bar)"
        ],
        "effort_hours": 3,
        "language": "Python"
      },
      {
        "component": "C2-central-broker",
        "task": "Subscribe to tire pressure sensor channel",
        "details": [
          "Add subscription to 'sensors:tire_pressure'",
          "Forward data to cloud via C1"
        ],
        "effort_hours": 1,
        "language": "Node.js"
      },
      {
        "component": "C1-cloud-communication",
        "task": "No changes required",
        "details": [
          "Existing WebSocket connection handles all sensor data"
        ],
        "effort_hours": 0
      }
    ],
    
    "data_format": {
      "redis_channel": "sensors:tire_pressure",
      "message_format": {
        "type": "sensor_data",
        "sensor": "tire_pressure",
        "data": {
          "frontLeft": 2.3,
          "frontRight": 2.4,
          "rearLeft": 2.2,
          "rearRight": 2.2
        },
        "timestamp": "2025-11-19T10:02:00Z",
        "licensePlate": "ABC-123",
        "unit": "bar"
      }
    },
    
    "effort_estimate": {
      "total_hours": 4,
      "breakdown": {
        "C5_simulator": 3,
        "C2_subscription": 1,
        "C1_changes": 0
      }
    },
    
    "risks": [
      {
        "level": "low",
        "description": "Simulated data may not reflect real sensor behavior",
        "mitigation": "Add realistic value ranges and fluctuation patterns"
      }
    ],
    
    "test_requirements": [
      "Unit tests for sensor simulator",
      "Integration tests for C5 -> C2 -> C1 data flow",
      "End-to-end test from sensor to cloud"
    ],
    
    "hardware_notes": "For production with real vehicles, requires TPMS (Tire Pressure Monitoring System) integration via CAN bus"
  },
  
  "recommendation": "proceed",
  "notes": "Simulation is straightforward. Can be upgraded to real TPMS hardware when available."
}
```

---

## 4. Agent A Consolidates and Responds to User

After receiving responses from both Agent B and Agent C, Agent A consolidates all information.

### Final Response to User
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Agent: agent-a
X-Agents-Consulted: agent-b,agent-c
X-Total-Analysis-Time: 5.2s

{
  "request_id": "req-2025-11-19-001",
  "feature": "Add tire pressure monitoring to car dashboard",
  "analysis_timestamp": "2025-11-19T10:03:00Z",
  "status": "feasible",
  "recommendation": "proceed",
  
  "consolidated_assessment": {
    "overall_impact": "low-medium",
    "feasibility": "high",
    "breaking_changes": false,
    
    "total_effort": {
      "hours": 14,
      "days": 1.75,
      "breakdown": {
        "agent_a_frontend": 6,
        "agent_b_backend": 4,
        "agent_c_incar": 4
      }
    },
    
    "implementation_phases": [
      {
        "phase": 1,
        "name": "In-Car Sensor Implementation",
        "agent": "agent-c",
        "duration_hours": 4,
        "components": ["C5-data-sensors", "C2-central-broker"],
        "blocking": true,
        "reason": "Backend and frontend depend on sensor data"
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
  "code_examples_url": "https://agent-a.cloud-region-1.example.com/api/v1/code-examples/req-2025-11-19-001",
  
  "implementation_plan_url": "https://agent-a.cloud-region-1.example.com/api/v1/implementation-plan/req-2025-11-19-001",
  
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
Host: agent-a.cloud-region-1.example.com
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
Host: agent-a.cloud-region-1.example.com
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
  "result_url": "https://agent-a.cloud-region-1.example.com/api/v1/results/req-2025-11-19-001"
}
```

---

## Summary

This API protocol enables:

1. ✅ **Distributed Architecture**: Agents operate independently in different locations
2. ✅ **Asynchronous Processing**: Requests are processed with status polling
3. ✅ **Consolidated Results**: Agent A consolidates responses from all agents
4. ✅ **Error Resilience**: Graceful degradation when agents are unavailable
5. ✅ **Security**: JWT authentication and rate limiting
6. ✅ **Traceability**: Request IDs and correlation IDs for debugging

The protocol supports the distributed agent model where:
- **Agent A** is the single entry point
- **Agent B** and **Agent C** provide independent domain analysis
- All communication is via well-defined REST APIs
- Results are consolidated and presented to the user
