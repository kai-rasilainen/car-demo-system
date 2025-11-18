# Jenkins Pipeline for AI Agent System

This Jenkinsfile enables you to use the AI Agent system through Jenkins with input parameters.

## Features

✅ **Parameterized Pipeline** - Choose agent, request type, and analysis depth  
✅ **Multi-Agent Support** - Agent A, B, or C analysis  
✅ **Comprehensive Reports** - Markdown reports with effort estimates  
✅ **Test Case Generation** - Automatic test suite generation  
✅ **Ollama Integration** - Optional code analysis with Ollama  
✅ **Artifact Archiving** - All reports saved as Jenkins artifacts

## Setup in Jenkins

### 1. Create New Pipeline Job

1. Jenkins Dashboard → New Item
2. Enter name: `Car-Demo-Feature-Analysis`
3. Select: **Pipeline**
4. Click OK

### 2. Configure Pipeline

**Pipeline Section:**
- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/kai-rasilainen/car-demo-system.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

### 3. Save and Build

Click "Build with Parameters"

## Pipeline Parameters

### 1. AGENT
**Type**: Choice  
**Options**:
- Agent A (Frontend & Coordinator) ← **Recommended**
- Agent B (Backend)
- Agent C (In-Car Systems)

**Description**: Which agent to send the request to

### 2. FEATURE_REQUEST
**Type**: String  
**Default**: `Add tire pressure monitoring to the car dashboard`

**Example Requests**:
- "Add tire pressure monitoring to the car dashboard"
- "Show vehicle speed on the dashboard"
- "Add door lock/unlock feature"
- "Display battery charge level"
- "Show vehicle location history"

### 3. ANALYSIS_DEPTH
**Type**: Choice  
**Options**:
- Full Analysis ← **Recommended**
- Quick Impact
- Test Cases Only
- Effort Estimate Only

### 4. GENERATE_TESTS
**Type**: Boolean  
**Default**: `true`

Generate comprehensive test cases (30+ tests)

### 5. USE_OLLAMA
**Type**: Boolean  
**Default**: `false`

Enable Ollama-powered code analysis (requires Windows Ollama running at `http://10.0.2.2:11434`)

### 6. OUTPUT_FILE
**Type**: String  
**Default**: `feature-analysis-report.md`

Name of the consolidated report file

## Usage Examples

### Example 1: Tire Pressure Monitoring (Full Analysis)

**Parameters**:
```
AGENT: Agent A (Frontend & Coordinator)
FEATURE_REQUEST: Add tire pressure monitoring to the car dashboard
ANALYSIS_DEPTH: Full Analysis
GENERATE_TESTS: true
USE_OLLAMA: false
OUTPUT_FILE: tire-pressure-analysis.md
```

**Outputs**:
- `tire-pressure-analysis.md` - Consolidated report
- `agent-a-report.md` - Frontend analysis
- `agent-b-report.md` - Backend analysis
- `agent-c-report.md` - In-car systems analysis
- `test-cases.md` - 30+ test cases

### Example 2: Quick Backend Impact

**Parameters**:
```
AGENT: Agent B (Backend)
FEATURE_REQUEST: Add vehicle speed monitoring API
ANALYSIS_DEPTH: Quick Impact
GENERATE_TESTS: false
USE_OLLAMA: true
OUTPUT_FILE: speed-api-impact.md
```

**Outputs**:
- `speed-api-impact.md` - Backend-focused report
- `agent-b-report.md` - Backend analysis
- `ollama-backend-analysis.txt` - Ollama code analysis

### Example 3: Test Cases Only

**Parameters**:
```
AGENT: Agent A (Frontend & Coordinator)
FEATURE_REQUEST: Display engine temperature
ANALYSIS_DEPTH: Test Cases Only
GENERATE_TESTS: true
USE_OLLAMA: false
OUTPUT_FILE: engine-temp-tests.md
```

**Outputs**:
- `engine-temp-tests.md` - Test-focused report
- `test-cases.md` - Comprehensive test suite

## Pipeline Stages

### 1. Setup
- Creates analysis directory
- Validates environment
- Prints configuration

### 2. Validate Request
- Checks feature request is not empty
- Validates input parameters

### 3. Agent A: Frontend Analysis
- Analyzes UI components (A1 mobile, A2 web)
- Identifies API requirements
- Estimates frontend effort (9-13 hours)

### 4. Agent B: Backend Analysis
- Analyzes API changes (B1 web server)
- Identifies database changes (B3 MongoDB, B4 PostgreSQL)
- Analyzes real-time data (B2 IoT gateway)
- Estimates backend effort (7-10 hours)

### 5. Agent C: In-Car Analysis
- Analyzes sensor requirements (C5)
- Identifies Redis channel needs (C2)
- Plans simulation logic
- Estimates in-car effort (6-8 hours)

### 6. Generate Test Cases
- Creates comprehensive test suite
- Frontend tests (A1 + A2)
- Backend tests (B1 + B2)
- In-car tests (C5)
- Integration tests
- Total: 30+ tests

### 7. Ollama Code Analysis (Optional)
- Connects to Windows Ollama
- Analyzes existing backend code
- Analyzes sensor simulator code
- Generates AI-powered insights

### 8. Consolidate Report
- Combines all agent analyses
- Creates executive summary
- Calculates total effort (22-31 hours)
- Provides Go/No-Go decision

### 9. Archive Results
- Archives all markdown reports
- Archives Ollama analysis (if enabled)
- Creates downloadable artifacts

## Output Reports

All reports are saved in `analysis-reports/` directory:

### 1. Consolidated Report (Main Output)
**File**: `<OUTPUT_FILE>` (default: `feature-analysis-report.md`)

**Contents**:
- Executive summary
- Total effort breakdown
- Implementation order
- Risk assessment
- Go/No-Go decision
- Links to detailed reports

### 2. Agent A Report
**File**: `agent-a-report.md`

**Contents**:
- Frontend components affected (A1 + A2)
- UI requirements
- API needs
- Effort estimate

### 3. Agent B Report
**File**: `agent-b-report.md`

**Contents**:
- Backend components affected (B1 + B2 + B3 + B4)
- Database schema changes
- API modifications
- Effort estimate

### 4. Agent C Report
**File**: `agent-c-report.md`

**Contents**:
- In-car components affected (C1 + C2 + C5)
- Sensor simulation details
- Redis channel configuration
- Effort estimate

### 5. Test Cases
**File**: `test-cases.md`

**Contents**:
- Frontend unit tests
- Frontend integration tests
- Backend unit tests
- Backend integration tests
- In-car unit tests
- In-car integration tests
- Performance tests
- Total: 30+ tests

### 6. Summary
**File**: `SUMMARY.txt`

Quick overview text file with key metrics

## Accessing Reports

### Download from Jenkins UI

1. Open the build (e.g., Build #5)
2. Click "Build Artifacts"
3. Download `analysis-reports.zip`
4. Extract and view markdown files

### View in Jenkins

Reports are plain markdown - can be viewed directly in Jenkins workspace:
```
https://your-jenkins/job/Car-Demo-Feature-Analysis/5/artifact/analysis-reports/
```

## Jenkins Environment Variables

The pipeline uses these environment variables:

- `OLLAMA_HOST`: `http://10.0.2.2:11434` (Windows Ollama)
- `WORKSPACE_ROOT`: Jenkins workspace path
- `ANALYSIS_DIR`: `${WORKSPACE}/analysis-reports`
- `TIMESTAMP`: Current date/time (YYYYMMDD-HHMMSS)

## Ollama Integration

To enable Ollama code analysis:

### Prerequisites
1. Ollama running on Windows at `10.0.2.2:11434`
2. Model `llama3:8b` available
3. Ubuntu can reach Windows Ollama (firewall configured)

### Enable in Build
Set parameter: `USE_OLLAMA = true`

### What It Does
- Analyzes backend code (`B1-web-server/server.js`)
- Analyzes sensor code (`C5-data-sensors/sensor_simulator.py`)
- Generates AI insights about code quality
- Saves results in `ollama-*-analysis.txt`

## Example Build Output

```
🚀 Car Demo AI Agent System - Feature Analysis
==============================================
Agent: Agent A (Frontend & Coordinator)
Request: Add tire pressure monitoring to the car dashboard
Analysis Depth: Full Analysis
Timestamp: 20251117-143022

✅ Feature request validated
🎨 Agent A: Analyzing Frontend Impact...
✅ Agent A analysis complete
⚙️ Agent B: Analyzing Backend Impact...
✅ Agent B analysis complete
🚗 Agent C: Analyzing In-Car Systems Impact...
✅ Agent C analysis complete
🧪 Generating Test Cases...
✅ Test cases generated: 30 tests
📊 Consolidating Analysis Report...
✅ Consolidated report generated
📦 Archiving Analysis Results...

✅ Analysis Complete!
====================

Feature analyzed: Add tire pressure monitoring to the car dashboard
Total effort: 22-31 hours (3-4 days)
Reports generated in: /var/jenkins/workspace/Car-Demo-Feature-Analysis/analysis-reports

Download the artifacts to view detailed analysis.
```

## Troubleshooting

### "Cannot connect to Ollama"
- Check Windows Ollama is running
- Verify firewall allows port 11434
- Test: `curl http://10.0.2.2:11434/api/tags`
- Set `USE_OLLAMA = false` to skip

### "File not found" errors
- Ensure workspace has submodules: `git submodule update --init --recursive`
- Check repository structure matches expected paths

### Reports not generated
- Check Jenkins has write permissions in workspace
- Verify `analysis-reports/` directory created
- Check console output for specific errors

## Advanced Usage

### Custom Analysis Script

You can extend the Jenkinsfile to run custom analysis:

```groovy
stage('Custom Analysis') {
    steps {
        sh '''
            # Your custom analysis script
            ./my-custom-analyzer.sh "${FEATURE_REQUEST}"
        '''
    }
}
```

### Email Reports

Add email notification:

```groovy
post {
    success {
        emailext(
            subject: "Feature Analysis Complete: ${params.FEATURE_REQUEST}",
            body: readFile("${env.ANALYSIS_DIR}/SUMMARY.txt"),
            to: "team@example.com",
            attachmentsPattern: "analysis-reports/**/*"
        )
    }
}
```

### Slack Integration

Send to Slack:

```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "Feature Analysis Complete: ${params.FEATURE_REQUEST}\nEffort: 22-31 hours\nDecision: PROCEED ✅"
        )
    }
}
```

## Pipeline Metrics

Each build tracks:
- Execution time
- Reports generated
- Test cases created
- Ollama usage
- Artifacts archived

View in Jenkins Blue Ocean for visual pipeline.

## Next Steps

1. ✅ Create Jenkins pipeline job
2. ✅ Configure with this Jenkinsfile
3. ✅ Run "Build with Parameters"
4. ✅ Download and review analysis reports
5. ✅ Make implementation decision
6. ✅ Begin development following the plan

---

**Ready to analyze features?** Click "Build with Parameters" in Jenkins!
