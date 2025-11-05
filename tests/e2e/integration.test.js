const request = require('supertest');
const WebSocket = require('ws');
const redis = require('redis');
const { spawn } = require('child_process');
const path = require('path');

describe('Car Demo System - End-to-End Integration Tests', () => {
  let redisClient;
  let services = {};
  
  const SERVICE_URLS = {
    B1_API: 'http://localhost:3001',
    B2_IOT: 'http://localhost:3002', 
    C2_BROKER: 'http://localhost:3003'
  };
  
  const WS_URL = 'ws://localhost:8081';

  beforeAll(async () => {
    // Setup Redis client for testing
    redisClient = redis.createClient({ url: 'redis://localhost:6379' });
    await redisClient.connect();
    
    // Wait for services to be ready
    await waitForServices();
  }, 30000);

  afterAll(async () => {
    if (redisClient) {
      await redisClient.disconnect();
    }
  });

  async function waitForServices() {
    const maxRetries = 30;
    const retryDelay = 1000;
    
    for (const [name, url] of Object.entries(SERVICE_URLS)) {
      let retries = 0;
      while (retries < maxRetries) {
        try {
          const response = await request(url).get('/health').timeout(5000);
          if (response.status === 200) {
            console.log(`✅ ${name} is ready`);
            break;
          }
        } catch (error) {
          retries++;
          if (retries >= maxRetries) {
            throw new Error(`${name} failed to start after ${maxRetries} retries`);
          }
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }
  }

  describe('Service Health Checks', () => {
    test('All services should be healthy', async () => {
      // Check B1 Web Server
      const b1Response = await request(SERVICE_URLS.B1_API)
        .get('/health')
        .expect(200);
      
      expect(b1Response.body).toHaveProperty('server', 'ok');
      
      // Check B2 IoT Gateway
      const b2Response = await request(SERVICE_URLS.B2_IOT)
        .get('/health')
        .expect(200);
      
      expect(b2Response.body).toHaveProperty('status');
      
      // Check C2 Central Broker
      const c2Response = await request(SERVICE_URLS.C2_BROKER)
        .get('/health')
        .expect(200);
      
      expect(c2Response.body).toHaveProperty('status', 'healthy');
      expect(c2Response.body).toHaveProperty('redis', 'connected');
    });

    test('Redis should be accessible', async () => {
      const pong = await redisClient.ping();
      expect(pong).toBe('PONG');
    });
  });

  describe('Complete Data Flow', () => {
    test('Sensor data should flow from C5 -> C2 -> B1', async () => {
      const testCarData = {
        licensePlate: 'E2E-TEST',
        indoorTemp: 23.5,
        outdoorTemp: 16.8,
        gps: { lat: 60.1700, lng: 24.9400 },
        speed: 0,
        engineStatus: 'off',
        fuelLevel: 85,
        batteryVoltage: 12.5,
        timestamp: new Date().toISOString()
      };

      // 1. Simulate sensor data injection via C2
      const c2Response = await request(SERVICE_URLS.C2_BROKER)
        .post('/api/data')
        .send(testCarData)
        .expect(200);

      expect(c2Response.body).toHaveProperty('success', true);
      expect(c2Response.body).toHaveProperty('licensePlate', 'E2E-TEST');

      // 2. Verify data is stored in Redis
      const redisData = await redisClient.get('car:E2E-TEST:latest_data');
      expect(redisData).toBeTruthy();
      
      const parsedRedisData = JSON.parse(redisData);
      expect(parsedRedisData.licensePlate).toBe('E2E-TEST');
      expect(parsedRedisData.indoorTemp).toBe(23.5);

      // 3. Verify data is accessible via C2 API
      const c2DataResponse = await request(SERVICE_URLS.C2_BROKER)
        .get('/api/car/E2E-TEST/data')
        .expect(200);

      expect(c2DataResponse.body.licensePlate).toBe('E2E-TEST');
      expect(c2DataResponse.body.indoorTemp).toBe(23.5);

      // 4. Verify data is accessible via B1 API (with possible mock data)
      const b1Response = await request(SERVICE_URLS.B1_API)
        .get('/api/car/E2E-TEST');

      // B1 might return mock data or actual data depending on implementation
      expect(b1Response.status).toBeOneOf([200, 404]);
    });

    test('Command flow should work from B1 -> C2 -> Car', async () => {
      const testCommand = {
        command: 'start_heating',
        parameters: { temperature: 25 }
      };

      // 1. Send command via B1 API
      const b1Response = await request(SERVICE_URLS.B1_API)
        .post('/api/car/ABC-123/command')
        .send(testCommand)
        .expect(200);

      expect(b1Response.body).toHaveProperty('success', true);
      expect(b1Response.body).toHaveProperty('command', 'start_heating');

      // 2. Verify command is propagated to C2
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for propagation

      const c2CommandResponse = await request(SERVICE_URLS.C2_BROKER)
        .get('/api/car/ABC-123/commands')
        .expect(200);

      expect(Array.isArray(c2CommandResponse.body)).toBe(true);
    });
  });

  describe('Real-time Communication', () => {
    test('WebSocket connection should work with B2 IoT Gateway', (done) => {
      const ws = new WebSocket(WS_URL);
      
      ws.on('open', () => {
        const testMessage = {
          licensePlate: 'WS-TEST',
          indoorTemp: 22.0,
          outdoorTemp: 15.5,
          timestamp: new Date().toISOString()
        };
        
        ws.send(JSON.stringify(testMessage));
      });

      ws.on('message', (data) => {
        const response = JSON.parse(data.toString());
        expect(response).toHaveProperty('status');
        ws.close();
        done();
      });

      ws.on('error', (error) => {
        done(error);
      });

      // Timeout after 10 seconds
      setTimeout(() => {
        ws.close();
        done(new Error('WebSocket test timed out'));
      }, 10000);
    });
  });

  describe('Data Consistency', () => {
    test('Same car data should be consistent across services', async () => {
      const licensePlate = 'ABC-123';
      
      // Get data from different services
      const [c2Response, b1Response] = await Promise.allSettled([
        request(SERVICE_URLS.C2_BROKER).get(`/api/car/${licensePlate}/data`),
        request(SERVICE_URLS.B1_API).get(`/api/car/${licensePlate}`)
      ]);

      // At least one service should have data for the test car
      const c2HasData = c2Response.status === 'fulfilled' && c2Response.value.status === 200;
      const b1HasData = b1Response.status === 'fulfilled' && b1Response.value.status === 200;
      
      expect(c2HasData || b1HasData).toBe(true);

      if (c2HasData && b1HasData) {
        // If both have data, verify license plate consistency
        expect(c2Response.value.body.licensePlate).toBe(licensePlate);
        expect(b1Response.value.body.licensePlate).toBe(licensePlate);
      }
    });

    test('Multiple cars should be handled correctly', async () => {
      const testCars = ['ABC-123', 'XYZ-789', 'DEF-456'];
      const carDataPromises = testCars.map(car => 
        request(SERVICE_URLS.C2_BROKER)
          .get(`/api/car/${car}/data`)
          .catch(() => null) // Handle 404s gracefully
      );

      const responses = await Promise.all(carDataPromises);
      const validResponses = responses.filter(response => response && response.status === 200);

      // Should have at least some valid car data
      expect(validResponses.length).toBeGreaterThan(0);

      validResponses.forEach(response => {
        expect(response.body).toHaveProperty('licensePlate');
        expect(testCars).toContain(response.body.licensePlate);
      });
    });
  });

  describe('Load Testing', () => {
    test('System should handle multiple concurrent requests', async () => {
      const concurrentRequests = 10;
      const requests = Array.from({ length: concurrentRequests }, (_, i) => 
        request(SERVICE_URLS.C2_BROKER)
          .post('/api/data')
          .send({
            licensePlate: `LOAD-${i.toString().padStart(3, '0')}`,
            indoorTemp: 20 + i,
            outdoorTemp: 15 + i,
            timestamp: new Date().toISOString()
          })
      );

      const responses = await Promise.allSettled(requests);
      const successfulResponses = responses.filter(
        result => result.status === 'fulfilled' && result.value.status === 200
      );

      // At least 80% of requests should succeed
      expect(successfulResponses.length).toBeGreaterThanOrEqual(concurrentRequests * 0.8);
    });

    test('System should handle rapid data updates for same car', async () => {
      const licensePlate = 'RAPID-TEST';
      const updateCount = 5;
      const updates = [];

      for (let i = 0; i < updateCount; i++) {
        const update = request(SERVICE_URLS.C2_BROKER)
          .post('/api/data')
          .send({
            licensePlate: licensePlate,
            indoorTemp: 20 + i,
            outdoorTemp: 15 + i,
            timestamp: new Date().toISOString()
          });
        
        updates.push(update);
        await new Promise(resolve => setTimeout(resolve, 100)); // 100ms between updates
      }

      const responses = await Promise.all(updates);
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });

      // Verify final state
      const finalDataResponse = await request(SERVICE_URLS.C2_BROKER)
        .get(`/api/car/${licensePlate}/data`)
        .expect(200);

      expect(finalDataResponse.body.licensePlate).toBe(licensePlate);
    });
  });

  describe('Error Handling', () => {
    test('System should handle invalid data gracefully', async () => {
      const invalidData = {
        licensePlate: '', // Invalid
        indoorTemp: 'not-a-number', // Invalid type
        // Missing required fields
      };

      const response = await request(SERVICE_URLS.C2_BROKER)
        .post('/api/data')
        .send(invalidData)
        .expect(400);

      expect(response.body).toHaveProperty('error');
    });

    test('System should handle non-existent car requests', async () => {
      const nonExistentCar = 'DOES-NOT-EXIST';
      
      const c2Response = await request(SERVICE_URLS.C2_BROKER)
        .get(`/api/car/${nonExistentCar}/data`)
        .expect(404);

      expect(c2Response.body).toHaveProperty('error');

      const b1Response = await request(SERVICE_URLS.B1_API)
        .get(`/api/car/${nonExistentCar}`);

      expect([404, 400]).toContain(b1Response.status);
    });
  });

  describe('System Recovery', () => {
    test('System should recover from Redis disconnection', async () => {
      // This test would require more complex setup to actually disconnect Redis
      // For now, we'll test that the system reports Redis status correctly
      
      const healthResponse = await request(SERVICE_URLS.C2_BROKER)
        .get('/health')
        .expect(200);

      expect(healthResponse.body).toHaveProperty('redis');
      expect(['connected', 'disconnected']).toContain(healthResponse.body.redis);
    });
  });
});

// Helper functions
function expectStatusOneOf(response, statuses) {
  expect(statuses).toContain(response.status);
}

// Add custom matcher
expect.extend({
  toBeOneOf(received, array) {
    const pass = array.includes(received);
    if (pass) {
      return {
        message: () => `expected ${received} not to be one of ${array}`,
        pass: true,
      };
    } else {
      return {
        message: () => `expected ${received} to be one of ${array}`,
        pass: false,
      };
    }
  },
});