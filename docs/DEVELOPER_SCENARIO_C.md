# Developer Scenario: Implementing Agent C - In-Car Systems

## Scenario Overview

**Feature Request**: "Add tire pressure monitoring to the car dashboard"

**Your Role**: In-Car Systems Developer (Agent C)

**Goal**: Implement tire pressure sensors and data transmission from the vehicle to the backend system.

---

## Agent C Architecture

```
[C5 - Data Sensors] -> [C2 - Central Broker] -> [C1 - Cloud Communication] -> Backend (Agent B)
```

**Components:**
- **C5**: Tire pressure sensors (Python simulators)
- **C2**: Redis message broker for in-car data aggregation
- **C1**: Cloud communication service (sends data to B1 API)

---

## Step 1: Set Up Development Environment

### Prerequisites

```bash
# Navigate to in-car systems directory
cd C-car-demo-in-car

# Install Python dependencies
pip install -r requirements.txt

# Start Redis (C2 broker)
docker-compose up -d redis
```

### Verify Setup

```bash
# Test Redis connection
docker exec -it redis redis-cli ping
# Expected: PONG

# Check Python environment
python -c "import redis, requests; print('Dependencies OK')"
```

---

## Step 2: Implement Tire Pressure Sensors (C5)

### Add Tire Pressure to Existing Simulator

Edit `C5-data-sensors/sensor_simulator.py`:

```python
import time
import random
import redis
import json
import argparse
from datetime import datetime

class TirePressureSensor:
    def __init__(self, car_id, redis_client):
        self.car_id = car_id
        self.redis = redis_client
        self.base_pressure = 2.2  # bar (normal pressure)
        
    def get_tire_pressure(self):
        """Generate realistic tire pressure data"""
        return {
            'front_left': round(self.base_pressure + random.uniform(-0.1, 0.1), 2),
            'front_right': round(self.base_pressure + random.uniform(-0.1, 0.1), 2),
            'rear_left': round(self.base_pressure + random.uniform(-0.1, 0.1), 2),
            'rear_right': round(self.base_pressure + random.uniform(-0.1, 0.1), 2)
        }
    
    def run(self):
        """Send tire pressure data every 5 seconds"""
        while True:
            try:
                pressure_data = {
                    'car_id': self.car_id,
                    'sensor_type': 'tire_pressure',
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': self.get_tire_pressure(),
                    'unit': 'bar'
                }
                
                # Send to Redis channel
                channel = f"sensor_data:{self.car_id}"
                self.redis.publish(channel, json.dumps(pressure_data))
                
                print(f"[{self.car_id}] Tire pressure: {pressure_data['data']}")
                time.sleep(5)  # Send every 5 seconds
                
            except Exception as e:
                print(f"Error sending tire pressure data: {e}")
                time.sleep(1)

# Add to existing sensor simulator main function
def start_tire_pressure_sensors(cars, redis_url):
    """Start tire pressure sensors for all cars"""
    redis_client = redis.Redis.from_url(redis_url)
    
    sensors = []
    for car_id in cars:
        sensor = TirePressureSensor(car_id, redis_client)
        sensors.append(sensor)
    
    # Run sensors in parallel (simplified for demo)
    import threading
    
    threads = []
    for sensor in sensors:
        thread = threading.Thread(target=sensor.run)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping tire pressure sensors...")
```

### Test Tire Pressure Sensors

```bash
# Start tire pressure sensors
cd C5-data-sensors
python sensor_simulator.py --cars CAR001 CAR002

# In another terminal, monitor Redis
redis-cli
> SUBSCRIBE sensor_data:CAR001
# Should see tire pressure data every 5 seconds
```

---

## Step 3: Configure Central Broker (C2)

### Redis Configuration

Edit `C2-central-broker/docker-compose.yml`:

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - car_network

volumes:
  redis_data:

networks:
  car_network:
    driver: bridge
```

### Data Aggregation Script

Create `C2-central-broker/data_aggregator.py`:

```python
import redis
import json
import time
from collections import defaultdict

class DataAggregator:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.latest_data = defaultdict(dict)
    
    def start_aggregation(self, cars):
        """Aggregate data from all car sensors"""
        # Subscribe to all car sensor channels
        for car_id in cars:
            channel = f"sensor_data:{car_id}"
            self.pubsub.subscribe(channel)
        
        print(f"Aggregating data for cars: {cars}")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    car_id = data['car_id']
                    sensor_type = data['sensor_type']
                    
                    # Store latest data for each sensor type
                    self.latest_data[car_id][sensor_type] = data
                    
                    # Forward to cloud communication
                    self.forward_to_cloud(data)
                    
                except Exception as e:
                    print(f"Error processing message: {e}")
    
    def forward_to_cloud(self, sensor_data):
        """Send aggregated data to cloud communication service"""
        cloud_channel = "cloud_upload"
        self.redis.publish(cloud_channel, json.dumps(sensor_data))
    
    def get_latest_data(self, car_id):
        """Get latest sensor data for a car"""
        return self.latest_data.get(car_id, {})

if __name__ == "__main__":
    aggregator = DataAggregator()
    cars = ["CAR001", "CAR002", "CAR003"]
    aggregator.start_aggregation(cars)
```

---

## Step 4: Implement Cloud Communication (C1)

### Cloud Uploader Service

Create `C1-cloud-communication/cloud_uploader.py`:

```python
import redis
import requests
import json
import time
from datetime import datetime

class CloudUploader:
    def __init__(self, 
                 redis_url="redis://localhost:6379",
                 backend_url="http://localhost:3001/api"):
        self.redis = redis.Redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.backend_url = backend_url
        self.pubsub.subscribe("cloud_upload")
    
    def start_uploading(self):
        """Listen for data and upload to backend"""
        print(f"Starting cloud uploader to {self.backend_url}")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    sensor_data = json.loads(message['data'])
                    self.upload_sensor_data(sensor_data)
                except Exception as e:
                    print(f"Error uploading data: {e}")
    
    def upload_sensor_data(self, data):
        """Upload sensor data to backend API"""
        if data['sensor_type'] == 'tire_pressure':
            self.upload_tire_pressure(data)
    
    def upload_tire_pressure(self, data):
        """Upload tire pressure data to B1 API"""
        try:
            # Transform data for backend API
            payload = {
                'car_id': data['car_id'],
                'timestamp': data['timestamp'],
                'pressures': {
                    'frontLeft': data['data']['front_left'],
                    'frontRight': data['data']['front_right'],
                    'rearLeft': data['data']['rear_left'],
                    'rearRight': data['data']['rear_right']
                },
                'unit': data['unit']
            }
            
            # POST to B1 monitoring endpoint
            url = f"{self.backend_url}/monitoring/tire-pressure"
            response = requests.post(url, 
                                   json=payload,
                                   timeout=5,
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print(f"[{data['car_id']}] Uploaded tire pressure data")
            else:
                print(f"[{data['car_id']}] Upload failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network error uploading data: {e}")
        except Exception as e:
            print(f"Error uploading tire pressure: {e}")

if __name__ == "__main__":
    uploader = CloudUploader()
    uploader.start_uploading()
```

---

## Step 5: Integration and Testing

### Start Complete Agent C System

Create `scripts/start_agent_c.sh`:

```bash
#!/bin/bash
echo "Starting Agent C - In-Car Systems"

# Start Redis (C2)
echo "Starting C2 - Central Broker..."
cd C2-central-broker
docker-compose up -d
cd ..

# Wait for Redis
sleep 3

# Start Data Aggregator
echo "Starting C2 - Data Aggregator..."
cd C2-central-broker
python data_aggregator.py &
AGGREGATOR_PID=$!
cd ..

# Start Cloud Uploader
echo "Starting C1 - Cloud Communication..."
cd C1-cloud-communication
python cloud_uploader.py &
UPLOADER_PID=$!
cd ..

# Start Tire Pressure Sensors
echo "Starting C5 - Tire Pressure Sensors..."
cd C5-data-sensors
python sensor_simulator.py --cars CAR001 CAR002 CAR003 &
SENSORS_PID=$!
cd ..

echo "Agent C system started!"
echo "PIDs: Aggregator=$AGGREGATOR_PID, Uploader=$UPLOADER_PID, Sensors=$SENSORS_PID"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping Agent C...'; kill $AGGREGATOR_PID $UPLOADER_PID $SENSORS_PID; docker-compose -f C2-central-broker/docker-compose.yml down" INT
wait
```

### Test Complete Flow

```bash
# Terminal 1: Start Agent C
chmod +x scripts/start_agent_c.sh
./scripts/start_agent_c.sh

# Terminal 2: Monitor Redis data
redis-cli monitor

# Terminal 3: Check backend API (if B1 is running)
curl http://localhost:3001/api/monitoring/tire-pressure/CAR001
```

---

## Step 6: Development Workflow

### Daily Development Tasks

1. **Sensor Development** (C5):
   ```bash
   cd C5-data-sensors
   python sensor_simulator.py --cars TEST001
   # Develop and test new sensor types
   ```

2. **Data Flow Testing** (C2):
   ```bash
   redis-cli
   > MONITOR  # Watch all Redis traffic
   ```

3. **Cloud Integration** (C1):
   ```bash
   cd C1-cloud-communication
   python cloud_uploader.py
   # Test API integration with backend
   ```

### Debugging

```bash
# Check Redis connections
redis-cli ping

# Monitor specific car data
redis-cli
> SUBSCRIBE sensor_data:CAR001

# Test backend connectivity
curl -X POST http://localhost:3001/api/monitoring/tire-pressure \
  -H "Content-Type: application/json" \
  -d '{"car_id":"TEST","pressures":{"frontLeft":2.2}}'
```

---

## Step 7: Production Deployment

### Docker Compose for Agent C

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  c2-redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - car_network
  
  c2-aggregator:
    build: 
      context: ./C2-central-broker
      dockerfile: Dockerfile
    depends_on:
      - c2-redis
    environment:
      - REDIS_URL=redis://c2-redis:6379
    networks:
      - car_network
  
  c1-uploader:
    build:
      context: ./C1-cloud-communication
      dockerfile: Dockerfile
    depends_on:
      - c2-redis
    environment:
      - REDIS_URL=redis://c2-redis:6379
      - BACKEND_URL=http://backend:3001/api
    networks:
      - car_network
  
  c5-sensors:
    build:
      context: ./C5-data-sensors
      dockerfile: Dockerfile
    depends_on:
      - c2-redis
    environment:
      - REDIS_URL=redis://c2-redis:6379
      - CARS=CAR001,CAR002,CAR003
    networks:
      - car_network

volumes:
  redis_data:

networks:
  car_network:
    external: true
```

### Deployment Commands

```bash
# Build and start all Agent C services
docker-compose up -d

# Scale sensors for more cars
docker-compose up -d --scale c5-sensors=3

# View logs
docker-compose logs -f c1-uploader
docker-compose logs -f c2-aggregator
```

---

## Suggested Subtasks

1. **Setup Environment** (30 min)
   - Install Redis and Python dependencies
   - Verify connections between components

2. **Implement Tire Pressure Sensors** (2 hours)
   - Add TirePressureSensor class to simulator
   - Generate realistic pressure variations
   - Test data transmission to Redis

3. **Configure Data Aggregation** (1 hour)
   - Set up Redis channels for sensor data
   - Implement data forwarding to cloud service

4. **Build Cloud Communication** (2 hours)
   - Create HTTP client for backend API
   - Transform sensor data to backend format
   - Add error handling and retry logic

5. **Integration Testing** (1 hour)
   - Test complete C5->C2->C1->B1 data flow
   - Verify data arrives at backend monitoring API

6. **Docker Deployment** (1 hour)
   - Create Dockerfiles for each service
   - Configure docker-compose for production

---

## Notes

- **Real Hardware**: In production, C5 would interface with actual tire pressure sensors via CAN bus or OBD-II
- **Security**: Add authentication for cloud communication in production
- **Reliability**: Implement data buffering in case of network outages
- **Monitoring**: Add health checks and metrics for all services
- **NO dependency on A1/B1**: Agent C can be developed and tested independently using mock backend

**Total Estimated Effort**: 6-8 hours for complete implementation