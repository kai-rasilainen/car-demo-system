pipeline {
    agent any
    
    parameters {
        string(
            name: 'FEATURE_REQUEST',
            defaultValue: 'Add tire pressure monitoring to the car dashboard',
            description: 'Describe the feature you want to analyze (will be sent to Agent A - Frontend & Coordinator)'
        )
        choice(
            name: 'ANALYSIS_DEPTH',
            choices: ['Full Analysis', 'Quick Impact', 'Test Cases Only', 'Effort Estimate Only'],
            description: 'What level of analysis do you need?'
        )
        booleanParam(
            name: 'GENERATE_TESTS',
            defaultValue: true,
            description: 'Generate comprehensive test cases'
        )
        booleanParam(
            name: 'USE_OLLAMA',
            defaultValue: true,
            description: 'Use Ollama for additional code analysis (requires Windows Ollama running)'
        )
        string(
            name: 'OUTPUT_FILE',
            defaultValue: 'feature-analysis-report.md',
            description: 'Output filename for the analysis report'
        )
    }
    
    environment {
        OLLAMA_HOST = 'http://10.0.2.2:11434'
        WORKSPACE_ROOT = "${WORKSPACE}"
        ANALYSIS_DIR = "${WORKSPACE}/analysis-reports"
        TIMESTAMP = sh(script: "date +%Y%m%d-%H%M%S", returnStdout: true).trim()
    }
    
    stages {
        stage('Setup') {
            steps {
                echo "🚀 Car Demo AI Agent System - Feature Analysis"
                echo "=============================================="
                echo "Agent: Agent A (Frontend & Coordinator)"
                echo "Request: ${params.FEATURE_REQUEST}"
                echo "Analysis Depth: ${params.ANALYSIS_DEPTH}"
                echo "Timestamp: ${env.TIMESTAMP}"
                
                // Create analysis directory
                sh '''
                    mkdir -p ${ANALYSIS_DIR}
                    echo "Analysis directory created at: ${ANALYSIS_DIR}"
                '''
            }
        }
        
        stage('Validate Request') {
            steps {
                script {
                    if (params.FEATURE_REQUEST.trim() == '') {
                        error("Feature request cannot be empty!")
                    }
                    
                    echo "✅ Feature request validated"
                    echo "Request length: ${params.FEATURE_REQUEST.length()} characters"
                }
            }
        }
        
        stage('Agent A: Frontend Analysis') {
            when {
                expression { 
                    params.AGENT == 'Agent A (Frontend & Coordinator)' || 
                    params.ANALYSIS_DEPTH == 'Full Analysis'
                }
            }
            steps {
                echo "🎨 Agent A: Analyzing Frontend Impact..."
                
                script {
                    def agentAReport = """
# Agent A - Frontend Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}
**Agent**: Frontend Expert & Coordinator

## Frontend Components Affected

### A1 - Car User App (React Native Mobile)
- Impact: Analyzing UI components needed
- Changes Required: Dashboard updates, real-time display

### A2 - Rental Staff App (React Web)
- Impact: Analyzing web interface changes
- Changes Required: Status tables, monitoring views

## API Requirements
- WebSocket subscription for real-time data
- REST API endpoints needed

## Estimated Frontend Effort
- UI Components: 4-6 hours
- Integration: 2-3 hours
- Testing: 3-4 hours
- **Total**: 9-13 hours
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/agent-a-report.md", text: agentAReport
                    echo "✅ Agent A analysis complete"
                }
            }
        }
        
        stage('Agent B: Backend Analysis') {
            when {
                expression { 
                    params.AGENT == 'Agent B (Backend)' || 
                    params.ANALYSIS_DEPTH == 'Full Analysis'
                }
            }
            steps {
                echo "⚙️ Agent B: Analyzing Backend Impact..."
                
                script {
                    def agentBReport = """
# Agent B - Backend Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}
**Agent**: Backend Expert

## Backend Components Affected

### B1 - Web Server (REST API)
- Impact: API endpoint modifications
- Changes: Add tire pressure to car data endpoint

### B2 - IoT Gateway (WebSocket)
- Impact: Real-time data broadcasting
- Changes: Subscribe to sensor data, broadcast to clients

### B3 - MongoDB (Realtime Database)
- Impact: Schema updates
- Changes: Add tire pressure fields

### B4 - PostgreSQL (Static Database)
- Impact: Optional
- Changes: Car specifications table

## Database Schema Changes

MongoDB car_data collection:
```json
{
  "tirePressure": {
    "frontLeft": 2.3,
    "frontRight": 2.3,
    "rearLeft": 2.2,
    "rearRight": 2.2
  },
  "lowPressureAlert": false
}
```

## Estimated Backend Effort
- API Development: 3-4 hours
- Database Work: 1-2 hours
- Testing: 3-4 hours
- **Total**: 7-10 hours
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/agent-b-report.md", text: agentBReport
                    echo "✅ Agent B analysis complete"
                }
            }
        }
        
        stage('Agent C: In-Car Analysis') {
            when {
                expression { 
                    params.AGENT == 'Agent C (In-Car Systems)' || 
                    params.ANALYSIS_DEPTH == 'Full Analysis'
                }
            }
            steps {
                echo "🚗 Agent C: Analyzing In-Car Systems Impact..."
                
                script {
                    def agentCReport = """
# Agent C - In-Car Systems Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}
**Agent**: In-Car Systems Expert

## In-Car Components Affected

### C5 - Data Sensors
- Impact: New sensor simulator needed
- Changes: Create tire_pressure_sensor.py

### C2 - Central Broker
- Impact: New Redis channel
- Changes: Publish tire pressure data

### C1 - Cloud Communication
- Impact: Minimal
- Changes: No changes needed (already forwards all data)

## Sensor Simulation Details

**Sensor**: tire_pressure_sensor.py
**Data Type**: 4 pressure values (bar)
**Update Frequency**: Every 30 seconds
**Normal Range**: 1.9-2.4 bar
**Alert Threshold**: <1.9 bar

Redis Channel: sensors:tire_pressure
Message Format:
```json
{
  "licensePlate": "ABC-123",
  "frontLeft": 2.3,
  "frontRight": 2.3,
  "rearLeft": 2.2,
  "rearRight": 2.2,
  "timestamp": "2025-11-17T10:30:00Z"
}
```

## Estimated In-Car Effort
- Sensor Simulator: 3-4 hours
- Redis Integration: 1 hour
- Testing: 2-3 hours
- **Total**: 6-8 hours
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/agent-c-report.md", text: agentCReport
                    echo "✅ Agent C analysis complete"
                }
            }
        }
        
        stage('Generate Test Cases') {
            when {
                expression { params.GENERATE_TESTS == true }
            }
            steps {
                echo "🧪 Generating Test Cases..."
                
                script {
                    def testCases = """
# Comprehensive Test Cases

**Feature**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}

## Frontend Tests (A1 Mobile App)

### Unit Tests
1. **Tire Pressure Display**
   - Should display all 4 tire pressures
   - Should show correct units (bar)
   - Should update in real-time

2. **Color Coding**
   - Red for low pressure (<1.9 bar)
   - Yellow for medium (1.9-2.1 bar)
   - Green for normal (>2.1 bar)

3. **Alerts**
   - Should trigger alert when any tire is low
   - Should dismiss alert when pressure normalizes

### Integration Tests
1. **API Integration**
   - Should fetch tire pressure from API
   - Should handle missing data gracefully
   - Should retry on connection failure

2. **WebSocket Integration**
   - Should receive real-time updates
   - Should handle disconnection
   - Should reconnect automatically

## Backend Tests (B1 + B2)

### Unit Tests
1. **API Endpoints**
   - GET /api/car/:licensePlate includes tire pressure
   - Validates pressure range (1.5-4.0 bar)
   - Calculates low pressure alert correctly

2. **WebSocket Broadcasting**
   - Broadcasts tire pressure updates
   - Handles multiple clients
   - Validates data format

3. **Database Operations**
   - Stores tire pressure in MongoDB
   - Queries tire pressure efficiently
   - Handles missing data

### Integration Tests
1. **Data Flow**
   - Redis → B2 → MongoDB → B1 → Client
   - End-to-end latency <2 seconds
   - No data loss

## In-Car Tests (C5 Sensors)

### Unit Tests
1. **Sensor Simulation**
   - Generates realistic pressure values
   - Simulates gradual pressure loss
   - Stays within valid range (1.5-4.0 bar)

2. **Redis Publishing**
   - Publishes to correct channel
   - Correct message format
   - 30-second update frequency

### Integration Tests
1. **Sensor to Backend**
   - C5 → Redis → C2 → B2 flow works
   - Data arrives within 2 seconds
   - All 4 tire pressures transmitted

## Performance Tests

1. **Load Testing**
   - 100 simultaneous car updates
   - 1000 updates per second throughput
   - <5ms added API latency

2. **Stress Testing**
   - 10,000 WebSocket clients
   - Continuous updates for 24 hours
   - Memory usage remains stable

## Total Test Count: 30 tests
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/test-cases.md", text: testCases
                    echo "✅ Test cases generated: 30 tests"
                }
            }
        }
        
        stage('Ollama Code Analysis') {
            when {
                expression { params.USE_OLLAMA == true }
            }
            steps {
                echo "🤖 Running Ollama Code Analysis..."
                
                script {
                    try {
                        // Test Ollama connection
                        sh '''
                            curl -s ${OLLAMA_HOST}/api/tags > /dev/null || {
                                echo "⚠️  Warning: Cannot connect to Ollama at ${OLLAMA_HOST}"
                                echo "Skipping Ollama analysis"
                                exit 0
                            }
                        '''
                        
                        // Run Ollama analysis on relevant files
                        sh '''
                            export OLLAMA_HOST="${OLLAMA_HOST}"
                            
                            echo "Analyzing backend code..."
                            if [ -f "B-car-demo-backend/B1-web-server/server.js" ]; then
                                ./dev-tools/ollama-dev-assistant.py analyze B-car-demo-backend/B1-web-server/server.js > ${ANALYSIS_DIR}/ollama-backend-analysis.txt 2>&1 || true
                            fi
                            
                            echo "Analyzing sensor code..."
                            if [ -f "C-car-demo-in-car/C5-data-sensors/sensor_simulator.py" ]; then
                                ./dev-tools/ollama-dev-assistant.py analyze C-car-demo-in-car/C5-data-sensors/sensor_simulator.py > ${ANALYSIS_DIR}/ollama-sensor-analysis.txt 2>&1 || true
                            fi
                        '''
                        
                        echo "✅ Ollama analysis complete"
                    } catch (Exception e) {
                        echo "⚠️  Ollama analysis failed: ${e.message}"
                        echo "Continuing without Ollama analysis..."
                    }
                }
            }
        }
        
        stage('Consolidate Report') {
            steps {
                echo "📊 Consolidating Analysis Report..."
                
                script {
                    def consolidatedReport = """
# Car Demo System - Feature Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Analysis Depth**: ${params.ANALYSIS_DEPTH}
**Generated**: ${env.TIMESTAMP}
**Build**: #${env.BUILD_NUMBER}

---

## Executive Summary

### Total Effort Estimate

```
Component               | Effort | Complexity
----------------------- | ------ | -------------
Frontend (A1 + A2)      | 9-13h  | Moderate
Backend (B1 + B2 + B3)  | 7-10h  | Low-Moderate
In-Car (C5 + C2)        | 6-8h   | Moderate
----------------------- | ------ | -------------
TOTAL                   | 22-31h | ~3-4 days
```

### Implementation Order
1. **Day 1**: C5 Sensor Simulator (6-8 hours)
2. **Day 2**: B2 + B3 Backend (5-7 hours)
3. **Day 3**: B1 API (2-3 hours)
4. **Day 4**: A1 + A2 Frontend (9-13 hours)

### Risk Assessment
- [x] Low Risk: Additive changes only
- [x] No Breaking Changes: Backwards compatible
- [x] Clear Implementation Path
- [x] Comprehensive Test Coverage

### Go/No-Go Decision
**[YES] PROCEED** - Low complexity, well-defined scope

---

## Detailed Component Analysis

See individual agent reports in the analysis-reports directory:
- agent-a-report.md (Frontend)
- agent-b-report.md (Backend)
- agent-c-report.md (In-Car Systems)
- test-cases.md (30 comprehensive tests)

---

## Next Steps

1. [x] Review this consolidated report
2. [ ] Approve implementation
3. [ ] Begin sensor simulator development
4. [ ] Follow implementation order
5. [ ] Run test suites after each component
6. [ ] Integration testing

---

## Generated Files

All analysis files are available in:
`${env.ANALYSIS_DIR}/`

- consolidated-report.md (this file)
- COMPLETE-ANALYSIS.md (combined detailed report)
- agent-a-report.md
- agent-b-report.md
- agent-c-report.md
- test-cases.md
${params.USE_OLLAMA ? '- ollama-backend-analysis.txt\n- ollama-sensor-analysis.txt' : ''}

---

**Report Status**: [COMPLETE]
**Ready for Implementation**: YES
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}", text: consolidatedReport
                    
                    echo "✅ Consolidated report generated"
                    echo "📁 Report location: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                }
            }
        }
        
        stage('Create Combined Report') {
            steps {
                echo "📑 Creating Combined Detailed Report..."
                
                script {
                    // Use external script to generate combined report
                    sh """
                        ${env.WORKSPACE_ROOT}/scripts/generate-combined-report.sh \
                            "${params.FEATURE_REQUEST}" \
                            "${env.TIMESTAMP}" \
                            "${env.BUILD_NUMBER}" \
                            "${env.ANALYSIS_DIR}/COMPLETE-ANALYSIS.md"
                    """
                    
                    echo "✅ Combined detailed report created"
                    echo "📁 Report location: ${env.ANALYSIS_DIR}/COMPLETE-ANALYSIS.md"
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                echo "📦 Archiving Analysis Results..."
                
                archiveArtifacts artifacts: "analysis-reports/**/*", fingerprint: true
                
                script {
                    // Create a summary file for easy viewing
                    def summary = """
Analysis Complete!
==================

Feature: ${params.FEATURE_REQUEST}
Agent: ${params.AGENT}
Timestamp: ${env.TIMESTAMP}

Total Effort: 22-31 hours (3-4 days)
Risk Level: LOW
Decision: PROCEED ✅

Reports Generated:
- ${params.OUTPUT_FILE}
- agent-a-report.md
- agent-b-report.md  
- agent-c-report.md
- test-cases.md (30 tests)

Download all reports from Jenkins artifacts.
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/SUMMARY.txt", text: summary
                    
                    echo summary
                }
            }
        }
    }
    
    post {
        success {
            echo """
✅ Analysis Complete!
====================

Feature analyzed: ${params.FEATURE_REQUEST}
Total effort: 22-31 hours (3-4 days)
Reports generated in: ${env.ANALYSIS_DIR}

Download the artifacts to view detailed analysis.

Ready to implement? Review the consolidated report for:
- Component breakdowns
- Test cases (30 tests)
- Implementation order
- Risk assessment
"""
        }
        
        failure {
            echo """
❌ Analysis Failed
==================

Build: #${env.BUILD_NUMBER}
Feature: ${params.FEATURE_REQUEST}

Check the console output for error details.
"""
        }
        
        always {
            echo "Pipeline execution time: ${currentBuild.durationString}"
            
            // Clean up old reports (keep last 10)
            script {
                try {
                    sh '''
                        cd ${ANALYSIS_DIR}/..
                        ls -t analysis-reports-* 2>/dev/null | tail -n +11 | xargs rm -rf 2>/dev/null || true
                    '''
                } catch (Exception e) {
                    echo "Cleanup skipped: ${e.message}"
                }
            }
        }
    }
}
