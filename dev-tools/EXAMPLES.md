# Ollama Development Tools - Examples

## Quick Examples

### Example 1: Analyze Backend Code

```bash
cd /home/kai/projects/car-demo-repos/car-demo-system

# Analyze the web server
python3 dev-tools/ollama-dev-assistant.py analyze B-car-demo-backend/B1-web-server/server.js
```

**What it does**: Analyzes the code for bugs, performance issues, security vulnerabilities, and suggests improvements.

### Example 2: Generate Documentation

```bash
# Document the sensor simulator
python3 dev-tools/ollama-dev-assistant.py document C-car-demo-in-car/C5-data-sensors/sensor_simulator.py --output docs/sensor-simulator.md
```

**What it does**: Creates comprehensive documentation including function descriptions, parameters, usage examples, and edge cases.

### Example 3: Generate Tests

```bash
# Generate tests for IoT Gateway
python3 dev-tools/ollama-dev-assistant.py generate-tests B-car-demo-backend/B2-iot-gateway/server.js --output tests/b2-gateway.test.js
```

**What it does**: Creates complete test suites with unit tests, edge cases, and integration tests.

### Example 4: Code Review

```bash
# Get review feedback for cloud communicator
python3 dev-tools/ollama-dev-assistant.py review C-car-demo-in-car/C1-cloud-communication/cloud_communicator.py
```

**What it does**: Provides detailed code review focusing on architecture, design patterns, and refactoring opportunities.

### Example 5: Explain Complex Code

```bash
# Understand database queries
python3 dev-tools/ollama-dev-assistant.py explain B-car-demo-backend/B3-realtime-database/queries.js
```

**What it does**: Explains what the code does in simple terms, how it works step-by-step, and why certain approaches are used.

## Batch Processing Examples

### Analyze All Backend Services

```bash
#!/bin/bash
cd /home/kai/projects/car-demo-repos/car-demo-system

echo "Analyzing all backend services..."
for service in B-car-demo-backend/*/server.js; do
  echo "=== Analyzing $service ==="
  python3 dev-tools/ollama-dev-assistant.py analyze "$service"
  echo ""
done
```

### Generate Documentation for All Python Files

```bash
#!/bin/bash
cd /home/kai/projects/car-demo-repos/car-demo-system

mkdir -p docs/auto-generated

find C-car-demo-in-car -name "*.py" -type f | while read file; do
  basename=$(basename "$file" .py)
  echo "Documenting $file..."
  python3 dev-tools/ollama-dev-assistant.py document "$file" --output "docs/auto-generated/${basename}.md"
done
```

### Generate Tests for Entire Component

```bash
#!/bin/bash
cd /home/kai/projects/car-demo-repos/car-demo-system

mkdir -p tests/auto-generated

# Generate tests for all JS files in B1
for file in B-car-demo-backend/B1-web-server/*.js; do
  basename=$(basename "$file" .js)
  echo "Generating tests for $file..."
  python3 dev-tools/ollama-dev-assistant.py generate-tests "$file" --output "tests/auto-generated/${basename}.test.js"
done
```

## Integration Examples

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Analyzing staged files with Ollama..."

# Get staged JavaScript and Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|py)$')

if [ -n "$STAGED_FILES" ]; then
  for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
      echo "Analyzing $file..."
      python3 dev-tools/ollama-dev-assistant.py analyze "$file" | head -20
      echo ""
    fi
  done
fi

# Continue with commit
exit 0
```

### VS Code Task

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Ollama: Analyze Current File",
      "type": "shell",
      "command": "python3",
      "args": [
        "${workspaceFolder}/dev-tools/ollama-dev-assistant.py",
        "analyze",
        "${file}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Ollama: Document Current File",
      "type": "shell",
      "command": "python3",
      "args": [
        "${workspaceFolder}/dev-tools/ollama-dev-assistant.py",
        "document",
        "${file}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Ollama: Generate Tests",
      "type": "shell",
      "command": "python3",
      "args": [
        "${workspaceFolder}/dev-tools/ollama-dev-assistant.py",
        "generate-tests",
        "${file}",
        "--output",
        "${workspaceFolder}/tests/${fileBasenameNoExtension}.test${fileExtname}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## Advanced Examples

### Using Different Models

```bash
# Use codellama for code-specific analysis
ollama pull codellama
python3 dev-tools/ollama-dev-assistant.py analyze server.js --model codellama

# Use llama3.2 for documentation
python3 dev-tools/ollama-dev-assistant.py document server.js --model llama3.2
```

### Chaining Commands

```bash
#!/bin/bash
FILE="B-car-demo-backend/B1-web-server/server.js"

echo "=== Analysis ==="
python3 dev-tools/ollama-dev-assistant.py analyze "$FILE"

echo ""
echo "=== Review ==="
python3 dev-tools/ollama-dev-assistant.py review "$FILE"

echo ""
echo "=== Documentation ==="
python3 dev-tools/ollama-dev-assistant.py document "$FILE" --output "docs/$(basename $FILE .js).md"

echo ""
echo "=== Tests ==="
python3 dev-tools/ollama-dev-assistant.py generate-tests "$FILE" --output "tests/$(basename $FILE .js).test.js"
```

### CI/CD Integration

Add to `.github/workflows/ollama-analysis.yml`:

```yaml
name: Ollama Code Analysis

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Ollama
        run: curl -fsSL https://ollama.com/install.sh | sh
      
      - name: Pull Model
        run: ollama pull llama3.2
      
      - name: Analyze Changed Files
        run: |
          git diff --name-only origin/main...HEAD | grep -E '\.(js|py)$' | while read file; do
            echo "Analyzing $file..."
            python3 dev-tools/ollama-dev-assistant.py analyze "$file"
          done
```

## Tips & Tricks

### Speed Up Analysis
```bash
# Start Ollama server in background (faster subsequent calls)
ollama serve &

# Then use the assistant (will connect to running server)
python3 dev-tools/ollama-dev-assistant.py analyze file.js
```

### Save Results for Later
```bash
# Create analysis report
python3 dev-tools/ollama-dev-assistant.py analyze file.js > reports/analysis-$(date +%Y%m%d).txt
```

### Compare Before/After Refactoring
```bash
# Before
python3 dev-tools/ollama-dev-assistant.py review old-code.js > before.txt

# After refactoring
python3 dev-tools/ollama-dev-assistant.py review new-code.js > after.txt

# Compare
diff before.txt after.txt
```
