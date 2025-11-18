# 🧪 Car Demo System - Testing Guide

## Overview

This document provides comprehensive testing strategies for the Car Demo System, including unit tests, integration tests, and end-to-end tests.

## Test Structure

```
car-demo-system/
├── car-demo-backend/
│   ├── B1-web-server/tests/     # B1 API unit tests
│   ├── B2-iot-gateway/tests/    # B2 IoT unit tests
│   └── package.json             # Test scripts
├── car-demo-in-car/
│   ├── C1-cloud-communication/tests/  # Python unit tests
│   ├── C2-central-broker/tests/       # C2 Redis unit tests
│   └── C5-data-sensors/tests/         # Sensor unit tests
├── tests/
│   ├── e2e/                     # End-to-end integration tests
│   └── setup.js                 # Global test setup
└── run-tests.sh                 # Test runner script
```

## 🚀 Quick Start

### Run All Tests
```bash
# Navigate to your project directory
./run-tests.sh --all
```

### Run Specific Test Types
```bash
# Unit tests only
./run-tests.sh --unit

# End-to-end tests only  
./run-tests.sh --e2e

# With coverage
./run-tests.sh --unit --coverage

# Watch mode for development
./run-tests.sh --unit --watch
```

### Run Component-Specific Tests
```bash
# B1 Web Server tests
./run-tests.sh --component b1

# B2 IoT Gateway tests
./run-tests.sh --component b2

# C2 Central Broker tests
./run-tests.sh --component c2
```

## 📋 Test Categories

### 1. Unit Tests

#### **B1 Web Server Tests** (`B1-web-server/tests/`)
```bash
npm run test:b1
```

**Coverage:**
- ✅ REST API endpoints (`/api/car/*`, `/health`)
- ✅ Database connection handling (MongoDB, PostgreSQL, Redis)
- ✅ Request validation and error handling
- ✅ CORS and security headers
- ✅ Car command processing
- ✅ Input sanitization (SQL injection prevention)

**Key Test Cases:**
- Health endpoint returns proper status
- Car data retrieval with valid/invalid license plates
- Command validation (start_heating, start_cooling, etc.)
- Error handling for database failures
- Request input validation

#### **B2 IoT Gateway Tests** (`B2-iot-gateway/tests/`)
```bash
npm run test:b2
```

**Coverage:**
- ✅ WebSocket connection handling
- ✅ MQTT message processing
- ✅ Sensor data validation
- ✅ Real-time data processing
- ✅ Error handling and reconnection logic
- ✅ Data format conversion

**Key Test Cases:**
- WebSocket message processing
- MQTT publish/subscribe functionality
- Sensor data validation (temperature, GPS, fuel)
- Invalid data handling
- Connection error recovery

#### **C2 Central Broker Tests** (`C2-central-broker/tests/`)
```bash
cd car-demo-system/car-demo-in-car/C2-central-broker
npm test
```

**Coverage:**
- ✅ Redis operations (get, set, publish, subscribe)
- ✅ REST API endpoints
- ✅ Real-time data broadcasting
- ✅ Command queuing and processing
- ✅ Data persistence and retrieval
- ✅ Error handling

**Key Test Cases:**
- Car data storage and retrieval
- Command processing and history
- Real-time WebSocket broadcasting
- Redis connection handling
- API request validation

#### **Python Component Tests** (`C1/C5 tests/`)
```bash
# From virtual environment
source car-demo-venv/bin/activate

# C1 Cloud Communication tests
cd car-demo-system/car-demo-in-car/C1-cloud-communication
python -m pytest tests/ -v

# C5 Sensor Simulator tests  
cd ../C5-data-sensors
python -m pytest tests/ -v
```

**Coverage:**
- ✅ Sensor data generation and validation
- ✅ Redis async operations
- ✅ Cloud communication protocols
- ✅ Data serialization/deserialization
- ✅ Error handling and retry logic
- ✅ Concurrent data processing

### 2. Integration Tests

#### **End-to-End Tests** (`tests/e2e/`)
```bash
./run-tests.sh --e2e
```

**Prerequisites:** All services must be running
- B1 Web Server (port 3001)
- B2 IoT Gateway (port 3002)
- C2 Central Broker (port 3003)
- Redis (port 6379)

**Coverage:**
- ✅ Complete data flow (Sensor → C2 → B1)
- ✅ Command flow (B1 → C2 → Car)
- ✅ Real-time WebSocket communication
- ✅ Multi-service data consistency
- ✅ Load testing (concurrent requests)
- ✅ System recovery and error handling

**Key Test Scenarios:**
- Full sensor data pipeline
- Command execution flow
- Real-time data updates
- Multiple car handling
- System resilience testing

## 🛠️ Test Infrastructure

### Dependencies

**Node.js Testing:**
- `jest` - Test framework
- `supertest` - HTTP testing
- `mongodb-memory-server` - In-memory MongoDB
- `ws` - WebSocket testing

**Python Testing:**
- `pytest` - Test framework
- `pytest-asyncio` - Async testing
- `pytest-mock` - Mocking
- `fakeredis` - Redis mocking

### Test Configuration

**Jest Configuration** (`package.json`):
```json
{
  "jest": {
    "testEnvironment": "node",
    "testTimeout": 30000,
    "setupFilesAfterEnv": ["<rootDir>/tests/setup.js"],
    "collectCoverageFrom": ["**/*.js", "!**/node_modules/**", "!**/tests/**"],
    "coverageThreshold": {
      "global": {
        "branches": 70,
        "functions": 70,
        "lines": 70,
        "statements": 70
      }
    }
  }
}
```

### Custom Test Utilities

**Global Test Helpers** (`tests/setup.js`):
```javascript
// Custom matchers
expect(timestamp).toBeValidTimestamp();
expect(licensePlate).toBeValidLicensePlate();
expect(temperature).toBeWithinTemperatureRange();

// Test data generators
global.testUtils.generateCarData('ABC-123');
global.testUtils.generateMultipleCarData(5);
global.testUtils.generateLicensePlate();
```

## 📊 Coverage Reports

### Generate Coverage
```bash
./run-tests.sh --unit --coverage
```

**Coverage Targets:**
- **Branches:** 70%
- **Functions:** 70%
- **Lines:** 70%
- **Statements:** 70%

**Coverage Reports Generated:**
- `coverage/lcov-report/index.html` - HTML report
- `coverage/lcov.info` - LCOV format
- `coverage/clover.xml` - Clover format

## 🔧 Development Workflow

### Test-Driven Development
```bash
# 1. Write failing test
# 2. Run tests to see failure
./run-tests.sh --component b1 --watch

# 3. Implement feature
# 4. Run tests to see success
# 5. Refactor and repeat
```

### Continuous Testing
```bash
# Watch mode for active development
./run-tests.sh --unit --watch

# Run tests on file changes
npm run test:watch
```

### Pre-commit Testing
```bash
# Run all tests before committing
./run-tests.sh --unit

# Quick smoke test
npm run test:coverage
```

## 🐛 Debugging Tests

### Common Issues

**1. Service Connection Errors**
```bash
# Check if services are running
curl http://localhost:3001/health
curl http://localhost:3003/health
redis-cli ping
```

**2. Database Connection Issues**
```bash
# Restart Redis
redis-server --daemonize yes

# Check MongoDB memory server
# (automatically handled in tests)
```

**3. Port Conflicts**
```bash
# Check what's using ports
lsof -i :3001
lsof -i :3003
lsof -i :8081
```

### Test Debugging
```bash
# Run single test file
npx jest B1-web-server/tests/server.test.js

# Run with debug output
DEBUG=* npm test

# Run specific test case
npx jest --testNamePattern="should handle car data"
```

## 📈 Performance Testing

### Load Testing
```bash
# Run load tests (part of E2E suite)
./run-tests.sh --e2e

# Manual load testing
for i in {1..100}; do
  curl -X POST http://localhost:3003/api/data \
    -H "Content-Type: application/json" \
    -d '{"licensePlate":"LOAD-'$i'","indoorTemp":22}' &
done
```

### Memory Testing
```bash
# Run tests with memory monitoring
node --inspect --max-old-space-size=512 ./node_modules/.bin/jest
```

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: npm install
      - run: ./run-tests.sh --unit --coverage
      - uses: codecov/codecov-action@v1
```

### Test Scripts for CI
```bash
# Automated testing (no interactive prompts)
export CI=true
./run-tests.sh --unit --coverage
```

## 📚 Best Practices

### Test Organization
- **Unit tests:** Test individual functions/modules
- **Integration tests:** Test service interactions
- **E2E tests:** Test complete user workflows

### Test Data
- Use realistic test data (valid license plates, GPS coordinates)
- Avoid hardcoded values in tests
- Use test data generators

### Mocking Strategy
- Mock external dependencies (databases, APIs)
- Use in-memory databases for integration tests
- Mock time-dependent functionality

### Assertions
- Use descriptive test names
- Test both positive and negative cases
- Verify error messages and status codes

## 🔍 Monitoring and Metrics

### Test Metrics to Track
- Test execution time
- Coverage percentage
- Test failure rate
- Flaky test identification

### Performance Metrics
- API response times
- WebSocket connection latency
- Database query performance
- Memory usage during tests

---

## 🎯 Getting Started Checklist

- [ ] Install dependencies: `npm install` and `pip install pytest`
- [ ] Start Redis: `redis-server --daemonize yes`
- [ ] Run unit tests: `./run-tests.sh --unit`
- [ ] Generate coverage: `./run-tests.sh --unit --coverage`
- [ ] Start services for E2E tests
- [ ] Run E2E tests: `./run-tests.sh --e2e`
- [ ] Review coverage report in `coverage/lcov-report/index.html`

**Happy Testing! 🚀**