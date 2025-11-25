# Developer Scenario: Getting A1 Requirements from Agent Analysis

## Scenario Overview

**Feature Request**: "Add real-time tire pressure monitoring to the mobile app"

**Your Role**: Mobile Developer (A1 - Car User Mobile App)

**Goal**: Understand what UI screens, API calls, and user interactions you need to implement in the React Native mobile app.

---

## Step 1: Run Jenkins Pipeline

### Trigger the AI Analysis

```bash
# Jenkins Pipeline Parameters:
FEATURE_REQUEST: "Add real-time tire pressure monitoring to the mobile app"
USE_AI_AGENTS: true
OLLAMA_MODEL: llama3:8b
OUTPUT_FILE: tire-pressure-monitoring-analysis.md
```

### What Happens Behind the Scenes

```
User Request: "Add real-time tire pressure monitoring to mobile app"
     |
     v
[Agent A] Analyzes frontend impact
     |
     |--> A1 (Mobile): Needs pressure display UI <-- YOUR WORK
     |--> A2 (Web): Dashboard might need monitoring view
     |
     v
[Agent A decides]: Needs backend API -> calls Agent B
     |
     v
[Agent B] Analyzes backend impact
     |
     |--> B1 (API): New monitoring endpoints needed
     |--> B2 (WebSocket): Real-time push to clients
     |--> B3 (MongoDB): Current readings storage
     |--> B4 (PostgreSQL): Historical data storage
     |
     v
[Agent B decides]: Needs sensor data -> calls Agent C
     |
     v
[Agent C] Analyzes in-car systems
     |
     |--> C5 (Sensors): Tire pressure monitoring
     |--> C2 (Redis): Real-time data caching
     |--> C1 (Cloud Comm): Send data to backend
```

---

## Step 2: Download Your Task File

After Jenkins completes, download:

```
analysis-reports/
  |-- tire-pressure-monitoring-analysis.md  (full analysis)
  `-- component-tasks/
      `-- task-A1.md  <-- YOUR FILE
```

---

## Step 3: Review task-A1.md

### Example Contents of task-A1.md

```markdown
# Task: A1

**Component**: A1  
**Technology**: React Native (Mobile App)  
**Effort Estimate**: 6 hours

Generated from analysis: `tire-pressure-monitoring-analysis.md`

## Analysis Excerpt

Agent A Analysis - Component A1 (Car User Mobile App):
- Create new screen: TirePressureMonitor.js
- Add navigation from car detail screen to tire pressure monitor
- Display all 4 tire pressures with visual indicators
- Show pressure values in bar/psi with unit toggle
- Add real-time updates via WebSocket
- Display historical pressure chart (last 7 days)
- Add refresh button to fetch latest data
- Show last update timestamp
- Handle loading states and error messages
- API calls: GET /api/monitoring/tire-pressure/:carId
- API calls: GET /api/monitoring/tire-pressure/:carId/history

Dependencies:
- B1 (Backend): API endpoints must be ready
- B2 (WebSocket): Real-time connection for updates
- Design: Need tire pressure icon and color scheme

## Proposed Implementation

### Example Code for A1

```javascript
// File: A1-car-user-app/screens/TirePressureMonitor.js
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, RefreshControl, ScrollView } from 'react-native';
import { useRoute } from '@react-navigation/native';
import io from 'socket.io-client';

const TirePressureMonitor = () => {
  const route = useRoute();
  const { carId } = route.params;
  
  const [pressureData, setPressureData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [unit, setUnit] = useState('bar'); // 'bar' or 'psi'
  
  // Fetch current tire pressure data
  const fetchPressureData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `https://api.cardemo.com/api/monitoring/tire-pressure/${carId}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch tire pressure data');
      }
      
      const data = await response.json();
      setPressureData(data);
      
    } catch (err) {
      setError(err.message);
      console.error('Error fetching pressure data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  // Setup WebSocket for real-time updates
  useEffect(() => {
    const socket = io('https://api.cardemo.com');
    
    socket.on('tire-pressure:update', (data) => {
      if (data.carId === carId) {
        setPressureData(prevData => ({
          ...prevData,
          tirePressure: data.tirePressure,
          timestamp: data.timestamp
        }));
      }
    });
    
    return () => {
      socket.disconnect();
    };
  }, [carId]);
  
  // Initial load
  useEffect(() => {
    fetchPressureData();
  }, [carId]);
  
  // Pull to refresh
  const onRefresh = () => {
    setRefreshing(true);
    fetchPressureData();
  };
  
  // Convert bar to psi if needed
  const convertPressure = (valueInBar) => {
    if (unit === 'psi') {
      return (valueInBar * 14.5038).toFixed(1);
    }
    return valueInBar.toFixed(1);
  };
  
  // Get color based on pressure value (in bar)
  const getPressureColor = (valueInBar) => {
    if (valueInBar < 2.0) return '#FF3B30'; // Critical - red
    if (valueInBar < 2.2) return '#FF9500'; // Warning - orange
    return '#34C759'; // Good - green
  };
  
  if (loading && !pressureData) {
    return (
      <View style={styles.centerContainer}>
        <Text>Loading tire pressure data...</Text>
      </View>
    );
  }
  
  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <Text style={styles.retryText} onPress={fetchPressureData}>
          Tap to retry
        </Text>
      </View>
    );
  }
  
  if (!pressureData) {
    return (
      <View style={styles.centerContainer}>
        <Text>No tire pressure data available</Text>
      </View>
    );
  }
  
  const { tirePressure, licensePlate, timestamp } = pressureData;
  
  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.title}>Tire Pressure Monitor</Text>
        <Text style={styles.licensePlate}>{licensePlate}</Text>
        <Text style={styles.timestamp}>
          Last updated: {new Date(timestamp).toLocaleString()}
        </Text>
      </View>
      
      {/* Unit Toggle */}
      <View style={styles.unitToggle}>
        <Text
          style={[styles.unitButton, unit === 'bar' && styles.unitButtonActive]}
          onPress={() => setUnit('bar')}
        >
          bar
        </Text>
        <Text
          style={[styles.unitButton, unit === 'psi' && styles.unitButtonActive]}
          onPress={() => setUnit('psi')}
        >
          psi
        </Text>
      </View>
      
      {/* Tire Pressure Grid */}
      <View style={styles.tiresContainer}>
        {/* Front Left */}
        <View style={styles.tireCard}>
          <Text style={styles.tireLabel}>Front Left</Text>
          <Text
            style={[
              styles.pressureValue,
              { color: getPressureColor(tirePressure.frontLeft) }
            ]}
          >
            {convertPressure(tirePressure.frontLeft)}
          </Text>
          <Text style={styles.unitLabel}>{unit}</Text>
        </View>
        
        {/* Front Right */}
        <View style={styles.tireCard}>
          <Text style={styles.tireLabel}>Front Right</Text>
          <Text
            style={[
              styles.pressureValue,
              { color: getPressureColor(tirePressure.frontRight) }
            ]}
          >
            {convertPressure(tirePressure.frontRight)}
          </Text>
          <Text style={styles.unitLabel}>{unit}</Text>
        </View>
      </View>
      
      <View style={styles.tiresContainer}>
        {/* Rear Left */}
        <View style={styles.tireCard}>
          <Text style={styles.tireLabel}>Rear Left</Text>
          <Text
            style={[
              styles.pressureValue,
              { color: getPressureColor(tirePressure.rearLeft) }
            ]}
          >
            {convertPressure(tirePressure.rearLeft)}
          </Text>
          <Text style={styles.unitLabel}>{unit}</Text>
        </View>
        
        {/* Rear Right */}
        <View style={styles.tireCard}>
          <Text style={styles.tireLabel}>Rear Right</Text>
          <Text
            style={[
              styles.pressureValue,
              { color: getPressureColor(tirePressure.rearRight) }
            ]}
          >
            {convertPressure(tirePressure.rearRight)}
          </Text>
          <Text style={styles.unitLabel}>{unit}</Text>
        </View>
      </View>
      
      {/* Pressure Guide */}
      <View style={styles.guideContainer}>
        <Text style={styles.guideTitle}>Pressure Status Guide</Text>
        <View style={styles.guideRow}>
          <View style={[styles.guideDot, { backgroundColor: '#34C759' }]} />
          <Text style={styles.guideText}>Good (>= 2.2 bar / 32 psi)</Text>
        </View>
        <View style={styles.guideRow}>
          <View style={[styles.guideDot, { backgroundColor: '#FF9500' }]} />
          <Text style={styles.guideText}>Low (2.0-2.2 bar / 29-32 psi)</Text>
        </View>
        <View style={styles.guideRow}>
          <View style={[styles.guideDot, { backgroundColor: '#FF3B30' }]} />
          <Text style={styles.guideText}>Critical (< 2.0 bar / 29 psi)</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  licensePlate: {
    fontSize: 18,
    color: '#666',
    marginBottom: 4,
  },
  timestamp: {
    fontSize: 14,
    color: '#999',
  },
  unitToggle: {
    flexDirection: 'row',
    justifyContent: 'center',
    padding: 15,
    gap: 10,
  },
  unitButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#007AFF',
    color: '#007AFF',
    fontSize: 16,
  },
  unitButtonActive: {
    backgroundColor: '#007AFF',
    color: '#fff',
  },
  tiresContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  tireCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    width: '45%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tireLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  pressureValue: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  unitLabel: {
    fontSize: 14,
    color: '#999',
  },
  guideContainer: {
    backgroundColor: '#fff',
    margin: 20,
    padding: 15,
    borderRadius: 12,
  },
  guideTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  guideRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 5,
  },
  guideDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 10,
  },
  guideText: {
    fontSize: 14,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    marginBottom: 10,
  },
  retryText: {
    fontSize: 16,
    color: '#007AFF',
  },
});

export default TirePressureMonitor;
```

### Navigation Setup

```javascript
// File: A1-car-user-app/navigation/AppNavigator.js
// Add to your existing navigation stack

import TirePressureMonitor from '../screens/TirePressureMonitor';

// In your Stack.Navigator:
<Stack.Screen 
  name="TirePressureMonitor" 
  component={TirePressureMonitor}
  options={{ title: 'Tire Pressure' }}
/>
```

### Add Button to Car Detail Screen

```javascript
// File: A1-car-user-app/screens/CarDetailScreen.js
// Add this button to navigate to tire pressure monitor

<TouchableOpacity
  style={styles.monitorButton}
  onPress={() => navigation.navigate('TirePressureMonitor', { carId: car.id })}
>
  <Text style={styles.monitorButtonText}>View Tire Pressure</Text>
</TouchableOpacity>
```

## Suggested Subtasks

- [X] Review analysis excerpt and understand requirements
- [ ] Adapt the code template to specific feature needs
- [ ] Create `screens/TirePressureMonitor.js` component
- [ ] Add navigation route in `AppNavigator.js`
- [ ] Add button to Car Detail screen for navigation
- [ ] Install socket.io-client package: `npm install socket.io-client`
- [ ] Test with mock data before B1 integration
- [ ] Coordinate with B1 team: confirm API endpoint format
- [ ] Test real-time WebSocket updates with B2
- [ ] Add loading and error states
- [ ] Test unit conversion (bar <-> psi)
- [ ] Test color indicators for pressure levels
- [ ] Add pull-to-refresh functionality
- [ ] Test on both iOS and Android
- [ ] Add accessibility labels for screen readers

## Notes

- **Component**: A1 (Car User Mobile App)
- **Effort**: 6 hours
- **Dependencies**: 
  - B1 (API): Needs endpoints ready for testing
  - B2 (WebSocket): Needs real-time connection for updates
  - Design team: Need tire pressure icons and color scheme approval
- **API Endpoints Used**:
  - `GET /api/monitoring/tire-pressure/:carId` - Get current readings
  - WebSocket event: `tire-pressure:update` - Real-time updates
- **UI Components**:
  - Tire pressure cards (4 tires)
  - Unit toggle (bar/psi)
  - Status guide
  - Pull-to-refresh
- **Libraries Needed**:
  - `socket.io-client` for WebSocket connection
  - `@react-navigation/native` for navigation (already installed)
```

---

## Step 4: What You Need to Do

### As an A1 Developer:

1. **Read the task file** (`task-A1.md`)
2. **Copy the example code** as a starting point
3. **Coordinate with other teams**:
   - Ask B1 team: "Are the monitoring API endpoints ready?"
   - Ask B2 team: "What's the WebSocket endpoint URL?"
   - Ask Design team: "Can you approve the color scheme?"
4. **Implement the screen** in your A1 codebase
5. **Test with mock data** before backend integration
6. **Write tests** for your components
7. **Test on both iOS and Android devices**
8. **Create a small PR** focused only on A1 changes

### Your Deliverables:

- `A1-car-user-app/screens/TirePressureMonitor.js` - Main screen
- `A1-car-user-app/navigation/AppNavigator.js` - Navigation setup
- Updated Car Detail screen with navigation button
- `A1-car-user-app/__tests__/TirePressureMonitor.test.js` - Unit tests
- Screenshots for PR review

---

## Step 5: Integration with Other Components

### Data Flow (for your understanding):

```
User taps "View Tire Pressure" button
     |
     v
A1 (YOU!) navigates to TirePressureMonitor
     |
     v
A1 (YOU!) calls B1 API: GET /api/monitoring/tire-pressure/:carId
     |
     v
B1 (Backend) fetches from B3 (MongoDB)
     |
     v
B1 returns JSON data to A1
     |
     v
A1 (YOU!) displays tire pressures
     |
     v
B2 (WebSocket) pushes real-time updates
     |
     v
A1 (YOU!) updates UI automatically
```

### Your Touch Points:

- **Downstream (you call)**:
  - B1: You call REST API for current data
  - B2: You connect via WebSocket for real-time updates
  
- **No upstream dependencies**: You are the entry point for the user

---

## Summary

**As an A1 developer, you now know**:

[X] What screen to create  
[X] What UI components to implement  
[X] What API endpoints to call  
[X] How to handle real-time updates  
[X] What other components you depend on (B1, B2)  
[X] Example code to start from  
[X] Estimated effort (6 hours)  
[X] Clear subtasks to complete  

**You DON'T need to understand**:
- How B1 fetches data from databases
- How C5 generates sensor data
- How B3/B4 store data
- The full system architecture

**You ONLY need to focus on**: Your A1 mobile UI and API integration.

This is the power of component-level task breakdown! [*]
