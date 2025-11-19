# Inter-Agent API Test Cases

## Overview

This document contains comprehensive test cases for the inter-agent API communication protocol. Tests cover request/response flows, error handling, authentication, rate limiting, and data validation.

---

## Test Suite 1: User to Agent A Feature Request

### TC-1.1: Valid Feature Request Submission
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Critical

**Test Steps**:
1. Send POST request with valid feature request payload
2. Verify response status is 202 Accepted
3. Verify response contains request_id
4. Verify response contains tracking_url
5. Verify estimated_completion timestamp is in future

**Request**:
```json
{
  "request_id": "req-test-001",
  "feature": "Add tire pressure monitoring",
  "priority": "medium",
  "user_id": "user-123",
  "timestamp": "2025-11-19T10:00:00Z"
}
```

**Expected Response**:
```json
{
  "request_id": "req-test-001",
  "status": "processing",
  "message": "Feature request accepted. Agent A is analyzing...",
  "estimated_completion": "2025-11-19T10:05:00Z",
  "tracking_url": "https://agent-a.example.com/api/v1/status/req-test-001"
}
```

**Assertions**:
- HTTP Status: 202
- response.request_id === "req-test-001"
- response.status === "processing"
- response.tracking_url is valid URL
- response.estimated_completion > current timestamp

---

### TC-1.2: Missing Required Fields
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Send POST request without required "feature" field
2. Verify response status is 400 Bad Request
3. Verify error message identifies missing field

**Request**:
```json
{
  "request_id": "req-test-002",
  "priority": "medium",
  "user_id": "user-123"
}
```

**Expected Response**:
```json
{
  "error": "validation_error",
  "message": "Missing required field: feature",
  "status": 400,
  "timestamp": "2025-11-19T10:00:00Z"
}
```

**Assertions**:
- HTTP Status: 400
- response.error === "validation_error"
- response.message contains "feature"

---

### TC-1.3: Invalid Priority Value
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Send POST request with invalid priority value
2. Verify response status is 400 Bad Request
3. Verify error message indicates valid priority values

**Request**:
```json
{
  "request_id": "req-test-003",
  "feature": "Add feature",
  "priority": "super-urgent",
  "user_id": "user-123"
}
```

**Expected Response**:
```json
{
  "error": "validation_error",
  "message": "Invalid priority. Must be one of: low, medium, high, critical",
  "status": 400
}
```

**Assertions**:
- HTTP Status: 400
- response.error === "validation_error"
- response.message contains "priority"

---

### TC-1.4: Unauthorized Request (Missing Token)
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Critical

**Test Steps**:
1. Send POST request without Authorization header
2. Verify response status is 401 Unauthorized

**Request Headers**:
```
Content-Type: application/json
(No Authorization header)
```

**Expected Response**:
```json
{
  "error": "unauthorized",
  "message": "Missing or invalid authentication token",
  "status": 401
}
```

**Assertions**:
- HTTP Status: 401
- response.error === "unauthorized"

---

### TC-1.5: Invalid Authentication Token
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Critical

**Test Steps**:
1. Send POST request with invalid/expired token
2. Verify response status is 401 Unauthorized

**Request Headers**:
```
Authorization: Bearer invalid-token-12345
Content-Type: application/json
```

**Expected Response**:
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token",
  "status": 401
}
```

**Assertions**:
- HTTP Status: 401
- response.error === "unauthorized"

---

## Test Suite 2: Agent A to Agent B Communication

### TC-2.1: Valid Backend Analysis Request
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: Critical

**Test Steps**:
1. Agent A sends backend analysis request to Agent B
2. Verify response status is 202 Accepted
3. Verify response contains analysis_id
4. Verify response contains callback_url or polling_url

**Request Headers**:
```
Authorization: Bearer <agent-a-token>
X-Request-ID: req-test-001
X-Source-Agent: agent-a
X-Correlation-ID: corr-test-001
Content-Type: application/json
```

**Request Body**:
```json
{
  "request_id": "req-test-001",
  "feature": "Add tire pressure monitoring",
  "frontend_analysis": {
    "ui_impact": "medium",
    "components_affected": ["A1-mobile-app", "A2-staff-web"],
    "estimated_effort_hours": 6
  },
  "api_requirements": {
    "endpoint": "GET /api/car/:licensePlate",
    "new_fields": ["tirePressure"],
    "update_frequency": "10s"
  },
  "callback_url": "https://agent-a.example.com/api/v1/callback/backend-analysis"
}
```

**Expected Response**:
```json
{
  "analysis_id": "analysis-b-001",
  "request_id": "req-test-001",
  "status": "processing",
  "message": "Backend analysis started",
  "estimated_completion": "2025-11-19T10:03:00Z",
  "polling_url": "https://agent-b.example.com/api/v1/analysis/analysis-b-001"
}
```

**Assertions**:
- HTTP Status: 202
- response.analysis_id exists
- response.request_id === "req-test-001"
- response.status === "processing"
- response.polling_url is valid URL

---

### TC-2.2: Missing Source Agent Header
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: High

**Test Steps**:
1. Send request without X-Source-Agent header
2. Verify response status is 400 Bad Request

**Request Headers**:
```
Authorization: Bearer <agent-a-token>
X-Request-ID: req-test-002
Content-Type: application/json
(Missing X-Source-Agent)
```

**Expected Response**:
```json
{
  "error": "validation_error",
  "message": "Missing required header: X-Source-Agent",
  "status": 400
}
```

**Assertions**:
- HTTP Status: 400
- response.error === "validation_error"

---

### TC-2.3: Unauthorized Inter-Agent Request
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: Critical

**Test Steps**:
1. Send request with user token instead of agent token
2. Verify response status is 403 Forbidden

**Request Headers**:
```
Authorization: Bearer <user-token>
X-Source-Agent: agent-a
Content-Type: application/json
```

**Expected Response**:
```json
{
  "error": "forbidden",
  "message": "Agent-to-agent authentication required",
  "status": 403
}
```

**Assertions**:
- HTTP Status: 403
- response.error === "forbidden"

---

### TC-2.4: Backend Analysis Complete Response
**Endpoint**: `POST /api/v1/callback/backend-analysis`  
**Target**: Agent A (callback)  
**Priority**: Critical

**Test Steps**:
1. Agent B completes analysis and sends callback to Agent A
2. Verify Agent A receives complete backend analysis
3. Verify all required fields are present

**Request from Agent B to Agent A**:
```json
{
  "analysis_id": "analysis-b-001",
  "request_id": "req-test-001",
  "status": "completed",
  "backend_analysis": {
    "status": "feasible",
    "components": {
      "B1": {
        "impact": "medium",
        "changes": ["Add tirePressure field to API"],
        "effort_hours": 2
      },
      "B2": {
        "impact": "medium",
        "changes": ["Accept tire pressure in WebSocket"],
        "effort_hours": 2
      },
      "B3": {
        "impact": "low",
        "changes": ["Add tirePressure field to MongoDB"],
        "effort_hours": 1
      }
    },
    "total_effort_hours": 5,
    "dependencies": ["Requires sensor data from Agent C"],
    "risks": ["None identified"]
  },
  "timestamp": "2025-11-19T10:03:00Z"
}
```

**Assertions**:
- HTTP Status: 200 (Agent A accepts callback)
- response.status === "completed"
- response.backend_analysis exists
- response.backend_analysis.total_effort_hours > 0

---

## Test Suite 3: Agent A to Agent C Communication

### TC-3.1: Valid In-Car Analysis Request
**Endpoint**: `POST /api/v1/analyze-incar`  
**Target**: Agent C  
**Priority**: Critical

**Test Steps**:
1. Agent A sends in-car analysis request to Agent C
2. Verify response status is 202 Accepted
3. Verify response contains analysis_id

**Request**:
```json
{
  "request_id": "req-test-001",
  "feature": "Add tire pressure monitoring",
  "frontend_analysis": {
    "ui_impact": "medium",
    "estimated_effort_hours": 6
  },
  "sensor_requirements": {
    "data_type": "tire_pressure",
    "format": {
      "frontLeft": "number",
      "frontRight": "number",
      "rearLeft": "number",
      "rearRight": "number"
    },
    "update_frequency": "10s",
    "accuracy": "0.1 bar"
  },
  "callback_url": "https://agent-a.example.com/api/v1/callback/incar-analysis"
}
```

**Expected Response**:
```json
{
  "analysis_id": "analysis-c-001",
  "request_id": "req-test-001",
  "status": "processing",
  "message": "In-car analysis started",
  "estimated_completion": "2025-11-19T10:03:00Z",
  "polling_url": "https://agent-c.example.com/api/v1/analysis/analysis-c-001"
}
```

**Assertions**:
- HTTP Status: 202
- response.analysis_id exists
- response.status === "processing"

---

### TC-3.2: Sensor Not Available Response
**Endpoint**: `POST /api/v1/callback/incar-analysis`  
**Target**: Agent A (callback)  
**Priority**: High

**Test Steps**:
1. Agent C determines sensor is not available
2. Agent C sends callback with status "not_feasible"
3. Verify Agent A receives limitation details

**Request from Agent C to Agent A**:
```json
{
  "analysis_id": "analysis-c-002",
  "request_id": "req-test-002",
  "status": "completed",
  "incar_analysis": {
    "status": "not_feasible",
    "reason": "Requested sensor type not available in current vehicle configuration",
    "limitations": [
      "Current sensor suite does not include tire pressure sensors",
      "Would require hardware upgrade"
    ],
    "alternatives": [
      "Use manual tire pressure input",
      "Integrate with TPMS if available"
    ]
  }
}
```

**Assertions**:
- response.status === "completed"
- response.incar_analysis.status === "not_feasible"
- response.incar_analysis.reason exists
- response.incar_analysis.alternatives is array

---

## Test Suite 4: Status Polling

### TC-4.1: Poll Processing Status
**Endpoint**: `GET /api/v1/status/:request_id`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Submit feature request and receive request_id
2. Poll status endpoint while processing
3. Verify status is "processing"

**Request**:
```http
GET /api/v1/status/req-test-001 HTTP/1.1
Host: agent-a.example.com
Authorization: Bearer <token>
```

**Expected Response**:
```json
{
  "request_id": "req-test-001",
  "status": "processing",
  "progress": {
    "agent_a": "completed",
    "agent_b": "processing",
    "agent_c": "pending"
  },
  "estimated_completion": "2025-11-19T10:05:00Z",
  "last_updated": "2025-11-19T10:02:00Z"
}
```

**Assertions**:
- HTTP Status: 200
- response.status === "processing"
- response.progress exists

---

### TC-4.2: Poll Completed Status
**Endpoint**: `GET /api/v1/status/:request_id`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Poll status after all agents complete
2. Verify status is "completed"
3. Verify consolidated_analysis exists

**Expected Response**:
```json
{
  "request_id": "req-test-001",
  "status": "completed",
  "progress": {
    "agent_a": "completed",
    "agent_b": "completed",
    "agent_c": "completed"
  },
  "result_url": "https://agent-a.example.com/api/v1/results/req-test-001",
  "completed_at": "2025-11-19T10:05:00Z"
}
```

**Assertions**:
- HTTP Status: 200
- response.status === "completed"
- response.result_url exists
- response.completed_at exists

---

### TC-4.3: Poll Non-Existent Request
**Endpoint**: `GET /api/v1/status/:request_id`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Poll status with invalid request_id
2. Verify response status is 404 Not Found

**Request**:
```http
GET /api/v1/status/invalid-request-id HTTP/1.1
```

**Expected Response**:
```json
{
  "error": "not_found",
  "message": "Request ID not found",
  "status": 404
}
```

**Assertions**:
- HTTP Status: 404
- response.error === "not_found"

---

## Test Suite 5: Results Retrieval

### TC-5.1: Get Complete Analysis Results
**Endpoint**: `GET /api/v1/results/:request_id`  
**Target**: Agent A  
**Priority**: Critical

**Test Steps**:
1. Request completed after all agents finish
2. Get complete consolidated results
3. Verify all agent responses are included

**Request**:
```http
GET /api/v1/results/req-test-001 HTTP/1.1
Host: agent-a.example.com
Authorization: Bearer <token>
```

**Expected Response Structure**:
```json
{
  "request_id": "req-test-001",
  "feature": "Add tire pressure monitoring",
  "status": "completed",
  "consolidated_analysis": {
    "overall_status": "feasible",
    "total_effort_hours": 15,
    "frontend": { /* Agent A analysis */ },
    "backend": { /* Agent B analysis */ },
    "incar": { /* Agent C analysis */ },
    "implementation_order": [ /* steps */ ],
    "risks": [ /* consolidated risks */ ],
    "recommendation": "proceed"
  },
  "completed_at": "2025-11-19T10:05:00Z"
}
```

**Assertions**:
- HTTP Status: 200
- response.consolidated_analysis exists
- response.consolidated_analysis.frontend exists
- response.consolidated_analysis.backend exists
- response.consolidated_analysis.incar exists
- response.consolidated_analysis.total_effort_hours > 0

---

### TC-5.2: Get Results Before Completion
**Endpoint**: `GET /api/v1/results/:request_id`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Request results while still processing
2. Verify response indicates not ready

**Expected Response**:
```json
{
  "error": "not_ready",
  "message": "Analysis not yet completed",
  "status": 409,
  "current_status": "processing",
  "status_url": "https://agent-a.example.com/api/v1/status/req-test-001"
}
```

**Assertions**:
- HTTP Status: 409
- response.error === "not_ready"
- response.status_url exists

---

## Test Suite 6: Error Handling

### TC-6.1: Agent B Timeout
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: High

**Test Steps**:
1. Simulate Agent B taking too long to respond
2. Verify Agent A handles timeout gracefully
3. Verify error is reported to user

**Expected Behavior**:
- Agent A waits for configured timeout (e.g., 30 seconds)
- Agent A returns partial results with error for Agent B
- Status endpoint shows Agent B as "timeout"

**Expected Status Response**:
```json
{
  "request_id": "req-test-003",
  "status": "partial_failure",
  "progress": {
    "agent_a": "completed",
    "agent_b": "timeout",
    "agent_c": "completed"
  },
  "errors": [
    {
      "agent": "agent_b",
      "error": "timeout",
      "message": "Backend analysis timed out after 30 seconds"
    }
  ]
}
```

**Assertions**:
- response.status === "partial_failure"
- response.errors array contains timeout error
- response.progress.agent_b === "timeout"

---

### TC-6.2: Agent C Returns Error
**Endpoint**: `POST /api/v1/callback/incar-analysis`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Agent C encounters internal error
2. Agent C sends error callback to Agent A
3. Verify Agent A handles error appropriately

**Request from Agent C (Error Callback)**:
```json
{
  "analysis_id": "analysis-c-003",
  "request_id": "req-test-004",
  "status": "error",
  "error": {
    "code": "internal_error",
    "message": "Failed to access sensor database",
    "details": "Connection to sensor registry timed out"
  },
  "timestamp": "2025-11-19T10:03:00Z"
}
```

**Expected Agent A Response to User**:
```json
{
  "request_id": "req-test-004",
  "status": "partial_failure",
  "consolidated_analysis": {
    "overall_status": "incomplete",
    "frontend": { /* completed */ },
    "backend": { /* completed */ },
    "incar": {
      "status": "error",
      "error": "Failed to access sensor database"
    }
  }
}
```

**Assertions**:
- response.status === "partial_failure"
- response.consolidated_analysis.incar.status === "error"

---

### TC-6.3: Network Error Between Agents
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: High

**Test Steps**:
1. Simulate network failure between Agent A and Agent B
2. Verify Agent A retries with exponential backoff
3. Verify eventual failure is reported

**Expected Behavior**:
- Agent A attempts retry 3 times with backoff
- After retries exhausted, marks Agent B as "network_error"
- User receives partial results

**Assertions**:
- Agent A makes 3 retry attempts
- Final status shows network error
- User notified of partial results

---

## Test Suite 7: Rate Limiting

### TC-7.1: Exceed Rate Limit
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Send requests exceeding rate limit (e.g., 100 per minute)
2. Verify 429 Too Many Requests response
3. Verify Retry-After header is present

**Expected Response**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Maximum 100 requests per minute.",
  "status": 429,
  "retry_after": 60,
  "limit": 100,
  "remaining": 0,
  "reset": 1700392860
}
```

**Response Headers**:
```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1700392860
```

**Assertions**:
- HTTP Status: 429
- response.error === "rate_limit_exceeded"
- response.retry_after > 0
- Retry-After header present

---

### TC-7.2: Rate Limit Headers Present
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Low

**Test Steps**:
1. Send valid request
2. Verify rate limit headers are present in response

**Expected Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1700392860
```

**Assertions**:
- X-RateLimit-Limit header exists
- X-RateLimit-Remaining header exists
- X-RateLimit-Reset header exists

---

## Test Suite 8: Webhook Notifications

### TC-8.1: Register Webhook
**Endpoint**: `POST /api/v1/webhooks`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Register webhook URL for notifications
2. Verify webhook is registered successfully
3. Verify webhook_id is returned

**Request**:
```json
{
  "url": "https://client.example.com/webhooks/agent-notifications",
  "events": ["analysis_completed", "analysis_failed"],
  "secret": "webhook-secret-key-123"
}
```

**Expected Response**:
```json
{
  "webhook_id": "webhook-001",
  "url": "https://client.example.com/webhooks/agent-notifications",
  "events": ["analysis_completed", "analysis_failed"],
  "status": "active",
  "created_at": "2025-11-19T10:00:00Z"
}
```

**Assertions**:
- HTTP Status: 201
- response.webhook_id exists
- response.status === "active"

---

### TC-8.2: Webhook Notification Delivery
**Endpoint**: Client webhook URL  
**Target**: Client  
**Priority**: High

**Test Steps**:
1. Complete feature analysis
2. Verify webhook notification is sent to registered URL
3. Verify notification contains complete data

**Expected Webhook Payload**:
```json
{
  "event": "analysis_completed",
  "request_id": "req-test-001",
  "timestamp": "2025-11-19T10:05:00Z",
  "data": {
    "status": "completed",
    "result_url": "https://agent-a.example.com/api/v1/results/req-test-001"
  },
  "signature": "sha256=abc123..."
}
```

**Headers**:
```
Content-Type: application/json
X-Webhook-ID: webhook-001
X-Webhook-Signature: sha256=abc123...
```

**Assertions**:
- Client receives POST request
- event === "analysis_completed"
- signature is valid (HMAC-SHA256)

---

### TC-8.3: Webhook Delivery Failure Retry
**Endpoint**: Client webhook URL  
**Target**: Client  
**Priority**: Medium

**Test Steps**:
1. Configure webhook that returns 500 error
2. Verify Agent A retries webhook delivery
3. Verify exponential backoff is used

**Expected Behavior**:
- Agent A retries 3 times
- Backoff: 1s, 2s, 4s
- After retries, webhook marked as "failed"
- User can retrieve failed webhook logs

**Assertions**:
- 3 retry attempts made
- Backoff timing is correct
- Webhook status updated to "failed"

---

## Test Suite 9: Data Validation

### TC-9.1: Validate Effort Hours Range
**Endpoint**: `POST /api/v1/analyze-backend`  
**Target**: Agent B  
**Priority**: Low

**Test Steps**:
1. Agent B returns negative effort hours
2. Verify Agent A validates and rejects invalid data

**Invalid Response from Agent B**:
```json
{
  "analysis_id": "analysis-b-004",
  "backend_analysis": {
    "total_effort_hours": -5
  }
}
```

**Expected Behavior**:
- Agent A detects invalid data
- Agent A logs validation error
- Agent A requests correction from Agent B or marks as error

---

### TC-9.2: Validate Required Fields in Analysis
**Endpoint**: `POST /api/v1/callback/backend-analysis`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Agent B sends incomplete analysis (missing required fields)
2. Verify Agent A rejects incomplete response

**Invalid Response from Agent B**:
```json
{
  "analysis_id": "analysis-b-005",
  "request_id": "req-test-005",
  "status": "completed"
  // Missing backend_analysis object
}
```

**Expected Behavior**:
- Agent A returns 400 Bad Request
- Error message indicates missing backend_analysis

**Assertions**:
- HTTP Status: 400
- Error indicates missing required field

---

## Test Suite 10: Concurrent Requests

### TC-10.1: Multiple Simultaneous Requests
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Send 10 feature requests simultaneously
2. Verify all requests receive unique request_ids
3. Verify all requests are processed independently

**Expected Behavior**:
- All 10 requests return 202 Accepted
- Each has unique request_id
- Processing happens in parallel
- Status can be polled for each independently

**Assertions**:
- All requests succeed
- No request_id collisions
- All requests complete successfully

---

### TC-10.2: Same Feature Requested Twice
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Submit feature request "Add tire pressure monitoring"
2. Submit identical request again
3. Verify both are processed independently (no deduplication)

**Expected Behavior**:
- Both requests accepted
- Both receive unique request_ids
- Both processed independently

**Assertions**:
- Two separate analyses performed
- Results may be cached but requests are independent

---

## Test Suite 11: Security Tests

### TC-11.1: SQL Injection in Feature Description
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Critical

**Test Steps**:
1. Submit feature with SQL injection attempt
2. Verify input is sanitized
3. Verify no database errors occur

**Request**:
```json
{
  "request_id": "req-test-006",
  "feature": "Add feature'; DROP TABLE users; --",
  "priority": "medium",
  "user_id": "user-123"
}
```

**Expected Behavior**:
- Request accepted and sanitized
- No SQL executed
- Feature description stored as plain text

**Assertions**:
- No database errors
- Feature description stored safely

---

### TC-11.2: XSS in Feature Description
**Endpoint**: `GET /api/v1/results/:request_id`  
**Target**: Agent A  
**Priority**: High

**Test Steps**:
1. Submit feature with XSS payload
2. Retrieve results
3. Verify output is escaped

**Request**:
```json
{
  "feature": "<script>alert('XSS')</script>"
}
```

**Expected Results Response**:
- HTML entities escaped
- Script not executable
- Output: `&lt;script&gt;alert('XSS')&lt;/script&gt;`

**Assertions**:
- Scripts are escaped in output
- No executable code in response

---

### TC-11.3: Oversized Request Payload
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Send request with extremely large payload (> 1MB)
2. Verify request is rejected

**Expected Response**:
```json
{
  "error": "payload_too_large",
  "message": "Request payload exceeds maximum size of 1MB",
  "status": 413
}
```

**Assertions**:
- HTTP Status: 413
- response.error === "payload_too_large"

---

## Test Suite 12: Performance Tests

### TC-12.1: Response Time Under Load
**Endpoint**: `POST /api/v1/feature-request`  
**Target**: Agent A  
**Priority**: Medium

**Test Steps**:
1. Send 100 requests per second for 1 minute
2. Measure response times
3. Verify 95th percentile < 500ms

**Expected Behavior**:
- 95% of requests respond in < 500ms
- No requests fail
- Rate limiting applies after threshold

**Assertions**:
- p95 < 500ms
- p99 < 1000ms
- 0% error rate (excluding rate limited)

---

### TC-12.2: Large Analysis Result Size
**Endpoint**: `GET /api/v1/results/:request_id`  
**Target**: Agent A  
**Priority**: Low

**Test Steps**:
1. Request analysis with large consolidated result
2. Verify response is paginated or compressed

**Expected Behavior**:
- Large responses use gzip compression
- Response time remains reasonable
- Client can handle large payload

---

## Test Automation Scripts

### Example Using curl

```bash
#!/bin/bash
# TC-1.1: Valid Feature Request Submission

TOKEN="your-auth-token"
BASE_URL="https://agent-a.example.com/api/v1"

# Submit feature request
response=$(curl -s -w "\n%{http_code}" -X POST \
  "${BASE_URL}/feature-request" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req-test-001",
    "feature": "Add tire pressure monitoring",
    "priority": "medium",
    "user_id": "user-123",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }')

# Extract HTTP status code
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

# Assertions
if [ "$http_code" -eq 202 ]; then
  echo "[PASS] TC-1.1: Received 202 Accepted"
else
  echo "[FAIL] TC-1.1: Expected 202, got $http_code"
  exit 1
fi

request_id=$(echo "$body" | jq -r '.request_id')
if [ "$request_id" == "req-test-001" ]; then
  echo "[PASS] TC-1.1: Request ID matches"
else
  echo "[FAIL] TC-1.1: Request ID mismatch"
  exit 1
fi

echo "[SUCCESS] TC-1.1: All assertions passed"
```

### Example Using JavaScript/Node.js

```javascript
// TC-1.1: Valid Feature Request Submission
const axios = require('axios');

async function testValidFeatureRequest() {
  const baseURL = 'https://agent-a.example.com/api/v1';
  const token = 'your-auth-token';
  
  try {
    const response = await axios.post(
      `${baseURL}/feature-request`,
      {
        request_id: 'req-test-001',
        feature: 'Add tire pressure monitoring',
        priority: 'medium',
        user_id: 'user-123',
        timestamp: new Date().toISOString()
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    // Assertions
    console.assert(response.status === 202, 'Expected 202 Accepted');
    console.assert(response.data.request_id === 'req-test-001', 'Request ID matches');
    console.assert(response.data.status === 'processing', 'Status is processing');
    console.assert(response.data.tracking_url, 'Tracking URL exists');
    
    console.log('[PASS] TC-1.1: Valid Feature Request Submission');
    return true;
  } catch (error) {
    console.error('[FAIL] TC-1.1:', error.message);
    return false;
  }
}

testValidFeatureRequest();
```

### Example Using Python/pytest

```python
# test_inter_agent_api.py
import pytest
import requests
from datetime import datetime

BASE_URL = "https://agent-a.example.com/api/v1"
TOKEN = "your-auth-token"

@pytest.fixture
def auth_headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def test_valid_feature_request(auth_headers):
    """TC-1.1: Valid Feature Request Submission"""
    payload = {
        "request_id": "req-test-001",
        "feature": "Add tire pressure monitoring",
        "priority": "medium",
        "user_id": "user-123",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    response = requests.post(
        f"{BASE_URL}/feature-request",
        json=payload,
        headers=auth_headers
    )
    
    # Assertions
    assert response.status_code == 202, "Expected 202 Accepted"
    assert response.json()["request_id"] == "req-test-001"
    assert response.json()["status"] == "processing"
    assert "tracking_url" in response.json()
    
def test_missing_required_fields(auth_headers):
    """TC-1.2: Missing Required Fields"""
    payload = {
        "request_id": "req-test-002",
        "priority": "medium",
        "user_id": "user-123"
        # Missing "feature" field
    }
    
    response = requests.post(
        f"{BASE_URL}/feature-request",
        json=payload,
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"
    assert "feature" in response.json()["message"]

def test_unauthorized_request():
    """TC-1.4: Unauthorized Request"""
    payload = {
        "request_id": "req-test-003",
        "feature": "Add feature",
        "priority": "medium"
    }
    
    # No Authorization header
    response = requests.post(
        f"{BASE_URL}/feature-request",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"
```

---

## Test Coverage Summary

| Test Suite | Test Cases | Priority Critical | Priority High | Priority Medium | Priority Low |
|------------|------------|-------------------|---------------|-----------------|--------------|
| 1. User to Agent A | 5 | 3 | 1 | 1 | 0 |
| 2. Agent A to Agent B | 4 | 3 | 1 | 0 | 0 |
| 3. Agent A to Agent C | 2 | 1 | 1 | 0 | 0 |
| 4. Status Polling | 3 | 0 | 2 | 1 | 0 |
| 5. Results Retrieval | 2 | 1 | 1 | 0 | 0 |
| 6. Error Handling | 3 | 0 | 3 | 0 | 0 |
| 7. Rate Limiting | 2 | 0 | 0 | 1 | 1 |
| 8. Webhooks | 3 | 0 | 1 | 2 | 0 |
| 9. Data Validation | 2 | 0 | 0 | 1 | 1 |
| 10. Concurrent Requests | 2 | 0 | 1 | 1 | 0 |
| 11. Security | 3 | 1 | 1 | 1 | 0 |
| 12. Performance | 2 | 0 | 0 | 2 | 0 |
| **TOTAL** | **33** | **9** | **12** | **10** | **2** |

---

## Test Execution Order

### Phase 1: Basic Functionality (Critical Tests)
1. TC-1.1 - Valid feature request
2. TC-1.4 - Authentication
3. TC-2.1 - Agent A to B communication
4. TC-5.1 - Results retrieval

### Phase 2: Error Handling
5. TC-1.2 - Missing fields
6. TC-6.1 - Timeouts
7. TC-6.2 - Agent errors
8. TC-4.3 - Non-existent requests

### Phase 3: Advanced Features
9. TC-7.1 - Rate limiting
10. TC-8.1 - Webhooks
11. TC-10.1 - Concurrent requests
12. TC-11.1 - Security tests

### Phase 4: Performance & Load
13. TC-12.1 - Response time under load
14. TC-12.2 - Large payloads

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Inter-Agent API Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install pytest requests
    
    - name: Run API tests
      env:
        API_TOKEN: ${{ secrets.API_TEST_TOKEN }}
        BASE_URL: ${{ secrets.API_BASE_URL }}
      run: |
        pytest tests/test_inter_agent_api.py -v
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-results.xml
```

---

## Test Environment Setup

### Prerequisites
- Agent A, B, C services running
- Valid authentication tokens for users and agents
- Network connectivity between agents
- Test database with sample data

### Configuration
```json
{
  "agents": {
    "agent_a": {
      "base_url": "https://agent-a.example.com/api/v1",
      "auth_token": "agent-a-token"
    },
    "agent_b": {
      "base_url": "https://agent-b.example.com/api/v1",
      "auth_token": "agent-b-token"
    },
    "agent_c": {
      "base_url": "https://agent-c.example.com/api/v1",
      "auth_token": "agent-c-token"
    }
  },
  "test_user": {
    "user_id": "test-user-123",
    "auth_token": "user-test-token"
  },
  "timeouts": {
    "request": 30,
    "polling_interval": 1
  }
}
```
