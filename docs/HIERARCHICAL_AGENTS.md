# Hierarchical Agent Architecture

## Overview

The AI Agent Coordination system now uses a **hierarchical structure** where each component has its own dedicated agent. Each agent only knows about the APIs of its downstream dependencies, creating a clean separation of concerns.

## Agent Structure

### Frontend Layer (A-agents)

**Agent-A1: Car User Mobile App**
- Component: React Native mobile application
- APIs: `GET /bookings`, `POST /booking`, `GET /car-status`
- Can call: Agent-B1, Agent-B2
- Responsibilities: User authentication, car browsing, booking management, real-time car status

**Agent-A2: Rental Staff Web App**
- Component: React web application for staff
- APIs: `GET /fleet`, `PUT /car-status`, `GET /reports`
- Can call: Agent-B1, Agent-B3, Agent-B4
- Responsibilities: Fleet management UI, booking administration, staff dashboard, reports

### Backend Layer (B-agents)

**Agent-B1: Web Server (REST API)**
- Component: Node.js/Express REST API
- APIs: `/api/bookings`, `/api/cars`, `/api/users`, `/api/fleet`
- Can call: Agent-B3, Agent-B4, Agent-B2
- Responsibilities: REST endpoints, authentication, business logic, validation

**Agent-B2: IoT Gateway**
- Component: WebSocket/IoT server
- APIs: `ws://iot-gateway`, `/api/iot/status`, `/api/iot/command`
- Can call: Agent-C1, Agent-C2
- Responsibilities: WebSocket server, real-time updates, IoT communication, event streaming

**Agent-B3: Realtime Database (MongoDB)**
- Component: MongoDB database
- APIs: `mongodb://realtime-db`, Collections: `cars`, `sessions`, `iot_data`
- Can call: (none - leaf node)
- Responsibilities: Real-time data storage, car status, IoT data, sessions

**Agent-B4: Static Database (PostgreSQL)**
- Component: PostgreSQL database
- APIs: `postgresql://static-db`, Tables: `users`, `bookings`, `fleet`, `reports`
- Can call: (none - leaf node)
- Responsibilities: Transactional data, users, bookings, fleet data, reports

### In-Car System Layer (C-agents)

**Agent-C1: Cloud Communication**
- Component: Python cloud integration
- APIs: HTTP client to IoT Gateway, Redis pub/sub
- Can call: Agent-C2
- Responsibilities: Cloud connectivity, data sync, remote commands, status updates

**Agent-C2: Central Broker (Redis)**
- Component: Redis message broker
- APIs: `redis://broker`, Channels: `car_status`, `commands`, `sensor_data`
- Can call: Agent-C3, Agent-C4, Agent-C5
- Responsibilities: Message routing, pub/sub, data buffering, event distribution

**Agent-C3: CAN Bus Interface**
- Component: CAN bus integration
- APIs: CAN interface, vehicle data access
- Can call: (none - leaf node)
- Responsibilities: CAN bus communication, vehicle network, protocol translation

**Agent-C4: Vehicle Controller**
- Component: Embedded vehicle control
- APIs: Control commands, vehicle state
- Can call: Agent-C3
- Responsibilities: Vehicle control logic, command execution, safety checks, state management

**Agent-C5: Data Sensors**
- Component: IoT sensors
- APIs: Sensor readings, GPS coordinates, vehicle telemetry
- Can call: Agent-C3
- Responsibilities: Sensor data collection, GPS, fuel level, tire pressure, diagnostics

## How It Works

### 1. Feature Request Entry
When a feature request comes in, the system determines which frontend agents to start with based on keywords:
- Keywords like "mobile", "app", "user", "booking" → Start with Agent-A1
- Keywords like "staff", "admin", "fleet", "report" → Start with Agent-A2
- If unclear → Start with both A1 and A2

### 2. Recursive Analysis
Each agent:
1. Analyzes the feature request from its perspective
2. Determines which downstream agents it needs
3. Calls only those needed downstream agents
4. Each downstream agent repeats the process

### 3. Agent Isolation
**Key Principle**: Each agent only knows about:
- Its own responsibilities
- The APIs of its direct downstream dependencies
- It does NOT know about the entire system architecture

This creates a realistic separation where:
- Frontend agents know about backend API endpoints
- Backend agents know about database schemas
- IoT gateway knows about in-car system interfaces
- Each layer is decoupled from layers beyond its direct dependencies

### 4. Example Flow

**Feature**: "Add tire pressure monitoring to the car dashboard"

```
Agent-A1 (Mobile App)
  └─ Needs Agent-B1 (for API endpoint)
       └─ Needs Agent-B2 (for real-time data)
            └─ Needs Agent-C1 (for IoT communication)
                 └─ Needs Agent-C2 (for message broker)
                      └─ Needs Agent-C5 (for sensor data)
                           └─ Needs Agent-C3 (for CAN bus access)
```

Each agent makes an **independent AI-driven decision** about whether it needs help from downstream agents.

## Benefits

1. **Realistic Modeling**: Mimics real-world team structure where each developer knows their domain and APIs
2. **Scalability**: Easy to add new agents without modifying existing ones
3. **Clear Boundaries**: Each agent has well-defined responsibilities
4. **Dynamic Coordination**: AI decides the coordination flow, not hardcoded rules
5. **API-Focused**: Agents interact through defined APIs, just like real systems

## Output

The system generates:
1. **Analysis Report**: Shows which agents were involved, their analyses, and the coordination flow
2. **Code Examples**: Frontend (JSX), backend (JS), and sensor (Python) code
3. **UI Mockup**: ASCII art interface design
4. **Call Tree**: Visual representation of agent coordination hierarchy

## Configuration

All agents are defined in `scripts/ai-agent-coordinator.py` in the `AgentCoordinator.__init__()` method. Each agent specifies:
- `name`: Agent identifier (e.g., "Agent-B1")
- `component`: Component they're responsible for
- `role`: Their role/expertise
- `responsibilities`: List of specific responsibilities
- `apis`: APIs they expose
- `downstream_agents`: Agents they can call

## Usage

```bash
python scripts/ai-agent-coordinator.py "Add tire pressure monitoring" output-dir/
```

The system automatically:
1. Determines starting agents
2. Recursively analyzes through the hierarchy
3. Generates comprehensive analysis and code examples
4. Creates visual documentation
