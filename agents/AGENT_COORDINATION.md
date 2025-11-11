# AI Agent Coordination System

## Overview

This document describes the AI agent system for the car demo project. Three specialized agents analyze feature requests and provide impact assessments across the entire system architecture.

## Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature Request                           │
│              "Add tire pressure monitoring"                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Agent Coordinator   │
        │  (Routes to agents)   │
        └──────────┬────────────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
    ┌─────────┬─────────┬─────────┐
    │ Agent A │ Agent B │ Agent C │
    │Frontend │ Backend │  In-Car │
    └────┬────┴────┬────┴────┬────┘
         │         │         │
         └─────────┼─────────┘
                   ▼
        ┌──────────────────────┐
        │  Consolidated Impact  │
        │    Assessment +       │
        │    Test Cases         │
        └──────────────────────┘
```

## Agent Roles

### Agent A - Frontend Component Agent
**File**: `agents/agent-a-frontend.md`

**Responsibilities**:
- Analyze UI/UX implications
- Assess API integration requirements
- Identify state management needs
- Recommend frontend test cases

**Components**:
- A1 Car User App (React Native)
- A2 Rental Staff App (React Web)

**Key Expertise**:
- React/React Native development
- REST API consumption
- Mobile and web UI patterns
- Frontend testing strategies

### Agent B - Backend Component Agent
**File**: `agents/agent-b-backend.md`

**Responsibilities**:
- Analyze API design implications
- Assess database schema changes
- Identify data flow requirements
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

### Agent C - In-Car Component Agent
**File**: `agents/agent-c-in-car.md`

**Responsibilities**:
- Analyze sensor requirements
- Assess communication protocols
- Identify simulation complexity
- Recommend in-car system test cases

**Components**:
- C1 Cloud Communication (Python)
- C2 Central Broker (Node.js)
- C5 Data Sensors (Python)

**Key Expertise**:
- Sensor data handling
- Redis pub/sub patterns
- WebSocket communication
- IoT system testing

## Feature Analysis Workflow

### Step 1: Initial Analysis
Each agent independently analyzes the feature request:

```markdown
Feature: [Feature Name]

Agent A Assessment:
- UI/UX Impact: [Low/Medium/High]
- New screens needed: [Yes/No]
- API changes required: [List]
- Estimated effort: [X hours]

Agent B Assessment:
- API changes: [New/Modified endpoints]
- Database changes: [Schema updates]
- Performance impact: [Assessment]
- Estimated effort: [X hours]

Agent C Assessment:
- New sensors needed: [Yes/No]
- Sensor types: [List]
- Data flow changes: [Description]
- Estimated effort: [X hours]
```

### Step 2: Cross-Component Communication

Agents communicate dependencies:

```
Agent A → Agent B: "Need GET /api/car/:licensePlate/tire-pressure endpoint"
Agent B → Agent C: "Need tire_pressure sensor data via Redis"
Agent C → Agent B: "Will publish to sensors:tire_pressure channel"
Agent B → Agent A: "API endpoint will be available, schema: {...}"
```

### Step 3: Consolidated Impact Assessment

```markdown
## Feature: [Feature Name]

### Overall Impact
- **Complexity**: Low | Medium | High
- **Breaking Changes**: Yes/No
- **Estimated Total Effort**: [X hours/days]

### Component Breakdown

#### Frontend (Agent A)
- Impact: [Summary]
- Changes: [List]
- Effort: [X hours]
- Risks: [List]

#### Backend (Agent B)
- Impact: [Summary]
- Changes: [List]
- Effort: [X hours]
- Risks: [List]

#### In-Car (Agent C)
- Impact: [Summary]
- Changes: [List]
- Effort: [X hours]
- Risks: [List]

### Implementation Order
1. [First component to implement]
2. [Second component]
3. [Third component]

### Testing Strategy
- Unit tests: [Count] across all components
- Integration tests: [Count]
- E2E tests: [Count]
- Total test effort: [X hours]

### Go/No-Go Recommendation
✅ PROCEED | ⚠️ PROCEED WITH CAUTION | 🔴 DO NOT PROCEED

Reasoning: [Explanation]
```

## Example: Complete Feature Analysis

### Feature Request: "Add Battery Level Monitoring"

#### Agent A - Frontend Analysis

```markdown
### Frontend Impact: LOW

**A1 Car User App**:
- Add battery gauge to car status screen
- Show battery percentage and charging status
- Add low battery warning (< 20%)

**A2 Rental Staff App**:
- Add battery column to fleet dashboard
- Add battery filter (show only low battery cars)
- Add battery chart to car details

**API Requirements**:
- Modify GET /api/car/:licensePlate to include batteryLevel field
- Add GET /api/cars?lowBattery=true filter

**Estimated Effort**: 6 hours
- A1 changes: 3 hours
- A2 changes: 3 hours

**Test Cases**: 8 unit tests, 4 integration tests, 2 E2E tests
```

#### Agent B - Backend Analysis

```markdown
### Backend Impact: LOW

**B1 Web Server**:
- Modify GET /api/car/:licensePlate response schema
- Add batteryLevel field (number, 0-100)
- Update Swagger documentation

**B2 IoT Gateway**:
- Accept batteryLevel in WebSocket messages
- Store in MongoDB car_data collection
- Forward to B1 via database query

**B3 MongoDB**:
- Add batteryLevel field to car_data collection
- No migration needed (schema-less)
- Add index: { batteryLevel: 1, timestamp: -1 }

**B4 PostgreSQL**:
- Optional: Add battery_capacity_kwh to cars table
- Not required for MVP

**Estimated Effort**: 8 hours
- B1 changes: 3 hours
- B2 changes: 3 hours
- B3 setup: 1 hour
- Testing: 1 hour

**Test Cases**: 12 unit tests, 6 integration tests, 3 E2E tests
```

#### Agent C - In-Car Analysis

```markdown
### In-Car Impact: LOW

**C5 Data Sensors**:
- Add battery sensor simulation
- Start at 100%, drain at ~0.1% per minute
- Simulate charging when parked
- Publish to Redis: sensors:battery_level

**C2 Central Broker**:
- Subscribe to sensors:battery_level
- Store in car:{licensePlate}:sensors hash
- Include in latest_data aggregation

**C1 Cloud Communication**:
- Forward batteryLevel in sensor_data messages
- No protocol changes needed

**Data Format**:
```json
{
  "value": 85.5,
  "unit": "percent",
  "charging": false,
  "timestamp": "2025-11-11T10:30:00Z",
  "licensePlate": "ABC-123"
}
```

**Estimated Effort**: 6 hours
- C5 sensor: 3 hours
- C2 changes: 2 hours
- Testing: 1 hour

**Test Cases**: 8 unit tests, 4 integration tests, 2 E2E tests
```

#### Consolidated Assessment

```markdown
## Feature: Add Battery Level Monitoring

### Overall Impact: LOW ✅

**Total Estimated Effort**: 20 hours
- Frontend: 6 hours
- Backend: 8 hours
- In-Car: 6 hours

**Breaking Changes**: None (additive change only)

**Implementation Order**:
1. C5: Add battery sensor (3 hours)
2. C2: Subscribe and aggregate (2 hours)
3. B2: Accept and store battery data (3 hours)
4. B1: Add to API response (3 hours)
5. A1/A2: Display in UI (6 hours)
6. Testing: Integration and E2E (3 hours)

**Total Test Cases**: 
- Unit: 28 tests
- Integration: 14 tests
- E2E: 7 tests
- Test development: ~6 hours

**Risks**: 
- None identified
- Backwards compatible
- No performance concerns

**Go/No-Go**: ✅ PROCEED

This is a low-risk, high-value feature that can be implemented incrementally 
without breaking existing functionality. Estimated delivery: 2-3 days.
```

## Agent Communication Protocols

### Standard Message Format

```markdown
FROM: Agent [A/B/C]
TO: Agent [A/B/C]
RE: [Feature Name]

REQUEST:
[Specific requirement or question]

DETAILS:
[Additional context]

DEPENDENCIES:
[What you need from the other agent]

TIMELINE:
[When you need this by]
```

### Example Communications

**Agent A to Agent B**:
```
FROM: Agent A (Frontend)
TO: Agent B (Backend)
RE: Battery Level Monitoring

REQUEST:
Need API endpoint to retrieve battery level for a car

DETAILS:
- Should include current battery percentage (0-100)
- Should include charging status (boolean)
- Should be part of existing car data endpoint

PROPOSED API:
GET /api/car/:licensePlate
Response: {
  ...existing fields...,
  "batteryLevel": 85.5,
  "charging": false
}

TIMELINE:
Need this before frontend development (Week 2)
```

**Agent B to Agent C**:
```
FROM: Agent B (Backend)
TO: Agent C (In-Car)
RE: Battery Level Monitoring

REQUEST:
Need battery level sensor data from in-car system

DETAILS:
- Data type: Number (0-100 percentage)
- Update frequency: Every 30 seconds
- Must include charging status

REQUIRED FORMAT:
Redis Channel: sensors:battery_level
Payload: {
  "value": 85.5,
  "unit": "percent",
  "charging": false,
  "timestamp": "ISO8601",
  "licensePlate": "ABC-123"
}

TIMELINE:
Need sensor operational by Week 1 for testing
```

**Agent C to Agent B**:
```
FROM: Agent C (In-Car)
TO: Agent B (Backend)
RE: Battery Level Monitoring

RESPONSE:
✅ Can provide battery level data

IMPLEMENTATION:
- Sensor: C5 battery_level_sensor.py
- Channel: sensors:battery_level
- Format: As specified
- Update: Every 30 seconds
- Additional: Will simulate charging when stationary

READY BY: End of Week 1

NOTES:
- Simulation will start at 100% and drain gradually
- When GPS velocity = 0 for 5+ minutes, will simulate charging
- Will include realistic charging curves (fast then slow)
```

## Decision Tree

```
Feature Request
    │
    ├─ Does it affect UI?
    │   └─ Yes → Consult Agent A
    │
    ├─ Does it need new API/data?
    │   └─ Yes → Consult Agent B
    │
    ├─ Does it need new sensors/car data?
    │   └─ Yes → Consult Agent C
    │
    └─ Coordination needed?
        ├─ Frontend + Backend → A ↔ B
        ├─ Backend + In-Car → B ↔ C
        └─ All three → A ↔ B ↔ C
```

## Risk Levels and Responses

### Low Risk (✅ PROCEED)
- Additive changes only
- No breaking changes
- Well-understood technology
- < 3 days effort
- Independent components

**Action**: Proceed with standard development

### Medium Risk (⚠️ PROCEED WITH CAUTION)
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

### High Risk (🔴 DO NOT PROCEED / MAJOR PLANNING REQUIRED)
- Major breaking changes
- Complex cross-component coordination
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

1. **Submit Feature Request**:
   - Describe the feature clearly
   - Include user stories
   - Specify requirements

2. **Agent Analysis**:
   - Review each agent's assessment
   - Understand cross-component impacts
   - Review test case recommendations

3. **Make Go/No-Go Decision**:
   - Consider consolidated risk assessment
   - Review effort estimates
   - Check team capacity

4. **Implementation**:
   - Follow recommended implementation order
   - Use test cases as acceptance criteria
   - Monitor for issues flagged by agents

### For AI Assistants Acting as Agents

1. **Read Your Agent Document**:
   - agent-a-frontend.md for frontend
   - agent-b-backend.md for backend
   - agent-c-in-car.md for in-car

2. **Analyze Feature Request**:
   - Use the analysis templates
   - Follow decision-making guidelines
   - Identify cross-agent dependencies

3. **Communicate with Other Agents**:
   - Use standard message format
   - Be specific about requirements
   - Provide clear schemas/interfaces

4. **Provide Comprehensive Output**:
   - Impact assessment
   - Test case recommendations
   - Risk analysis
   - Effort estimates

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

### Agent Contact Points
- **Frontend questions** → agent-a-frontend.md
- **Backend/API questions** → agent-b-backend.md
- **Sensor/IoT questions** → agent-c-in-car.md
- **Coordination** → This document

### Key Questions for Each Agent

**Agent A**:
- What UI changes are needed?
- Which apps are affected?
- What API data is required?

**Agent B**:
- What API endpoints are needed?
- What database changes are required?
- What's the performance impact?

**Agent C**:
- What sensor data is needed?
- How should data flow through Redis?
- What's the simulation complexity?
