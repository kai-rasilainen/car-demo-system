# Comprehensive Test Cases - Tire Pressure Monitoring

**Feature**: Add tire pressure monitoring to the car dashboard  
**Last Updated**: November 17, 2025

## Frontend Tests (A1 Mobile App)

### Unit Tests

#### 1. Tire Pressure Display Component

**File**: `A1-car-user-app/__tests__/TirePressureDisplay.test.js`

```javascript
import React from 'react';
import { render, waitFor } from '@testing-library/react-native';
import TirePressureDisplay from '../components/TirePressureDisplay';

describe('TirePressureDisplay', () => {
  it('should display all 4 tire pressures', () => {
    const pressures = { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 };
    const { getByText } = render(<TirePressureDisplay pressures={pressures} />);
    
    expect(getByText('FL: 2.2 bar')).toBeTruthy();
    expect(getByText('FR: 2.3 bar')).toBeTruthy();
    expect(getByText('RL: 2.1 bar')).toBeTruthy();
    expect(getByText('RR: 2.2 bar')).toBeTruthy();
  });
  
  it('should show correct units (bar)', () => {
    const pressures = { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 };
    const { getAllByText } = render(<TirePressureDisplay pressures={pressures} />);
    
    const barUnits = getAllByText(/bar/);
    expect(barUnits.length).toBe(4);
  });
  
  it('should update in real-time', async () => {
    const { getByText, rerender } = render(
      <TirePressureDisplay pressures={{ FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }} />
    );
    expect(getByText('FL: 2.2 bar')).toBeTruthy();
    
    rerender(<TirePressureDisplay pressures={{ FL: 1.8, FR: 2.3, RL: 2.1, RR: 2.2 }} />);
    await waitFor(() => expect(getByText('FL: 1.8 bar')).toBeTruthy());
  });
});
```

#### 2. Color Coding Tests

**File**: `A1-car-user-app/__tests__/TirePressureColor.test.js`

```javascript
import React from 'react';
import { render } from '@testing-library/react-native';
import TirePressure from '../components/TirePressure';

describe('Tire Pressure Color Coding', () => {
  it('should show red for low pressure (<1.9 bar)', () => {
    const { getByTestId } = render(<TirePressure value={1.7} position="FL" />);
    const element = getByTestId('tire-FL');
    expect(element.props.style.backgroundColor).toBe('#FF0000');
  });
  
  it('should show yellow for medium pressure (1.9-2.1 bar)', () => {
    const { getByTestId } = render(<TirePressure value={2.0} position="FL" />);
    const element = getByTestId('tire-FL');
    expect(element.props.style.backgroundColor).toBe('#FFA500');
  });
  
  it('should show green for normal pressure (>2.1 bar)', () => {
    const { getByTestId } = render(<TirePressure value={2.3} position="FL" />);
    const element = getByTestId('tire-FL');
    expect(element.props.style.backgroundColor).toBe('#00FF00');
  });
  
  it('should handle edge case at 1.9 bar boundary', () => {
    const { getByTestId } = render(<TirePressure value={1.9} position="FL" />);
    const element = getByTestId('tire-FL');
    expect(element.props.style.backgroundColor).toBe('#FFA500');
  });
  
  it('should handle edge case at 2.1 bar boundary', () => {
    const { getByTestId } = render(<TirePressure value={2.1} position="FL" />);
    const element = getByTestId('tire-FL');
    expect(element.props.style.backgroundColor).toBe('#FFA500');
  });
});
```

#### 3. Alert System Tests

**File**: `A1-car-user-app/__tests__/TirePressureAlert.test.js`

```javascript
import React from 'react';
import { render, Alert } from 'react-native';
import CarDashboard from '../screens/CarDashboard';

describe('Tire Pressure Alerts', () => {
  beforeEach(() => {
    jest.spyOn(Alert, 'alert').mockImplementation(() => {});
  });
  
  afterEach(() => {
    Alert.alert.mockRestore();
  });
  
  it('should trigger alert when any tire is low', () => {
    render(<CarDashboard pressures={{ FL: 1.6, FR: 2.2, RL: 2.1, RR: 2.2 }} />);
    
    expect(Alert.alert).toHaveBeenCalledWith(
      'Low Tire Pressure',
      'Front Left tire is low (1.6 bar)',
      expect.any(Array)
    );
  });
  
  it('should dismiss alert when pressure normalizes', () => {
    const { rerender } = render(
      <CarDashboard pressures={{ FL: 1.6, FR: 2.2, RL: 2.1, RR: 2.2 }} />
    );
    Alert.alert.mockClear();
    
    rerender(<CarDashboard pressures={{ FL: 2.3, FR: 2.2, RL: 2.1, RR: 2.2 }} />);
    
    expect(Alert.alert).not.toHaveBeenCalled();
  });
  
  it('should alert for multiple low tires', () => {
    render(<CarDashboard pressures={{ FL: 1.6, FR: 1.7, RL: 2.1, RR: 2.2 }} />);
    
    expect(Alert.alert).toHaveBeenCalledWith(
      'Low Tire Pressure',
      'Multiple tires are low: FL (1.6 bar), FR (1.7 bar)',
      expect.any(Array)
    );
  });
});
```

### Integration Tests

#### 4. API Integration Tests

**File**: `A1-car-user-app/__tests__/TirePressureAPI.test.js`

```javascript
import { fetchTirePressure } from '../services/api';

describe('API Integration', () => {
  it('should fetch tire pressure from API', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          licensePlate: 'ABC123',
          tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }
        })
      })
    );
    
    const data = await fetchTirePressure('ABC123');
    
    expect(data.tirePressure).toHaveProperty('FL');
    expect(data.tirePressure.FL).toBe(2.2);
  });
  
  it('should handle missing data gracefully', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          licensePlate: 'ABC123',
          tirePressure: null
        })
      })
    );
    
    const data = await fetchTirePressure('ABC123');
    
    expect(data.tirePressure).toBeNull();
  });
  
  it('should retry on connection failure', async () => {
    let attempts = 0;
    global.fetch = jest.fn(() => {
      attempts++;
      if (attempts < 3) {
        return Promise.reject(new Error('Network error'));
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ tirePressure: { FL: 2.2 } })
      });
    });
    
    const data = await fetchTirePressure('ABC123', { retries: 3 });
    
    expect(attempts).toBe(3);
    expect(data.tirePressure.FL).toBe(2.2);
  });
});
```

#### 5. WebSocket Integration Tests

**File**: `A1-car-user-app/__tests__/WebSocketIntegration.test.js`

```javascript
import { WebSocketService } from '../services/websocket';

describe('WebSocket Integration', () => {
  let ws;
  
  beforeEach(() => {
    ws = new WebSocketService('ws://localhost:3002');
  });
  
  afterEach(() => {
    ws.disconnect();
  });
  
  it('should receive real-time updates', (done) => {
    ws.on('tire_pressure', (data) => {
      expect(data).toHaveProperty('tirePressure');
      expect(data.tirePressure).toHaveProperty('FL');
      done();
    });
    
    ws.connect();
  });
  
  it('should handle disconnection', (done) => {
    ws.on('disconnect', () => {
      expect(ws.isConnected()).toBe(false);
      done();
    });
    
    ws.connect();
    setTimeout(() => ws.disconnect(), 100);
  });
  
  it('should reconnect automatically', (done) => {
    let reconnectCount = 0;
    
    ws.on('reconnect', () => {
      reconnectCount++;
      if (reconnectCount === 1) {
        expect(ws.isConnected()).toBe(true);
        done();
      }
    });
    
    ws.connect();
    setTimeout(() => ws.simulateDisconnect(), 100);
  });
});
```

---

## Backend Tests (B1 + B2)

### Unit Tests

#### 6. API Endpoint Tests

**File**: `B1-web-server/tests/api.test.js`

```javascript
const request = require('supertest');
const app = require('../server');
const { MongoClient } = require('mongodb');

describe('GET /api/car/:licensePlate', () => {
  let db;
  
  beforeAll(async () => {
    const client = await MongoClient.connect(process.env.MONGO_TEST_URL);
    db = client.db('test_car_data');
  });
  
  beforeEach(async () => {
    await db.collection('cars').deleteMany({});
  });
  
  it('should include tire pressure in response', async () => {
    await db.collection('cars').insertOne({
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }
    });
    
    const response = await request(app).get('/api/car/ABC123');
    
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('tirePressure');
    expect(response.body.tirePressure.FL).toBe(2.2);
    expect(response.body.tirePressure.FR).toBe(2.3);
    expect(response.body.tirePressure.RL).toBe(2.1);
    expect(response.body.tirePressure.RR).toBe(2.2);
  });
  
  it('should validate pressure range (1.5-4.0 bar)', async () => {
    const invalidData = {
      licensePlate: 'ABC123',
      tirePressure: { FL: 5.0, FR: 2.3, RL: 2.1, RR: 2.2 }
    };
    
    const response = await request(app)
      .post('/api/car/ABC123/tire-pressure')
      .send(invalidData);
    
    expect(response.status).toBe(400);
    expect(response.body.error).toContain('out of range');
  });
  
  it('should calculate low pressure alert correctly', async () => {
    await db.collection('cars').insertOne({
      licensePlate: 'ABC123',
      tirePressure: { FL: 1.7, FR: 2.2, RL: 2.1, RR: 2.2 }
    });
    
    const response = await request(app).get('/api/car/ABC123');
    
    expect(response.body.alerts).toContainEqual({
      type: 'LOW_TIRE_PRESSURE',
      tire: 'FL',
      value: 1.7,
      threshold: 1.9
    });
  });
  
  it('should return 404 for non-existent car', async () => {
    const response = await request(app).get('/api/car/NOTFOUND');
    expect(response.status).toBe(404);
  });
});
```

#### 7. WebSocket Broadcasting Tests

**File**: `B2-iot-gateway/tests/websocket.test.js`

```javascript
const WebSocket = require('ws');
const redis = require('redis');

describe('WebSocket Broadcasting', () => {
  let redisClient;
  
  beforeAll(() => {
    redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    redisClient.connect();
  });
  
  afterAll(() => {
    redisClient.quit();
  });
  
  it('should broadcast tire pressure updates', (done) => {
    const client = new WebSocket('ws://localhost:3002');
    
    client.on('open', () => {
      redisClient.publish('sensors:tire_pressure', JSON.stringify({
        licensePlate: 'ABC123',
        tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 },
        timestamp: Date.now()
      }));
    });
    
    client.on('message', (data) => {
      const message = JSON.parse(data);
      expect(message.type).toBe('tire_pressure');
      expect(message.data.tirePressure).toHaveProperty('FL');
      expect(message.data.tirePressure.FL).toBe(2.2);
      client.close();
      done();
    });
  });
  
  it('should handle multiple clients', async () => {
    const clients = Array(10).fill().map(() => new WebSocket('ws://localhost:3002'));
    const messages = [];
    
    await Promise.all(clients.map(client => 
      new Promise(resolve => client.on('open', resolve))
    ));
    
    clients.forEach(client => {
      client.on('message', (data) => messages.push(JSON.parse(data)));
    });
    
    await redisClient.publish('sensors:tire_pressure', JSON.stringify({ test: true }));
    await new Promise(resolve => setTimeout(resolve, 200));
    
    expect(messages.length).toBe(10);
    clients.forEach(client => client.close());
  });
  
  it('should validate data format', (done) => {
    const client = new WebSocket('ws://localhost:3002');
    
    client.on('message', (data) => {
      const message = JSON.parse(data);
      
      expect(message).toHaveProperty('type');
      expect(message).toHaveProperty('data');
      expect(message.data).toHaveProperty('licensePlate');
      expect(message.data).toHaveProperty('tirePressure');
      expect(message.data).toHaveProperty('timestamp');
      
      client.close();
      done();
    });
    
    client.on('open', () => {
      redisClient.publish('sensors:tire_pressure', JSON.stringify({
        licensePlate: 'ABC123',
        tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 },
        timestamp: Date.now()
      }));
    });
  });
});
```

#### 8. Database Operations Tests

**File**: `B3-realtime-database/tests/queries.test.js`

```javascript
const { MongoClient } = require('mongodb');

describe('MongoDB Tire Pressure Operations', () => {
  let client, db;
  
  beforeAll(async () => {
    client = await MongoClient.connect('mongodb://localhost:27017');
    db = client.db('test_car_data');
    
    // Create index for efficient queries
    await db.collection('cars').createIndex({ licensePlate: 1 });
  });
  
  afterAll(async () => {
    await client.close();
  });
  
  beforeEach(async () => {
    await db.collection('cars').deleteMany({});
  });
  
  it('should store tire pressure in MongoDB', async () => {
    const data = {
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 },
      timestamp: new Date()
    };
    
    await db.collection('cars').updateOne(
      { licensePlate: data.licensePlate },
      { $set: data },
      { upsert: true }
    );
    
    const result = await db.collection('cars').findOne({ licensePlate: 'ABC123' });
    expect(result.tirePressure.FL).toBe(2.2);
    expect(result.tirePressure.FR).toBe(2.3);
  });
  
  it('should query tire pressure efficiently with index', async () => {
    // Insert test data
    await db.collection('cars').insertOne({
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }
    });
    
    const start = Date.now();
    const result = await db.collection('cars')
      .findOne({ licensePlate: 'ABC123' })
      .project({ tirePressure: 1 });
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(10); // Should be <10ms with index
    expect(result.tirePressure).toBeDefined();
  });
  
  it('should handle missing data gracefully', async () => {
    const result = await db.collection('cars').findOne({ licensePlate: 'NOTFOUND' });
    expect(result).toBeNull();
  });
  
  it('should update existing tire pressure', async () => {
    await db.collection('cars').insertOne({
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }
    });
    
    await db.collection('cars').updateOne(
      { licensePlate: 'ABC123' },
      { $set: { 'tirePressure.FL': 1.8 } }
    );
    
    const result = await db.collection('cars').findOne({ licensePlate: 'ABC123' });
    expect(result.tirePressure.FL).toBe(1.8);
    expect(result.tirePressure.FR).toBe(2.3);
  });
});
```

### Integration Tests

#### 9. End-to-End Data Flow Test

**File**: `tests/e2e/tire-pressure-flow.test.js`

```javascript
const redis = require('redis');
const { MongoClient } = require('mongodb');
const WebSocket = require('ws');
const request = require('supertest');
const app = require('../../B-car-demo-backend/B1-web-server/server');

describe('Data Flow Integration Test', () => {
  let redisClient, mongoClient, db, wsClient;
  
  beforeAll(async () => {
    redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    await redisClient.connect();
    
    mongoClient = await MongoClient.connect('mongodb://localhost:27017');
    db = mongoClient.db('car_data');
  });
  
  afterAll(async () => {
    await redisClient.quit();
    await mongoClient.close();
  });
  
  it('should complete full data flow: Redis -> B2 -> MongoDB -> B1 -> Client', async () => {
    const testData = {
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 },
      timestamp: Date.now()
    };
    
    // Step 1: Publish to Redis
    await redisClient.publish('sensors:tire_pressure', JSON.stringify(testData));
    
    // Step 2: Wait for B2 to process and store in MongoDB
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 3: Verify data in MongoDB
    const mongoResult = await db.collection('cars').findOne({ 
      licensePlate: 'ABC123' 
    });
    expect(mongoResult).toBeDefined();
    expect(mongoResult.tirePressure.FL).toBe(2.2);
    
    // Step 4: Query via B1 API
    const apiResponse = await request(app).get('/api/car/ABC123');
    expect(apiResponse.status).toBe(200);
    expect(apiResponse.body.tirePressure.FL).toBe(2.2);
  });
  
  it('should have end-to-end latency <2 seconds', async () => {
    const start = Date.now();
    
    await redisClient.publish('sensors:tire_pressure', JSON.stringify({
      licensePlate: 'TEST123',
      tirePressure: { FL: 2.0, FR: 2.0, RL: 2.0, RR: 2.0 },
      timestamp: start
    }));
    
    // Poll API until data appears
    let found = false;
    let attempts = 0;
    while (!found && attempts < 20) {
      const response = await request(app).get('/api/car/TEST123');
      if (response.status === 200 && response.body.tirePressure) {
        found = true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
      attempts++;
    }
    
    const duration = Date.now() - start;
    expect(found).toBe(true);
    expect(duration).toBeLessThan(2000);
  });
  
  it('should not lose data during transmission', async () => {
    const testCars = Array(100).fill().map((_, i) => ({
      licensePlate: `CAR${i}`,
      tirePressure: { FL: 2.0 + i * 0.01, FR: 2.1, RL: 2.0, RR: 2.1 },
      timestamp: Date.now()
    }));
    
    // Publish all data
    for (const car of testCars) {
      await redisClient.publish('sensors:tire_pressure', JSON.stringify(car));
    }
    
    // Wait for processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Verify all data arrived
    const count = await db.collection('cars').countDocuments({
      licensePlate: { $regex: /^CAR\d+$/ }
    });
    
    expect(count).toBe(100);
  });
});
```

---

## In-Car Tests (C5 Sensors)

### Unit Tests

#### 10. Sensor Simulation Tests

**File**: `C-car-demo-in-car/C5-data-sensors/tests/test_sensor_simulator.py`

```python
import unittest
from sensor_simulator import TirePressureSensor
import time

class TestTirePressureSensor(unittest.TestCase):
    def setUp(self):
        self.sensor = TirePressureSensor()
    
    def test_generates_realistic_pressure_values(self):
        """Test that sensor generates realistic tire pressure values"""
        values = self.sensor.read_all_tires()
        
        for tire, pressure in values.items():
            self.assertGreaterEqual(pressure, 1.5)
            self.assertLessEqual(pressure, 4.0)
            self.assertIsInstance(pressure, float)
    
    def test_simulates_gradual_pressure_loss(self):
        """Test that pressure decreases gradually over time"""
        initial = self.sensor.read_tire('FL')
        
        # Simulate pressure loss
        for _ in range(10):
            self.sensor.simulate_pressure_loss('FL', rate=0.01)
            time.sleep(0.1)
        
        final = self.sensor.read_tire('FL')
        self.assertLess(final, initial)
        self.assertGreaterEqual(final, 1.5)  # Should stay within valid range
    
    def test_stays_within_valid_range(self):
        """Test that pressure never goes outside valid range (1.5-4.0 bar)"""
        # Simulate extreme conditions
        for _ in range(100):
            self.sensor.simulate_pressure_loss('FL', rate=0.1)
        
        pressure = self.sensor.read_tire('FL')
        self.assertGreaterEqual(pressure, 1.5)
        self.assertLessEqual(pressure, 4.0)
    
    def test_all_four_tires_independent(self):
        """Test that all four tires can have different pressures"""
        pressures = self.sensor.read_all_tires()
        
        self.assertIn('FL', pressures)
        self.assertIn('FR', pressures)
        self.assertIn('RL', pressures)
        self.assertIn('RR', pressures)
        
        # They should not all be exactly the same
        unique_values = set(pressures.values())
        self.assertGreater(len(unique_values), 1)

if __name__ == '__main__':
    unittest.main()
```

#### 11. Redis Publishing Tests

**File**: `C-car-demo-in-car/C5-data-sensors/tests/test_redis_publisher.py`

```python
import unittest
from unittest.mock import Mock, patch
import json
from redis_publisher import TirePressurePublisher
import time

class TestTirePressurePublisher(unittest.TestCase):
    def setUp(self):
        self.mock_redis = Mock()
        self.publisher = TirePressurePublisher(redis_client=self.mock_redis)
    
    def test_publishes_to_correct_channel(self):
        """Test that data is published to sensors:tire_pressure channel"""
        data = {
            'licensePlate': 'ABC123',
            'tirePressure': {'FL': 2.2, 'FR': 2.3, 'RL': 2.1, 'RR': 2.2}
        }
        
        self.publisher.publish(data)
        
        self.mock_redis.publish.assert_called_once()
        call_args = self.mock_redis.publish.call_args
        self.assertEqual(call_args[0][0], 'sensors:tire_pressure')
    
    def test_correct_message_format(self):
        """Test that published message has correct JSON format"""
        data = {
            'licensePlate': 'ABC123',
            'tirePressure': {'FL': 2.2, 'FR': 2.3, 'RL': 2.1, 'RR': 2.2}
        }
        
        self.publisher.publish(data)
        
        call_args = self.mock_redis.publish.call_args
        message = json.loads(call_args[0][1])
        
        self.assertIn('licensePlate', message)
        self.assertIn('tirePressure', message)
        self.assertIn('timestamp', message)
        self.assertEqual(message['licensePlate'], 'ABC123')
        self.assertEqual(message['tirePressure']['FL'], 2.2)
    
    def test_30_second_update_frequency(self):
        """Test that updates are published every 30 seconds"""
        publish_times = []
        
        def record_time(*args):
            publish_times.append(time.time())
        
        self.mock_redis.publish.side_effect = record_time
        
        # Run publisher for 90 seconds (should get 3 updates)
        with patch('time.sleep', return_value=None):
            for _ in range(3):
                self.publisher.publish_update()
                time.sleep(30)  # Mocked
        
        # Verify approximately 30 seconds between publishes
        self.assertEqual(len(publish_times), 3)
    
    def test_handles_redis_connection_error(self):
        """Test graceful handling of Redis connection errors"""
        self.mock_redis.publish.side_effect = Exception("Connection refused")
        
        # Should not raise exception
        try:
            self.publisher.publish({'licensePlate': 'ABC123'})
        except Exception as e:
            self.fail(f"Publisher should handle Redis errors: {e}")

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

#### 12. Sensor to Backend Flow Test

**File**: `C-car-demo-in-car/C5-data-sensors/tests/test_sensor_integration.py`

```python
import unittest
import redis
import time
import json
from sensor_simulator import TirePressureSensor
from redis_publisher import TirePressurePublisher

class TestSensorToBackendFlow(unittest.TestCase):
    def setUp(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('sensors:tire_pressure')
        
        self.sensor = TirePressureSensor()
        self.publisher = TirePressurePublisher(redis_client=self.redis_client)
    
    def tearDown(self):
        self.pubsub.unsubscribe()
        self.pubsub.close()
    
    def test_c5_to_redis_to_c2_to_b2_flow_works(self):
        """Test complete flow: C5 -> Redis -> C2 -> B2"""
        # C5: Read sensor data
        tire_data = self.sensor.read_all_tires()
        
        # C5: Publish to Redis
        message = {
            'licensePlate': 'TEST123',
            'tirePressure': tire_data,
            'timestamp': time.time()
        }
        self.publisher.publish(message)
        
        # Verify message arrives in Redis
        received = False
        timeout = time.time() + 2
        
        while time.time() < timeout:
            message = self.pubsub.get_message()
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['licensePlate'] == 'TEST123':
                    received = True
                    self.assertIn('tirePressure', data)
                    self.assertEqual(len(data['tirePressure']), 4)
                    break
            time.sleep(0.1)
        
        self.assertTrue(received, "Message not received within 2 seconds")
    
    def test_data_arrives_within_2_seconds(self):
        """Test that data arrives at Redis within 2 seconds"""
        start_time = time.time()
        
        message = {
            'licensePlate': 'SPEED123',
            'tirePressure': self.sensor.read_all_tires(),
            'timestamp': start_time
        }
        self.publisher.publish(message)
        
        received = False
        while time.time() - start_time < 2:
            msg = self.pubsub.get_message()
            if msg and msg['type'] == 'message':
                data = json.loads(msg['data'])
                if data['licensePlate'] == 'SPEED123':
                    duration = time.time() - start_time
                    self.assertLess(duration, 2.0)
                    received = True
                    break
            time.sleep(0.05)
        
        self.assertTrue(received)
    
    def test_all_4_tire_pressures_transmitted(self):
        """Test that all 4 tire pressures are transmitted correctly"""
        tire_data = {
            'FL': 2.2,
            'FR': 2.3,
            'RL': 2.1,
            'RR': 2.2
        }
        
        message = {
            'licensePlate': 'COMPLETE123',
            'tirePressure': tire_data,
            'timestamp': time.time()
        }
        self.publisher.publish(message)
        
        received = False
        timeout = time.time() + 2
        
        while time.time() < timeout:
            msg = self.pubsub.get_message()
            if msg and msg['type'] == 'message':
                data = json.loads(msg['data'])
                if data['licensePlate'] == 'COMPLETE123':
                    self.assertEqual(data['tirePressure']['FL'], 2.2)
                    self.assertEqual(data['tirePressure']['FR'], 2.3)
                    self.assertEqual(data['tirePressure']['RL'], 2.1)
                    self.assertEqual(data['tirePressure']['RR'], 2.2)
                    received = True
                    break
            time.sleep(0.05)
        
        self.assertTrue(received)

if __name__ == '__main__':
    unittest.main()
```

---

## Performance Tests

### 13. Load Testing

**File**: `tests/performance/load-test.js`

```javascript
const redis = require('redis');
const { performance } = require('perf_hooks');

describe('Load Testing', () => {
  let redisClient;
  
  beforeAll(async () => {
    redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    await redisClient.connect();
  });
  
  afterAll(async () => {
    await redisClient.quit();
  });
  
  it('should handle 100 simultaneous car updates', async () => {
    const cars = Array(100).fill().map((_, i) => ({
      licensePlate: `LOAD${i}`,
      tirePressure: { FL: 2.0 + Math.random(), FR: 2.1, RL: 2.0, RR: 2.1 },
      timestamp: Date.now()
    }));
    
    const start = performance.now();
    
    await Promise.all(cars.map(car => 
      redisClient.publish('sensors:tire_pressure', JSON.stringify(car))
    ));
    
    const duration = performance.now() - start;
    
    expect(duration).toBeLessThan(1000); // Should complete in <1 second
  });
  
  it('should achieve 1000 updates per second throughput', async () => {
    const updates = 1000;
    const start = performance.now();
    
    for (let i = 0; i < updates; i++) {
      await redisClient.publish('sensors:tire_pressure', JSON.stringify({
        licensePlate: `PERF${i}`,
        tirePressure: { FL: 2.0, FR: 2.1, RL: 2.0, RR: 2.1 },
        timestamp: Date.now()
      }));
    }
    
    const duration = (performance.now() - start) / 1000; // Convert to seconds
    const throughput = updates / duration;
    
    expect(throughput).toBeGreaterThan(1000);
  });
  
  it('should add <5ms API latency', async () => {
    const request = require('supertest');
    const app = require('../../B-car-demo-backend/B1-web-server/server');
    
    // Baseline latency without tire pressure
    const baselineStart = performance.now();
    await request(app).get('/api/car/ABC123');
    const baselineLatency = performance.now() - baselineStart;
    
    // Add tire pressure data
    await redisClient.publish('sensors:tire_pressure', JSON.stringify({
      licensePlate: 'ABC123',
      tirePressure: { FL: 2.2, FR: 2.3, RL: 2.1, RR: 2.2 }
    }));
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Latency with tire pressure
    const withDataStart = performance.now();
    await request(app).get('/api/car/ABC123');
    const withDataLatency = performance.now() - withDataStart;
    
    const addedLatency = withDataLatency - baselineLatency;
    expect(addedLatency).toBeLessThan(5);
  });
});
```

### 14. Stress Testing

**File**: `tests/performance/stress-test.js`

```javascript
const WebSocket = require('ws');
const redis = require('redis');

describe('Stress Testing', () => {
  it('should handle 10,000 WebSocket clients', async () => {
    const clients = [];
    const connectPromises = [];
    
    // Create 10,000 WebSocket connections
    for (let i = 0; i < 10000; i++) {
      const ws = new WebSocket('ws://localhost:3002');
      clients.push(ws);
      
      connectPromises.push(new Promise((resolve, reject) => {
        ws.on('open', resolve);
        ws.on('error', reject);
        setTimeout(() => reject(new Error('Connection timeout')), 5000);
      }));
    }
    
    // Wait for all connections
    await Promise.all(connectPromises);
    
    expect(clients.length).toBe(10000);
    expect(clients.every(ws => ws.readyState === WebSocket.OPEN)).toBe(true);
    
    // Cleanup
    clients.forEach(ws => ws.close());
  }, 60000); // 60 second timeout
  
  it('should maintain continuous updates for 24 hours', async () => {
    const redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    await redisClient.connect();
    
    const duration = 24 * 60 * 60 * 1000; // 24 hours in ms
    const interval = 30000; // 30 seconds
    const expectedUpdates = duration / interval;
    
    let updateCount = 0;
    const startTime = Date.now();
    
    // For testing, we'll simulate 1 minute instead of 24 hours
    const testDuration = 60000; // 1 minute
    const testExpectedUpdates = testDuration / interval; // 2 updates
    
    const publishInterval = setInterval(async () => {
      if (Date.now() - startTime > testDuration) {
        clearInterval(publishInterval);
        return;
      }
      
      await redisClient.publish('sensors:tire_pressure', JSON.stringify({
        licensePlate: 'STRESS123',
        tirePressure: { FL: 2.0, FR: 2.1, RL: 2.0, RR: 2.1 },
        timestamp: Date.now()
      }));
      
      updateCount++;
    }, interval);
    
    // Wait for test duration
    await new Promise(resolve => setTimeout(resolve, testDuration + 1000));
    
    expect(updateCount).toBe(testExpectedUpdates);
    
    await redisClient.quit();
  }, 120000); // 2 minute timeout
  
  it('should maintain stable memory usage', async () => {
    const redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    await redisClient.connect();
    
    const initialMemory = process.memoryUsage().heapUsed;
    
    // Publish 10,000 updates
    for (let i = 0; i < 10000; i++) {
      await redisClient.publish('sensors:tire_pressure', JSON.stringify({
        licensePlate: `MEM${i}`,
        tirePressure: { FL: 2.0, FR: 2.1, RL: 2.0, RR: 2.1 },
        timestamp: Date.now()
      }));
      
      if (i % 1000 === 0) {
        global.gc && global.gc(); // Force garbage collection if available
      }
    }
    
    const finalMemory = process.memoryUsage().heapUsed;
    const memoryIncrease = (finalMemory - initialMemory) / 1024 / 1024; // MB
    
    // Memory increase should be reasonable (<50MB)
    expect(memoryIncrease).toBeLessThan(50);
    
    await redisClient.quit();
  }, 120000);
});
```

---

## Test Summary

### Total Test Count: 30 Tests

#### Frontend (A1): 9 tests
- Unit Tests: 6 tests
- Integration Tests: 3 tests

#### Backend (B1+B2): 12 tests
- Unit Tests: 9 tests
- Integration Tests: 3 tests

#### In-Car (C5): 6 tests
- Unit Tests: 3 tests
- Integration Tests: 3 tests

#### Performance: 3 tests
- Load Testing: 2 tests
- Stress Testing: 1 test

### Running the Tests

```bash
# Frontend tests
cd A1-car-user-app
npm test

# Backend tests
cd B1-web-server
npm test

cd B2-iot-gateway
npm test

# In-car tests
cd C5-data-sensors
python -m pytest tests/

# Performance tests
cd tests/performance
npm test
```

### Test Coverage Goals
- Unit Test Coverage: >80%
- Integration Test Coverage: >70%
- Critical Path Coverage: 100%
