# Developer Scenario: Implementing Agent C5 - Tire Pressure Sensors

## Scenario Overview

**Feature Request**: "Add tire pressure monitoring to the car dashboard"

**Your Role**: Sensor Systems Developer (Agent C5)

**Goal**: Implement tire pressure sensors that generate realistic data and send it directly to the backend API.

---

## Agent C5 Architecture

```
[C5 - Tire Pressure Sensors] --> Backend B1 API (http://localhost:3001/api/monitoring/tire-pressure)
```

**Focus**: Direct sensor-to-cloud communication for tire pressure monitoring

---

## Step 1: Set Up Development Environment

### Prerequisites

```bash
# Navigate to sensor directory
cd C-car-demo-in-car/C5-data-sensors

# Install Python dependencies
pip install -r requirements.txt

# Verify dependencies
python -c "import requests, time, random; print('Dependencies OK')"
```

### Project Structure

```
C5-data-sensors/
|-- tire_pressure_sensor.py     # Main sensor implementation
|-- sensor_config.py            # Configuration settings
|-- test_sensors.py             # Unit tests
`-- requirements.txt             # Python dependencies
```

---

## Step 2: Implement Tire Pressure Sensor

### Core Sensor Class

Create `tire_pressure_sensor.py`:

```python
import time
import random
import requests
import json
import threading
from datetime import datetime
from typing import Dict, List

class TirePressureSensor:
    """
    Simulates tire pressure sensors for a vehicle.
    Generates realistic pressure readings and sends to backend API.
    """
    
    def __init__(self, car_id: str, backend_url: str = "http://localhost:3001"):
        self.car_id = car_id
        self.backend_url = backend_url
        self.api_endpoint = f"{backend_url}/api/monitoring/tire-pressure"
        self.running = False
        
        # Realistic tire pressure parameters
        self.normal_pressure = 2.2  # bar (32 PSI)
        self.min_pressure = 1.8     # bar (26 PSI) - low warning
        self.max_pressure = 2.6     # bar (38 PSI) - high warning
        
        # Current pressure state for each tire
        self.current_pressures = {
            'frontLeft': self.normal_pressure,
            'frontRight': self.normal_pressure,
            'rearLeft': self.normal_pressure,
            'rearRight': self.normal_pressure
        }
        
        # Simulation parameters
        self.drift_rate = 0.001     # Pressure drift per reading
        self.noise_amplitude = 0.02 # Random noise amplitude
        
    def simulate_pressure_changes(self):
        """Simulate realistic tire pressure changes over time"""
        for tire in self.current_pressures:
            # Natural pressure drift (usually slight decrease)
            drift = random.uniform(-self.drift_rate, self.drift_rate * 0.3)
            
            # Random noise from road conditions, temperature, etc.
            noise = random.uniform(-self.noise_amplitude, self.noise_amplitude)
            
            # Apply changes
            new_pressure = self.current_pressures[tire] + drift + noise
            
            # Keep within realistic bounds
            new_pressure = max(self.min_pressure * 0.8, new_pressure)
            new_pressure = min(self.max_pressure * 1.2, new_pressure)
            
            self.current_pressures[tire] = round(new_pressure, 2)
    
    def get_tire_pressure_reading(self) -> Dict:
        """Generate current tire pressure reading"""
        self.simulate_pressure_changes()
        
        return {
            'carId': self.car_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'pressures': self.current_pressures.copy(),
            'unit': 'bar',
            'sensor_health': 'normal',
            'temperature': round(random.uniform(18, 25), 1)  # Tire temperature in C
        }
    
    def send_to_backend(self, data: Dict) -> bool:
        """Send tire pressure data to backend API"""
        try:
            response = requests.post(
                self.api_endpoint,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"[{self.car_id}] [OK] Data sent: {data['pressures']}")
                return True
            else:
                print(f"[{self.car_id}] [ERROR] API error {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"[{self.car_id}] [ERROR] Connection failed - backend not available")
            return False
        except requests.exceptions.Timeout:
            print(f"[{self.car_id}] [ERROR] Request timeout")
            return False
        except Exception as e:
            print(f"[{self.car_id}] [ERROR] Unexpected error: {e}")
            return False
    
    def start_monitoring(self, interval: int = 10):
        """Start continuous tire pressure monitoring"""
        self.running = True
        print(f"[{self.car_id}] Starting tire pressure monitoring (interval: {interval}s)")
        
        while self.running:
            try:
                # Get current reading
                reading = self.get_tire_pressure_reading()
                
                # Send to backend
                self.send_to_backend(reading)
                
                # Wait for next reading
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"[{self.car_id}] Monitoring stopped by user")
                break
            except Exception as e:
                print(f"[{self.car_id}] Error in monitoring loop: {e}")
                time.sleep(1)
        
        self.running = False
    
    def stop_monitoring(self):
        """Stop tire pressure monitoring"""
        self.running = False
    
    def simulate_pressure_loss(self, tire: str, target_pressure: float):
        """Simulate gradual pressure loss in a specific tire"""
        if tire not in self.current_pressures:
            print(f"Invalid tire: {tire}")
            return
        
        current = self.current_pressures[tire]
        print(f"[{self.car_id}] Simulating pressure loss in {tire}: {current} -> {target_pressure} bar")
        
        # Gradual pressure loss over 30 seconds
        steps = 30
        pressure_drop = (current - target_pressure) / steps
        
        for i in range(steps):
            if not self.running:
                break
            self.current_pressures[tire] -= pressure_drop
            time.sleep(1)
        
        self.current_pressures[tire] = target_pressure
        print(f"[{self.car_id}] Pressure loss simulation complete for {tire}")

class MultiCarSensorSystem:
    """Manage tire pressure sensors for multiple vehicles"""
    
    def __init__(self, car_ids: List[str], backend_url: str = "http://localhost:3001"):
        self.sensors = {}
        self.threads = {}
        
        for car_id in car_ids:
            self.sensors[car_id] = TirePressureSensor(car_id, backend_url)
    
    def start_all_sensors(self, interval: int = 10):
        """Start monitoring for all vehicles"""
        print(f"Starting tire pressure monitoring for {len(self.sensors)} vehicles")
        
        for car_id, sensor in self.sensors.items():
            thread = threading.Thread(
                target=sensor.start_monitoring,
                args=(interval,),
                daemon=True
            )
            thread.start()
            self.threads[car_id] = thread
            time.sleep(0.5)  # Stagger startup
    
    def stop_all_sensors(self):
        """Stop monitoring for all vehicles"""
        print("Stopping all tire pressure sensors...")
        
        for sensor in self.sensors.values():
            sensor.stop_monitoring()
        
        for thread in self.threads.values():
            thread.join(timeout=2)
    
    def simulate_incident(self, car_id: str, tire: str, pressure: float):
        """Simulate tire pressure incident for specific vehicle"""
        if car_id in self.sensors:
            sensor = self.sensors[car_id]
            incident_thread = threading.Thread(
                target=sensor.simulate_pressure_loss,
                args=(tire, pressure),
                daemon=True
            )
            incident_thread.start()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Tire Pressure Sensor Simulator')
    parser.add_argument('--cars', nargs='+', default=['CAR001', 'CAR002', 'CAR003'],
                        help='Car IDs to simulate')
    parser.add_argument('--interval', type=int, default=10,
                        help='Reading interval in seconds')
    parser.add_argument('--backend-url', default='http://localhost:3001',
                        help='Backend API URL')
    
    args = parser.parse_args()
    
    # Create multi-car sensor system
    system = MultiCarSensorSystem(args.cars, args.backend_url)
    
    try:
        # Start all sensors
        system.start_all_sensors(args.interval)
        
        print("\nTire pressure monitoring active. Commands:")
        print("  'incident <car_id> <tire> <pressure>' - Simulate pressure loss")
        print("  'quit' - Stop monitoring")
        print("\nExample: incident CAR001 frontLeft 1.5")
        
        # Interactive command loop
        while True:
            try:
                cmd = input("\n> ").strip()
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    break
                elif cmd.startswith('incident'):
                    parts = cmd.split()
                    if len(parts) == 4:
                        _, car_id, tire, pressure = parts
                        pressure = float(pressure)
                        system.simulate_incident(car_id, tire, pressure)
                    else:
                        print("Usage: incident <car_id> <tire> <pressure>")
                elif cmd:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    finally:
        system.stop_all_sensors()
        print("Tire pressure monitoring stopped")
```

### Configuration Management

Create `sensor_config.py`:

```python
import os
from typing import Dict, List

class SensorConfig:
    """Configuration management for tire pressure sensors"""
    
    def __init__(self):
        # Backend configuration
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:3001')
        self.api_timeout = int(os.getenv('API_TIMEOUT', '5'))
        
        # Sensor configuration
        self.reading_interval = int(os.getenv('READING_INTERVAL', '10'))
        self.normal_pressure = float(os.getenv('NORMAL_PRESSURE', '2.2'))
        
        # Car configuration
        self.default_cars = ['CAR001', 'CAR002', 'CAR003']
        cars_env = os.getenv('CARS', '')
        self.cars = cars_env.split(',') if cars_env else self.default_cars
        
        # Simulation parameters
        self.drift_rate = float(os.getenv('DRIFT_RATE', '0.001'))
        self.noise_amplitude = float(os.getenv('NOISE_AMPLITUDE', '0.02'))
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def get_pressure_thresholds(self) -> Dict[str, float]:
        """Get pressure warning thresholds"""
        return {
            'low_warning': self.normal_pressure * 0.85,
            'low_critical': self.normal_pressure * 0.75,
            'high_warning': self.normal_pressure * 1.15,
            'high_critical': self.normal_pressure * 1.25
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        if self.reading_interval < 1:
            errors.append("Reading interval must be at least 1 second")
        
        if self.normal_pressure < 1.0 or self.normal_pressure > 4.0:
            errors.append("Normal pressure must be between 1.0 and 4.0 bar")
        
        if not self.cars:
            errors.append("At least one car ID must be specified")
        
        return errors
```

---

## Step 3: Testing Framework

### Unit Tests

Create `test_sensors.py`:

```python
import unittest
import json
from unittest.mock import Mock, patch
from tire_pressure_sensor import TirePressureSensor, MultiCarSensorSystem

class TestTirePressureSensor(unittest.TestCase):
    
    def setUp(self):
        self.sensor = TirePressureSensor('TEST001', 'http://localhost:3001')
    
    def test_initial_pressures(self):
        """Test that sensor initializes with normal pressures"""
        for tire, pressure in self.sensor.current_pressures.items():
            self.assertEqual(pressure, 2.2)
    
    def test_pressure_reading_format(self):
        """Test that pressure reading has correct format"""
        reading = self.sensor.get_tire_pressure_reading()
        
        self.assertIn('carId', reading)
        self.assertIn('timestamp', reading)
        self.assertIn('pressures', reading)
        self.assertIn('unit', reading)
        
        self.assertEqual(reading['carId'], 'TEST001')
        self.assertEqual(reading['unit'], 'bar')
        
        # Check all tires are present
        required_tires = ['frontLeft', 'frontRight', 'rearLeft', 'rearRight']
        for tire in required_tires:
            self.assertIn(tire, reading['pressures'])
    
    def test_pressure_simulation(self):
        """Test that pressure changes over time"""
        initial_pressures = self.sensor.current_pressures.copy()
        
        # Simulate multiple readings
        for _ in range(100):
            self.sensor.simulate_pressure_changes()
        
        # At least one tire should have changed
        changed = False
        for tire in initial_pressures:
            if abs(initial_pressures[tire] - self.sensor.current_pressures[tire]) > 0.01:
                changed = True
                break
        
        self.assertTrue(changed, "Pressures should change over time")
    
    @patch('requests.post')
    def test_successful_api_call(self, mock_post):
        """Test successful API communication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        reading = self.sensor.get_tire_pressure_reading()
        result = self.sensor.send_to_backend(reading)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_failed_api_call(self, mock_post):
        """Test failed API communication"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        reading = self.sensor.get_tire_pressure_reading()
        result = self.sensor.send_to_backend(reading)
        
        self.assertFalse(result)
    
    def test_pressure_loss_simulation(self):
        """Test tire pressure loss simulation"""
        original_pressure = self.sensor.current_pressures['frontLeft']
        target_pressure = 1.5
        
        # Mock the time.sleep to speed up test
        with patch('time.sleep'):
            self.sensor.simulate_pressure_loss('frontLeft', target_pressure)
        
        self.assertAlmostEqual(
            self.sensor.current_pressures['frontLeft'], 
            target_pressure, 
            places=1
        )

class TestMultiCarSensorSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = MultiCarSensorSystem(['CAR001', 'CAR002'])
    
    def test_sensor_creation(self):
        """Test that sensors are created for all cars"""
        self.assertEqual(len(self.system.sensors), 2)
        self.assertIn('CAR001', self.system.sensors)
        self.assertIn('CAR002', self.system.sensors)

if __name__ == '__main__':
    unittest.main()
```

---

## Step 4: Development Workflow

### Quick Start

```bash
# Start tire pressure sensors for default cars
python tire_pressure_sensor.py

# Start with custom cars
python tire_pressure_sensor.py --cars CAR001 CAR002 --interval 5

# Start with different backend
python tire_pressure_sensor.py --backend-url http://staging.example.com
```

### Environment Configuration

Create `.env` file:

```bash
# Backend configuration
BACKEND_URL=http://localhost:3001
API_TIMEOUT=5

# Sensor configuration
READING_INTERVAL=10
NORMAL_PRESSURE=2.2

# Simulation parameters
CARS=CAR001,CAR002,CAR003
DRIFT_RATE=0.001
NOISE_AMPLITUDE=0.02

# Logging
LOG_LEVEL=INFO
```

### Testing Commands

```bash
# Run unit tests
python -m pytest test_sensors.py -v

# Test single sensor
python -c "
from tire_pressure_sensor import TirePressureSensor
sensor = TirePressureSensor('TEST001')
reading = sensor.get_tire_pressure_reading()
print(reading)
"

# Test API connectivity
curl -X POST http://localhost:3001/api/monitoring/tire-pressure \
  -H "Content-Type: application/json" \
  -d '{"carId":"TEST","timestamp":"2025-11-28T10:00:00Z","pressures":{"frontLeft":2.2,"frontRight":2.2,"rearLeft":2.2,"rearRight":2.2},"unit":"bar"}'
```

---

## Step 5: Production Deployment

### Docker Configuration

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY *.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash sensor
USER sensor

# Set default environment
ENV BACKEND_URL=http://backend:3001
ENV CARS=CAR001,CAR002,CAR003
ENV READING_INTERVAL=10

CMD ["python", "tire_pressure_sensor.py"]
```

### Docker Compose Integration

```yaml
version: '3.8'
services:
  tire-pressure-sensors:
    build: .
    environment:
      - BACKEND_URL=http://backend:3001
      - CARS=CAR001,CAR002,CAR003
      - READING_INTERVAL=10
      - NORMAL_PRESSURE=2.2
    depends_on:
      - backend
    networks:
      - car_network
    restart: unless-stopped

networks:
  car_network:
    external: true
```

---

## Step 6: Monitoring and Debugging

### Logging Enhancement

Add to `tire_pressure_sensor.py`:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TirePressureSensor:
    def __init__(self, car_id: str, backend_url: str = "http://localhost:3001"):
        # ... existing init code ...
        logger.info(f"Initialized tire pressure sensor for {car_id}")
    
    def send_to_backend(self, data: Dict) -> bool:
        """Send tire pressure data with detailed logging"""
        try:
            logger.debug(f"[{self.car_id}] Sending data: {data}")
            response = requests.post(self.api_endpoint, json=data, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"[{self.car_id}] Successfully sent pressure data")
                return True
            else:
                logger.error(f"[{self.car_id}] API error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"[{self.car_id}] Failed to send data: {e}")
            return False
```

### Health Check Endpoint

Create `health_check.py`:

```python
import requests
import json
from tire_pressure_sensor import TirePressureSensor

def check_sensor_health(car_id: str, backend_url: str) -> Dict:
    """Check sensor and backend connectivity"""
    sensor = TirePressureSensor(car_id, backend_url)
    
    health_status = {
        'car_id': car_id,
        'sensor_status': 'ok',
        'backend_connectivity': False,
        'last_reading': None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Test sensor reading
        reading = sensor.get_tire_pressure_reading()
        health_status['last_reading'] = reading
        
        # Test backend connectivity
        test_data = {'carId': f"{car_id}_healthcheck", 'test': True}
        response = requests.get(f"{backend_url}/health", timeout=5)
        health_status['backend_connectivity'] = response.status_code == 200
        
    except Exception as e:
        health_status['sensor_status'] = f'error: {e}'
    
    return health_status

if __name__ == "__main__":
    cars = ['CAR001', 'CAR002', 'CAR003']
    backend_url = 'http://localhost:3001'
    
    for car_id in cars:
        status = check_sensor_health(car_id, backend_url)
        print(json.dumps(status, indent=2))
```

---

## Suggested Subtasks

1. **Basic Sensor Implementation** (2 hours)
   - Implement TirePressureSensor class
   - Add realistic pressure simulation
   - Test data generation and formatting

2. **API Integration** (1.5 hours)
   - Implement HTTP client for backend communication
   - Add error handling and retries
   - Test with B1 monitoring endpoints

3. **Multi-Car Support** (1 hour)
   - Implement MultiCarSensorSystem class
   - Add threading for parallel monitoring
   - Test multiple vehicle simulation

4. **Interactive Features** (1 hour)
   - Add pressure loss simulation
   - Implement command interface
   - Add real-time monitoring display

5. **Testing and Validation** (1 hour)
   - Write unit tests for sensor logic
   - Create integration tests with backend
   - Add health check functionality

6. **Production Deployment** (1 hour)
   - Create Docker configuration
   - Add environment variable support
   - Configure logging and monitoring

---

## Notes

- **Direct Communication**: C5 sends data directly to B1 API, bypassing C2 broker for simplicity
- **Realistic Simulation**: Pressure values drift naturally and respond to simulated incidents
- **Production Ready**: Includes error handling, logging, health checks, and Docker deployment
- **NO dependencies**: Can be developed and tested independently using B1 mock endpoints
- **Scalable**: Easy to add more cars or sensor types

**Total Estimated Effort**: 6-8 hours for complete implementation