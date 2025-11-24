#!/usr/bin/env python3
"""
Simple helper: read an AI analysis markdown report and emit one task file per known component.

Usage:
  scripts/create-component-tasks.py <analysis_md> <output_dir>

This script is intentionally conservative: it does not post to GitHub or create issues.
It creates local markdown files under <output_dir> that a developer or another script can
turn into issues/PRs later.
"""
import argparse
import os
import re
import sys

COMPONENTS = ["A1","A2","B1","B2","B3","B4","C1","C2","C5"]

# Component technology stacks and code templates
COMPONENT_INFO = {
    "A1": {
        "tech": "React Native (Mobile)",
        "template": """// Example: Add new screen/component
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function TirePressureScreen() {
  const [pressure, setPressure] = useState(null);
  
  useEffect(() => {
    // Fetch data from B1 API
    fetch('http://api.example.com/car/tire-pressure')
      .then(res => res.json())
      .then(data => setPressure(data));
  }, []);
  
  return (
    <View style={styles.container}>
      <Text>Tire Pressure: {pressure?.frontLeft} bar</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 }
});"""
    },
    "A2": {
        "tech": "React (Web)",
        "template": """// Example: Add new component
import React, { useState, useEffect } from 'react';
import './TirePressureDashboard.css';

export default function TirePressureDashboard() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://api.example.com/realtime');
    ws.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };
    return () => ws.close();
  }, []);
  
  return (
    <div className="dashboard">
      <h2>Fleet Tire Pressure</h2>
      {data.map(car => (
        <div key={car.id}>{car.licensePlate}: {car.tirePressure}</div>
      ))}
    </div>
  );
}"""
    },
    "B1": {
        "tech": "Node.js/Express (REST API)",
        "template": """// Example: Add new API endpoint
const express = require('express');
const router = express.Router();

// GET /api/car/:id/tire-pressure
router.get('/car/:id/tire-pressure', async (req, res) => {
  try {
    const carId = req.params.id;
    
    // Query B3 (MongoDB) for real-time data
    const car = await db.collection('cars').findOne({ carId });
    
    if (!car) {
      return res.status(404).json({ error: 'Car not found' });
    }
    
    res.json({
      carId: car.carId,
      tirePressure: {
        frontLeft: car.tirePressure.frontLeft,
        frontRight: car.tirePressure.frontRight,
        rearLeft: car.tirePressure.rearLeft,
        rearRight: car.tirePressure.rearRight,
        timestamp: car.tirePressure.timestamp
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;"""
    },
    "B2": {
        "tech": "Node.js/WebSocket (IoT Gateway)",
        "template": """// Example: WebSocket handler for real-time data
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 3002 });

// Receive data from C1 (in-car)
wss.on('connection', (ws) => {
  console.log('C1 connected');
  
  ws.on('message', async (data) => {
    try {
      const sensorData = JSON.parse(data);
      
      // Store in B3 (MongoDB)
      await db.collection('cars').updateOne(
        { carId: sensorData.carId },
        { 
          $set: { 
            tirePressure: sensorData.tirePressure,
            lastUpdate: new Date()
          }
        },
        { upsert: true }
      );
      
      // Broadcast to connected A2 clients
      wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(sensorData));
        }
      });
    } catch (error) {
      console.error('Error processing sensor data:', error);
    }
  });
});"""
    },
    "B3": {
        "tech": "MongoDB (Real-time Database)",
        "template": """// Example: MongoDB schema and queries
// Collection: cars
{
  "_id": ObjectId("..."),
  "carId": "car-001",
  "licensePlate": "ABC-123",
  "tirePressure": {
    "frontLeft": 2.3,
    "frontRight": 2.4,
    "rearLeft": 2.2,
    "rearRight": 2.2,
    "timestamp": ISODate("2025-11-24T10:00:00Z")
  },
  "lastUpdate": ISODate("2025-11-24T10:00:00Z")
}

// Index for fast lookups
db.cars.createIndex({ "carId": 1 });
db.cars.createIndex({ "licensePlate": 1 });
db.cars.createIndex({ "lastUpdate": -1 });

// Query example
db.cars.find({ 
  "tirePressure.frontLeft": { $lt: 2.0 } 
}).sort({ lastUpdate: -1 });"""
    },
    "B4": {
        "tech": "PostgreSQL (Static Database)",
        "template": """-- Example: Database schema and migrations
-- Table: cars
CREATE TABLE cars (
  id SERIAL PRIMARY KEY,
  car_id VARCHAR(50) UNIQUE NOT NULL,
  license_plate VARCHAR(20) UNIQUE NOT NULL,
  make VARCHAR(50),
  model VARCHAR(50),
  year INT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: maintenance_records
CREATE TABLE maintenance_records (
  id SERIAL PRIMARY KEY,
  car_id VARCHAR(50) REFERENCES cars(car_id),
  service_type VARCHAR(100),
  description TEXT,
  service_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Query example
SELECT c.license_plate, c.make, c.model, 
       COUNT(m.id) as maintenance_count
FROM cars c
LEFT JOIN maintenance_records m ON c.car_id = m.car_id
WHERE m.service_type = 'Tire Maintenance'
GROUP BY c.license_plate, c.make, c.model;"""
    },
    "C1": {
        "tech": "Python asyncio (Cloud Communication)",
        "template": """# Example: Cloud communication module
import asyncio
import websockets
import json
from redis import Redis

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

async def fetch_from_c2_and_send_to_b2():
    uri = "ws://backend.example.com:3002"
    
    async with websockets.connect(uri) as websocket:
        while True:
            # Fetch latest data from C2 (Redis)
            data = redis_client.get('sensors:tire_pressure:car-001')
            
            if data:
                sensor_data = json.loads(data)
                
                # Send to B2 via WebSocket
                await websocket.send(json.dumps(sensor_data))
                print(f"Sent data to B2: {sensor_data['carId']}")
            
            await asyncio.sleep(10)  # Every 10 seconds

if __name__ == '__main__':
    asyncio.run(fetch_from_c2_and_send_to_b2())"""
    },
    "C2": {
        "tech": "Redis (Message Broker)",
        "template": """# Example: Redis pub/sub configuration and usage
# Channels:
# - sensors:tire_pressure
# - sensors:temperature
# - sensors:gps
# - vehicle:commands

# Publisher (from C5):
import redis
import json

r = redis.Redis(host='localhost', port=6379)

sensor_data = {
    "carId": "car-001",
    "licensePlate": "ABC-123",
    "frontLeft": 2.3,
    "frontRight": 2.4,
    "rearLeft": 2.2,
    "rearRight": 2.2,
    "timestamp": "2025-11-24T10:00:00Z"
}

# Publish to channel
r.publish('sensors:tire_pressure', json.dumps(sensor_data))

# Store latest value
r.set('sensors:tire_pressure:car-001', json.dumps(sensor_data), ex=60)

# Subscriber (in C1):
pubsub = r.pubsub()
pubsub.subscribe('sensors:tire_pressure')

for message in pubsub.listen():
    if message['type'] == 'message':
        data = json.loads(message['data'])
        print(f"Received: {data}")"""
    },
    "C5": {
        "tech": "Python (Sensor Simulation)",
        "template": """# Example: Tire pressure sensor simulator
import time
import random
import json
import redis

class TirePressureSensor:
    def __init__(self, car_id, license_plate):
        self.car_id = car_id
        self.license_plate = license_plate
        self.redis_client = redis.Redis(host='localhost', port=6379)
        
        # Initial pressure values (bar)
        self.pressures = {
            'frontLeft': 2.3,
            'frontRight': 2.4,
            'rearLeft': 2.2,
            'rearRight': 2.2
        }
    
    def generate_reading(self):
        # Simulate small pressure changes
        for tire in self.pressures:
            change = random.uniform(-0.05, 0.05)
            self.pressures[tire] = max(1.5, min(2.8, 
                                       self.pressures[tire] + change))
        
        return {
            'carId': self.car_id,
            'licensePlate': self.license_plate,
            'tirePressure': {
                'frontLeft': round(self.pressures['frontLeft'], 2),
                'frontRight': round(self.pressures['frontRight'], 2),
                'rearLeft': round(self.pressures['rearLeft'], 2),
                'rearRight': round(self.pressures['rearRight'], 2)
            },
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    
    def publish(self):
        data = self.generate_reading()
        self.redis_client.publish('sensors:tire_pressure', 
                                  json.dumps(data))
        print(f"Published: {data['licensePlate']}")

if __name__ == '__main__':
    sensor = TirePressureSensor('car-001', 'ABC-123')
    while True:
        sensor.publish()
        time.sleep(10)  # Every 10 seconds"""
    }
}


def excerpt_for_component(text_lines, token, context=5):
    matches = []
    for i, line in enumerate(text_lines):
        if token in line:
            start = max(0, i - context)
            end = min(len(text_lines), i + context + 1)
            excerpt = "".join(text_lines[start:end]).strip()
            matches.append((i, excerpt))
    # fall back: if no direct match, try word-boundary search
    if not matches:
        pattern = re.compile(r"\b" + re.escape(token) + r"\b")
        for i, line in enumerate(text_lines):
            if pattern.search(line):
                start = max(0, i - context)
                end = min(len(text_lines), i + context + 1)
                excerpt = "".join(text_lines[start:end]).strip()
                matches.append((i, excerpt))
    return matches


def main():
    p = argparse.ArgumentParser(description="Create per-component task markdown files from analysis report")
    p.add_argument('analysis_md', help='Path to the AI analysis markdown file')
    p.add_argument('out_dir', help='Directory to write component task files')
    args = p.parse_args()

    if not os.path.isfile(args.analysis_md):
        print(f"[ERROR] Analysis file not found: {args.analysis_md}")
        return 2

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.analysis_md, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    created = 0
    for comp in COMPONENTS:
        matches = excerpt_for_component(lines, comp)
        comp_info = COMPONENT_INFO.get(comp, {})
        
        filename = os.path.join(args.out_dir, f"task-{comp}.md")
        with open(filename, 'w', encoding='utf-8') as out:
            out.write(f"# Task: {comp}\n\n")
            out.write(f"**Component**: {comp}\n")
            out.write(f"**Technology**: {comp_info.get('tech', 'N/A')}\n\n")
            out.write(f"Generated from analysis: `{os.path.basename(args.analysis_md)}`\n\n")
            
            if matches:
                out.write("## Analysis Excerpt\n\n```")
                # include up to 3 matches
                for idx, (lineno, excerpt) in enumerate(matches[:3]):
                    out.write(excerpt)
                    if idx != min(2, len(matches)-1):
                        out.write('\n---\n')
                out.write("\n```\n")
            else:
                out.write("## Analysis Excerpt\n\n")
                out.write("No direct excerpt found for component. Please review the analysis and add details.\n\n")

            # Add source code proposal
            if comp_info.get('template'):
                out.write('## Proposed Implementation\n\n')
                out.write(f"### Example Code for {comp}\n\n")
                out.write('```python' if comp in ['C1', 'C5'] else 
                         '```sql' if comp == 'B4' else
                         '```javascript' if comp in ['A1', 'A2', 'B1', 'B2'] else
                         '```')
                out.write('\n')
                out.write(comp_info['template'])
                out.write('\n```\n\n')
                out.write('**Note**: This is a template example. Adapt it based on the specific feature requirements from the analysis.\n\n')

            out.write('## Suggested Subtasks\n\n')
            out.write('- [ ] Review analysis excerpt and understand requirements\n')
            out.write('- [ ] Adapt the code template to specific feature needs\n')
            out.write('- [ ] Investigate required interface changes (APIs, events, DB)\n')
            out.write('- [ ] Implement changes in a small, well-scoped PR\n')
            out.write('- [ ] Add/adjust unit and integration tests\n')
            out.write('- [ ] Update API documentation if needed\n')
            out.write('- [ ] Create CI/CD/deployment notes if needed\n')

            out.write('\n## Notes\n\n')
            out.write(f'- Component: {comp}\n')
            out.write('- Effort: _(estimate from analysis)_\n')
            out.write('- Dependencies: _(list upstream/downstream components)_\n')
            out.write('- API Endpoints: _(if applicable)_\n')
            out.write('- Data Models: _(if applicable)_\n')

        created += 1

    print(f"[OK] Created {created} task files in {args.out_dir}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
