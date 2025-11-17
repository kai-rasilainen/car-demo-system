# Development Tools - Ollama Integration

This directory contains Ollama-powered development tools to assist with code analysis, documentation, and test generation for the car demo project.

## Prerequisites

1. **Ollama installed**: 
   - Linux/Mac: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Download from https://ollama.com/download
2. **Pull a model**: `ollama pull llama3:8b`

## Tools

### 1. Ollama Development Assistant

A Python CLI tool that uses Ollama for various development tasks.

#### Installation

```bash
# Make the script executable
chmod +x dev-tools/ollama-dev-assistant.py

# Optional: Create alias in your ~/.bashrc or ~/.zshrc
alias ollama-dev='python3 /path/to/car-demo-system/dev-tools/ollama-dev-assistant.py'
```

#### Usage

**Analyze Code** - Find bugs, performance issues, and improvement opportunities:
```bash
python3 dev-tools/ollama-dev-assistant.py analyze car-demo-backend/B1-web-server/server.js
```

**Generate Documentation** - Create comprehensive docs for code:
```bash
python3 dev-tools/ollama-dev-assistant.py document C-car-demo-in-car/C5-data-sensors/sensor_simulator.py
```

**Generate Tests** - Create test cases with full coverage:
```bash
python3 dev-tools/ollama-dev-assistant.py generate-tests car-demo-backend/B2-iot-gateway/server.js --output tests/test-b2-gateway.js
```

**Code Review** - Get detailed code review feedback:
```bash
python3 dev-tools/ollama-dev-assistant.py review car-demo-frontend/A1-car-user-app/App.js
```

**Explain Code** - Get simple explanations of what code does:
```bash
python3 dev-tools/ollama-dev-assistant.py explain car-demo-in-car/C1-cloud-communication/cloud_communicator.py
```

#### Options

- `--model MODEL` - Use a different Ollama model (default: llama3.2)
  ```bash
  python3 dev-tools/ollama-dev-assistant.py analyze file.js --model codellama
  ```

- `--output FILE` - Save output to file instead of stdout
  ```bash
  python3 dev-tools/ollama-dev-assistant.py document file.py --output docs/file-doc.md
  ```

## Recommended Models

### For Code Analysis
- **codellama**: Specialized for code understanding
  ```bash
  ollama pull codellama
  python3 dev-tools/ollama-dev-assistant.py analyze file.js --model codellama
  ```

### For Documentation
- **llama3:8b**: Good general-purpose model (default)
  ```bash
  ollama pull llama3:8b
  ```

### For Test Generation
- **codellama**: Better at generating syntactically correct test code
  ```bash
  ollama pull codellama
  python3 dev-tools/ollama-dev-assistant.py generate-tests file.js --model codellama
  ```

## Windows Usage

On Windows, use `python` instead of `python3`:

```cmd
python dev-tools\ollama-dev-assistant.py analyze file.js
python dev-tools\ollama-dev-assistant.py document file.py --output docs\file-doc.md
```

## Example Workflows

### Before Committing Code
```bash
# Analyze for issues
python3 dev-tools/ollama-dev-assistant.py analyze my-changes.js

# Generate tests if missing
python3 dev-tools/ollama-dev-assistant.py generate-tests my-changes.js --output tests/my-changes.test.js

# Get code review feedback
python3 dev-tools/ollama-dev-assistant.py review my-changes.js
```

### Documenting a Component
```bash
# Generate docs for all files in a component
for file in car-demo-backend/B1-web-server/*.js; do
  python3 dev-tools/ollama-dev-assistant.py document "$file" --output "docs/$(basename "$file" .js).md"
done
```

### Understanding Existing Code
```bash
# Get explanations for complex files
python3 dev-tools/ollama-dev-assistant.py explain car-demo-backend/B3-realtime-database/queries.js
```

## Integration with Git Hooks

You can set up Git hooks to automatically analyze code before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash
for file in $(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|py)$'); do
  echo "Analyzing $file..."
  python3 dev-tools/ollama-dev-assistant.py analyze "$file"
done
```

## Performance Tips

1. **Use smaller models for faster responses**: `llama3.2` is faster than larger models
2. **Run Ollama as a service**: `ollama serve` in background for faster startup
3. **Cache results**: Save analysis results to avoid re-analyzing unchanged files

## Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Or on Ubuntu
sudo snap install ollama
```

### "Model not found"
```bash
# Pull the model first
ollama pull llama3.2
```

### "Request timed out"
- Large files may take time
- Increase timeout in the script
- Use smaller models or split large files

## Future Enhancements

Planned features:
- [ ] Batch processing multiple files
- [ ] Integration with VS Code extension
- [ ] Automated PR reviews
- [ ] Code refactoring suggestions
- [ ] Security vulnerability scanning
- [ ] Performance profiling analysis
