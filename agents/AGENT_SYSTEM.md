# AI Agent System - Distributed Architecture

## Overview

This document describes the AI agent system for the car demo project. Three specialized agents operate as independent entities. Each agent analyzes feature requests from their domain perspective and communicates with other agents when cross-domain orchestration is needed.

## Distributed Agent Architecture

```
                    User/Client
                         |
                         | Feature Request
                         v
            +-------------------------+
            |       Agent A           |
            |   Frontend Analysis     |
            |   (Entry Point)         |
            +-------------------------+
                   |            |
                   |            |
    Backend needed?|            | In-car data needed?
                   |            |
                   v            v
         +--------------+   +--------------+
         |   Agent B    |   |   Agent C    |
         |   Backend    |   |   In-Car     |
         |   Analysis   |   |   Analysis   |
         +--------------+   +--------------+
                   |            |
                   |            |
                   +-----+------+
                         |
                         v
            +-------------------------+
            |       Agent A           |
            |   Consolidates Results  |
            |   Provides Assessment   |
            +-------------------------+
```

**Independent Agent Architecture**:
1. **Agent A (Frontend)** - Entry point for all requests
2. **Agent B (Backend)** - Independent backend analysis
3. **Agent C (In-Car)** - Independent in-car systems analysis

**Communication Flow**:
1. User sends feature request to **Agent A** (Frontend)
2. Agent A analyzes frontend impact independently
3. Agent A sends requests to Agent B and/or Agent C if needed
4. Agents B and C perform independent analysis and respond to Agent A
5. Agent A consolidates all responses and provides final assessment

## Agent Roles

### Agent A - Frontend Analysis Agent (Entry Point)
**File**: `agents/agent-a-frontend.md`

**Primary Responsibilities**:
- **Entry point for all feature requests**
- Analyze UI/UX implications independently
- Assess API integration requirements
- Identify state management needs
- **Request analysis from Agents B and C when cross-domain impact exists**
- **Consolidate responses from distributed agents into final assessment**
- Recommend frontend test cases
- Provide go/no-go recommendation

**Components**:
- A1 Car User App (React Native)
- A2 Rental Staff App (React Web)

**Key Expertise**:
- React/React Native development
- REST API consumption
- Mobile and web UI patterns
- Frontend testing strategies
- **Distributed system communication**

### Agent B - Backend Analysis Agent
**File**: `agents/agent-b-backend.md`

**Responsibilities**:
- Analyze API design implications independently
- Assess database schema changes
- Identify data flow requirements
- Evaluate backend service impact
- Respond to Agent A with backend analysis
- Recommend backend test cases

**Components**:
- B1 Web Server (REST API)
- B2 IoT Gateway (WebSocket + REST)
- B3 MongoDB (Realtime Database)
- B4 PostgreSQL (Static Database)

**Key Expertise**:
- Node.js/Express development
- Database design (SQL + NoSQL)
- API design and documentation
- Backend testing strategies
- Microservices architecture

### Agent C - In-Car Systems Analysis Agent
**File**: `agents/agent-c-in-car.md`

**Responsibilities**:
- Analyze sensor requirements independently
- Assess communication protocols
- Identify simulation complexity
- Evaluate vehicle system impact
- Respond to Agent A with in-car analysis
- Recommend in-car system test cases

**Components**:
- C1 Cloud Communication (Python)
- C2 Central Broker (Node.js + Redis)
- C5 Data Sensors (Python)

**Key Expertise**:
- Sensor data handling
- Redis pub/sub patterns
- WebSocket communication
- System constraints
- IoT system testing

## Distributed Feature Analysis Workflow

### Step 1: Feature Request to Agent A (Entry Point)
All feature requests start with Agent A (Frontend) as the single entry point:

```markdown
Feature: Add tire pressure monitoring

Agent A receives request and analyzes:
1. Does this affect the UI? -> YES (need gauge display)
2. Do I need new API data? -> YES (need tire pressure from backend)
3. Will backend need new sensors? -> PROBABLY (need to ask Agent C)

Agent A's independent assessment:
- UI Impact: Medium (new gauge component in 2 apps)
- API Needs: New field in existing endpoint
- Estimated frontend effort: 6 hours

Next: Send analysis request to Agent B (Backend)
```

### Step 2: Agent A Requests Analysis from Agent B
Agent A sends request to Agent B:

```markdown
FROM: Agent A (Frontend)
TO: Agent B (Backend)
PROTOCOL: REST API / Message Queue

REQUEST:
Feature: "tire pressure monitoring"
API Requirement:
- Modify GET /api/car/:licensePlate
- Add field: tirePressure { frontLeft, frontRight, rearLeft, rearRight }
- Data type: Numbers (bar, 1.5-4.0 range)
- Update frequency: Every 10 seconds

QUESTIONS:
- Can backend provide this data?
- Where does the data come from?
- What is the backend effort?
```

Agent B (independent analysis) responds:

```markdown
FROM: Agent B (Backend)
TO: Agent A (Frontend)
PROTOCOL: REST API / Message Queue

RESPONSE:
STATUS: [OK] YES - Backend can provide this data

Implementation:
- B1: Add tirePressure field to API response (2 hours)
- B2: Accept and store tire pressure from sensors (2 hours)
- B3: Add field to MongoDB car_data collection (no migration needed)

Data Source: Requires sensor data from Agent C (in-car systems)

Backend Effort: 4 hours
Dependencies: Agent C must provide tire pressure sensor data via Redis

Note: I need to verify with Agent C about sensor availability
```

### Step 3: Agent A Requests Analysis from Agent C
Agent A sends request to Agent C:

```markdown
FROM: Agent A (Frontend)
TO: Agent C (In-Car Systems)
PROTOCOL: REST API / Message Queue

REQUEST:
Feature: "tire pressure monitoring"
Sensor Requirement:
- Type: tire_pressure
- Data: 4 values (frontLeft, frontRight, rearLeft, rearRight)
- Range: 1.5-4.0 bar
- Update Frequency: Every 10 seconds
- Format: JSON via Redis

QUESTIONS:
- Can in-car systems provide this sensor data?
- What is the implementation effort?
- Any vehicle compatibility issues?
```

Agent C (independent analysis) responds:

```markdown
FROM: Agent C (In-Car Systems)
TO: Agent A (Frontend)
PROTOCOL: REST API / Message Queue

RESPONSE:
STATUS: [OK] YES - Can provide tire pressure sensor data

Implementation:
- C5: Create tire pressure sensor simulator (3 hours)
- C2: Subscribe to sensors:tire_pressure channel (1 hour)
- C1: Forward via WebSocket (no changes needed)

Data Format:
{
  "frontLeft": 2.3,
  "frontRight": 2.3,
  "rearLeft": 2.2,
  "rearRight": 2.2,
  "timestamp": "2025-11-12T10:30:00Z",
  "licensePlate": "ABC-123"
}

In-Car Effort: 4 hours
Ready to implement: Yes

Data will be available via: sensors:tire_pressure Redis channel
```

### Step 4: Agent A Consolidates Distributed Responses
Agent A receives responses from Agent B and Agent C, then consolidates:

```markdown
## Feature: Add Tire Pressure Monitoring

### Final Consolidated Assessment by Agent A

RECEIVED FROM:
- Agent B: [OK] Backend feasible, 4 hours
- Agent C: [OK] Sensor data available, 4 hours

#### Overall Impact: LOW-MEDIUM [OK]

**Total Estimated Effort**: 14 hours (across 3 distributed agents)
- Agent A - Frontend (A1 + A2): 6 hours
- Agent B - Backend (B1 + B2): 4 hours
- Agent C - In-Car (C5 + C2): 4 hours

**Breaking Changes**: None (additive change only)

**Implementation Order** (Distributed Execution):
1. **Week 1, Day 1-2**: Agent C implements sensor (4 hours)
2. **Week 1, Day 2-3**: Agent B implements backend (4 hours)
3. **Week 1, Day 3-4**: Agent A implements frontend (6 hours)
4. **Week 1, Day 5**: Cross-agent integration testing (2 hours)

#### Component Breakdown by Agent

**Agent A - Frontend**:
- A1 Mobile: Add tire pressure gauge component
- A2 Web: Add tire pressure indicators to dashboard
- Both: Show warnings for low pressure (<1.9 bar)
- API Integration: Consume new tirePressure field
- Effort: 6 hours
- Risk: Low

**Agent B - Backend**:
- B1: Add tirePressure field to GET /api/car/:licensePlate
- B2: Accept tire pressure in WebSocket messages
- B3: Add tirePressure to MongoDB car_data collection
- Swagger: Update API documentation
- Effort: 4 hours
- Risk: Low

**Agent C - In-Car**:
- C5: Create tire pressure sensor simulator
- C2: Subscribe to sensors:tire_pressure channel
- Redis: Publish to sensors:tire_pressure every 10 seconds
- Effort: 4 hours
- Risk: Low

#### Data Flow
```
C5 Sensor -> Redis (sensors:tire_pressure) -> C2 Broker -> 
C1 Communication -> WebSocket -> B2 Gateway -> MongoDB -> 
B1 API -> Frontend Apps
```

#### Test Cases Summary
- Unit Tests: 24 total (8 per component)
- Integration Tests: 12 total
- E2E Tests: 6 total
- Test Development: 4 hours

#### Dependencies & Sequencing
1. C5 must publish data before B2 can receive it
2. B2 must store data before B1 can query it
3. B1 API must be ready before frontend can display
4. All components can develop in parallel, integrate sequentially

#### Risks & Mitigations
- **Risk**: Sensor simulation realism
  - **Mitigation**: Use realistic pressure ranges (1.9-2.4 bar), simulate slow leaks
- **Risk**: Data synchronization lag
  - **Mitigation**: 10-second update frequency is acceptable for tire pressure
- **Risk**: API backwards compatibility
  - **Mitigation**: tirePressure is optional field, old clients ignore it

#### Go/No-Go Decision: [OK] PROCEED

**Reasoning**: 
- Low complexity across all components
- No breaking changes
- Reasonable effort (14 hours = ~2 days)
- High user value (safety feature)
- Low risk implementation

**Recommendation**: Proceed with implementation in Sprint 12
```

## Example: Complete Feature Analysis

### Feature Request: "Add Tire Pressure Monitoring"

#### Agent A - Frontend Analysis

```markdown
### Frontend Impact: MEDIUM

**A1 Car User App**:
- Add tire pressure gauge display showing all 4 tires
- Visual indicators for each tire (green/yellow/red based on pressure)
- Warning alert when any tire is below 1.9 bar
- Real-time updates as pressure changes

**A2 Rental Staff App**:
- Add tire pressure column to fleet dashboard
- Add tire pressure filter (show only cars with low pressure)
- Add detailed tire pressure view in car details page
- Historical tire pressure chart

**API Requirements**:
- Modify GET /api/car/:licensePlate to include tirePressure field
- Add GET /api/cars?lowPressure=true filter

**Estimated Effort**: 8 hours
- A1 changes: 4 hours (gauge component, alerts)
- A2 changes: 4 hours (dashboard, charts)

**Test Cases**: 10 unit tests, 6 integration tests, 4 E2E tests
```

#### Agent B - Backend Analysis

```markdown
### Backend Impact: MEDIUM

**B1 Web Server**:
- Modify GET /api/car/:licensePlate response schema
- Add tirePressure field: { frontLeft, frontRight, rearLeft, rearRight }
- Data type: Numbers in bar (1.5-4.0 range)
- Update Swagger documentation

**B2 IoT Gateway**:
- Accept tirePressure in WebSocket messages
- Validate pressure values (1.5-4.0 bar)
- Store in MongoDB car_data collection
- Forward to B1 via database query

**B3 MongoDB**:
- Add tirePressure field to car_data collection
- No migration needed (schema-less)
- Add index: { tirePressure.frontLeft: 1, timestamp: -1 }

**B4 PostgreSQL**:
- Optional: Add tire_specification to cars table
- Not required for MVP

**Estimated Effort**: 6 hours
- B1 changes: 2 hours
- B2 changes: 3 hours
- B3 setup: 1 hour
- Testing: included above

**Test Cases**: 12 unit tests, 8 integration tests, 4 E2E tests
```

#### Agent C - In-Car Analysis

```markdown
### In-Car Impact: MEDIUM

**C5 Data Sensors**:
- Add tire pressure sensor simulation
- Generate realistic pressure values (1.9-2.4 bar)
- Simulate gradual pressure loss over time
- Random variation (±0.1 bar)
- Publish to Redis: sensors:tire_pressure

**C2 Central Broker**:
- Subscribe to sensors:tire_pressure
- Store in car:{licensePlate}:sensors hash
- Include in latest_data aggregation
- Forward via C1

**C1 Cloud Communication**:
- Forward tirePressure in sensor_data messages
- No protocol changes needed

**Data Format**:
```json
{
  "frontLeft": 2.3,
  "frontRight": 2.3,
  "rearLeft": 2.2,
  "rearRight": 2.2,
  "timestamp": "2025-11-12T10:30:00Z",
  "licensePlate": "ABC-123"
}
```

**Estimated Effort**: 5 hours
- C5 sensor: 3 hours
- C2 changes: 1.5 hours
- Testing: 0.5 hours

**Test Cases**: 8 unit tests, 4 integration tests, 2 E2E tests
```

#### Consolidated Assessment

```markdown
## Feature: Add Tire Pressure Monitoring

### Overall Impact: MEDIUM [OK]

**Total Estimated Effort**: 19 hours
- Frontend: 8 hours
- Backend: 6 hours
- In-Car: 5 hours

**Breaking Changes**: None (additive change only)

**Implementation Order**:
1. C5: Add tire pressure sensor (3 hours)
2. C2: Subscribe and aggregate (1.5 hours)
3. B2: Accept and store tire pressure data (3 hours)
4. B1: Add to API response (2 hours)
5. A1/A2: Display in UI (8 hours)
6. Testing: Integration and E2E (1.5 hours)

**Total Test Cases**: 
- Unit: 30 tests
- Integration: 18 tests
- E2E: 10 tests
- Test development: ~5 hours

**Risks**: 
- Sensor simulation must be realistic (gradual pressure loss, not sudden)
- Low pressure alerts should not be too sensitive (avoid false alarms)
- Need proper validation (pressure can't be negative or > 4.0 bar)

**Go/No-Go**: [OK] PROCEED

This is a medium-complexity, high-value safety feature that can be implemented
incrementally without breaking existing functionality. Estimated delivery: 2-3 days.
```

## Agent Communication Protocols

### Agent A -> Agent B Communication

**When to Consult Agent B**:
- New API endpoints needed
- Modifications to existing API responses
- Database schema questions
- Performance/scalability concerns
- Data storage requirements

**Message Format from Agent A to Agent B**:

**Message Format from Agent A to Agent B**:

```markdown
FROM: Agent A (Frontend)
TO: Agent B (Backend)
RE: [Feature Name]

FRONTEND NEEDS:
[Specific API requirements from frontend perspective]

API REQUEST:
- Endpoint: [Method] [Path]
- Request Body: [Schema if POST/PUT]
- Response Needed: [Schema]
- Update Frequency: [Real-time/polling interval]
- Error Handling: [Expected error cases]

QUESTIONS FOR BACKEND:
1. Can you provide this data?
2. Where will the data come from?
3. What's the expected latency?
4. Any performance concerns?

FRONTEND CONTEXT:
- Use case: [How frontend will use this data]
- User impact: [Why users need this]
```

**Response Format from Agent B to Agent A**:

```markdown
FROM: Agent B (Backend)
TO: Agent A (Frontend)
RE: [Feature Name]

STATUS: [OK] YES / [WARN] PARTIAL / [NO] NO

IMPLEMENTATION PLAN:
- B1 Changes: [API modifications]
- B2 Changes: [Data ingestion]
- B3/B4 Changes: [Database schema]
- Effort: [X hours]

API SPECIFICATION:
[Detailed endpoint spec with request/response schemas]

DATA SOURCE:
[Where backend gets the data from - may need Agent C]

DEPENDENCIES:
[What backend needs from other components]

TIMELINE:
[When this can be ready]

CONCERNS:
[Any issues or limitations]
```

### Agent A -> Agent C Communication

**When to Consult Agent C**:
- New sensor data needed
- Questions about data collection frequency
- In-car system capabilities
- Command execution requirements
- Real-time data streaming needs

**Message Format from Agent A to Agent C**:

```markdown
FROM: Agent A (Frontend)
TO: Agent C (In-Car)
RE: [Feature Name]

FRONTEND NEEDS:
[What data/functionality frontend requires]

SENSOR REQUIREMENT:
- Data Type: [What needs to be measured]
- Format: [Expected data structure]
- Frequency: [How often updates are needed]
- Accuracy: [Required precision]

COMMAND REQUIREMENT (if applicable):
- Command: [What action car should perform]
- Parameters: [Command parameters]
- Response: [Expected feedback]

QUESTIONS FOR IN-CAR:
1. Can sensors provide this data?
2. What's the update frequency limit?
3. Is simulation feasible or need real hardware?
4. Any safety/security concerns?

FRONTEND CONTEXT:
- Use case: [How frontend will display/use this]
- User impact: [Why users need this]
```

**Response Format from Agent C to Agent A**:

```markdown
FROM: Agent C (In-Car)
TO: Agent A (Frontend)
RE: [Feature Name]

STATUS: [OK] YES / [WARN] PARTIAL / [NO] NO

IMPLEMENTATION PLAN:
- C5 Sensor: [New sensor or modification]
- C2 Broker: [Message routing changes]
- C1 Communication: [Data sync changes]
- Effort: [X hours]

DATA SPECIFICATION:
[Exact data format, channels, update frequency]

SIMULATION APPROACH:
[How sensor will be simulated]

DEPENDENCIES:
[What in-car system needs from backend]

TIMELINE:
[When this can be ready]

CONCERNS:
[Any issues or limitations]
```

### Agent B ↔ Agent C Communication

When Agent B needs clarification from Agent C (routed through Agent A):

**Agent B to Agent A to Agent C**:
```markdown
FROM: Agent B (Backend) via Agent A
TO: Agent C (In-Car)
RE: [Feature Name]

BACKEND NEEDS CLARIFICATION:
[Specific question about sensor data format/availability]

TECHNICAL DETAILS:
[Backend-specific requirements for data processing]
```
```
FROM: Agent A (Frontend)
TO: Agent B (Backend)
RE: Tire Pressure Monitoring

REQUEST:
Need API endpoint to retrieve tire pressure data for a car

DETAILS:
- Should include pressure for all 4 tires (in bar)
- Should include low pressure alerts
- Should be part of existing car data endpoint

PROPOSED API:
GET /api/car/:licensePlate
Response: {
  ...existing fields...,
  "tirePressure": {
    "frontLeft": 2.3,
    "frontRight": 2.3,
    "rearLeft": 2.2,
    "rearRight": 2.2
  },
  "lowPressureAlert": false
}

TIMELINE:
Need this before frontend development (Week 2)
```

**Agent B to Agent C**:
```
FROM: Agent B (Backend)
TO: Agent C (In-Car)
RE: Tire Pressure Monitoring

REQUEST:
Need tire pressure sensor data from in-car system

DETAILS:
- Data type: Object with 4 tire pressures (in bar)
- Update frequency: Every 30 seconds
- Must include low pressure detection

REQUIRED FORMAT:
Redis Channel: sensors:tire_pressure
Payload: {
  "frontLeft": 2.3,
  "frontRight": 2.3,
  "rearLeft": 2.2,
  "rearRight": 2.2,
  "timestamp": "ISO8601",
  "licensePlate": "ABC-123"
}

TIMELINE:
Need sensor operational by Week 1 for testing
```

**Agent C to Agent B**:
```
FROM: Agent C (In-Car)
TO: Agent C (Backend)
RE: Tire Pressure Monitoring

RESPONSE:
[OK] Can provide tire pressure data

IMPLEMENTATION:
- Sensor: C5 tire_pressure_sensor.py
- Channel: sensors:tire_pressure
- Format: As specified
- Update: Every 30 seconds
- Additional: Will simulate gradual pressure loss over time

READY BY: End of Week 1

NOTES:
- Simulation will start at 100% and drain gradually
- When GPS velocity = 0 for 5+ minutes, will simulate charging
- Will include realistic charging curves (fast then slow)
```

## Decision Tree

```
Feature Request Arrives
    |
+---------------------+
|   Agent A Receives  |
|   (Entry Point)     |
+----------+----------+
           |
    Does it affect UI?
           |
       +---+---+
      Yes      No -> [Unusual - verify it's really a frontend request]
       |
+------------------+
| Agent A analyzes |
| frontend impact  |
+------+-----------+
       |
   Need new API data?
       |
    +--+--+
   Yes    No
    |      |
+---------------+    +-----------------+
| Consult       |    | Frontend-only   |
| Agent B       |    | implementation  |
| about API     |    +-----------------+
+-------+-------+
        |
    Agent B responds
        |
    Need new sensor data?
        |
     +--+--+
    Yes    No
     |      |
+---------------+    +-----------------+
| Consult       |    | Backend provides|
| Agent C       |    | from existing   |
| about sensors |    | data sources    |
+-------+-------+    +-----------------+
        |
    Agent C responds
        |
+---------------------+
| Agent A consolidates|
| all responses       |
+----------+----------+
           |
    +--------------+
    | Final Report |
    | with effort, |
    | risks, steps |
    +--------------+
```

**Agent A Decision Points**:

1. **Frontend-Only Feature** (No consult needed)
   - UI-only changes (styling, layout, navigation)
   - Client-side logic (validation, formatting)
   - Using existing API data in new ways
   - Example: "Add dark mode to mobile app"

2. **Consult Agent B** (Backend involvement)
   - New API endpoints needed
   - Modify API response format
   - New database queries
   - Performance optimization
   - Example: "Add user preferences storage"

3. **Consult Agent C** (Sensor/in-car involvement)
   - New sensor data required
   - New car commands needed
   - In-car system changes
   - Example: "Add tire pressure monitoring"

4. **Consult Both B and C** (Full stack feature)
   - New sensors + new APIs + new UI
   - Complete data flow from car to user
   - Example: "Add tire pressure monitoring"

## Risk Levels and Responses

### Low Risk ([OK] PROCEED)
- Additive changes only
- No breaking changes
- Well-understood technology
- < 3 days effort
- Independent components

**Action**: Proceed with standard development

### Medium Risk ([WARN] PROCEED WITH CAUTION)
- Some breaking changes (manageable)
- Cross-component dependencies
- Moderate complexity
- 3-7 days effort
- Performance considerations

**Action**: 
- Create detailed implementation plan
- Add extra testing
- Consider phased rollout
- Schedule review checkpoints

### High Risk ([STOP] DO NOT PROCEED / MAJOR PLANNING REQUIRED)
- Major breaking changes
- Complex cross-component orchestration
- New technology/paradigms
- > 7 days effort
- Safety/security critical
- Performance concerns

**Action**:
- Architecture review required
- Proof of concept first
- Detailed design document
- Risk mitigation plan
- Consider alternatives

## Usage Instructions

### For Development Teams

1. **Submit Feature Request to Agent A**:
   ```markdown
   Feature: [Name]
   Description: [What users will see/do]
   User Story: As a [user], I want [feature] so that [benefit]
   ```

2. **Agent A's Analysis Process**:
   - Analyzes frontend requirements
   - Identifies API needs -> Consults Agent B if needed
   - Identifies sensor needs -> Consults Agent C if needed
   - Waits for responses from B and C
   - Consolidates everything into final report

3. **Review Agent A's Final Report**:
   - Overall complexity and effort
   - Component-by-component breakdown
   - Implementation order
   - Test case recommendations
   - Risk assessment
   - Go/No-Go recommendation

4. **Make Decision**:
   - [OK] Green light -> Proceed with implementation
   - [WARN] Yellow light -> Proceed with extra planning
   - [STOP] Red light -> Consider alternatives

5. **Implementation**:
   - Follow implementation order from Agent A
   - Use test cases as acceptance criteria
   - Monitor for flagged risks

### For AI Assistants Acting as Agents

**If you are Agent A** (Entry Point & Coordinator):
1. Receive all feature requests first
2. Analyze frontend impact immediately
3. Identify if you need backend support:
   - New API endpoints?
   - Data modifications?
   - Performance concerns?
   -> If YES: Send request to Agent B
4. Identify if you need in-car support:
   - New sensors?
   - New commands?
   - Data collection changes?
   -> If YES: Send request to Agent C
5. Wait for responses from B and/or C
6. Consolidate all responses into comprehensive report
7. Provide final go/no-go recommendation

**If you are Agent B** (Backend Support):
1. Wait for requests from Agent A
2. Analyze backend implications:
   - API design
   - Database changes
   - Performance impact
3. Check if you need sensor data from Agent C:
   - Send clarification request to Agent A
   - Agent A will forward to Agent C
4. Respond to Agent A with:
   - Implementation plan
   - Effort estimate
   - API specifications
   - Dependencies
   - Concerns

**If you are Agent C** (In-Car Support):
1. Wait for requests from Agent A
2. Analyze in-car system implications:
   - Sensor availability
   - Data collection feasibility
   - Simulation complexity
3. Respond to Agent A with:
   - Implementation plan
   - Effort estimate
   - Data specifications
   - Dependencies
   - Concerns

## Integration with Development Process

### Sprint Planning
- Run feature through agent analysis
- Use effort estimates for story pointing
- Use test cases for acceptance criteria

### Design Reviews
- Reference agent assessments
- Validate design against agent recommendations
- Address risks identified by agents

### Implementation
- Follow implementation order from agents
- Use agent-provided schemas and patterns
- Implement recommended test cases

### Testing
- Use agent test case recommendations as baseline
- Ensure cross-component integration tests
- Verify agent-identified risks are covered

### Code Review
- Check implementation against agent specs
- Verify API contracts match agent proposals
- Confirm test coverage meets recommendations

## Continuous Improvement

### Agent Knowledge Updates
When system changes significantly:
1. Update relevant agent document
2. Document new patterns/practices
3. Add new decision-making guidelines
4. Update example analyses

### Feedback Loop
After feature implementation:
1. Compare actual effort vs agent estimates
2. Note any unexpected issues
3. Update agent knowledge base
4. Refine assessment templates

## Quick Reference

### Communication Flow
```
Feature Request
    |
Agent A (analyzes)
    |
Agent A -> Agent B (if API needed)
    |
Agent A -> Agent C (if sensors needed)
    |
Agent B -> Agent A (responds)
    |
Agent C -> Agent A (responds)
    |
Agent A (consolidates)
    |
Final Report to User
```

### Who to Start With
- **ALL feature requests** -> Start with Agent A
- Agent A decides if B or C consultation is needed
- Never start with Agent B or C directly

### Agent Responsibilities

**Agent A (Coordinator)**:
- Entry point for all requests
- Frontend impact analysis
- Consult other agents
- Consolidate responses
- Final recommendation

**Agent B (Consultant)**:
- Respond to Agent A requests
- Backend/API expertise
- Database design
- Performance analysis

**Agent C (Consultant)**:
- Respond to Agent A requests
- Sensor expertise
- In-car systems
- Data collection
