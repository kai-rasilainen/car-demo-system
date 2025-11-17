# Ollama Dev Tools - Windows Quick Start

## Installation on Windows

### 1. Install Ollama
1. Download Ollama from https://ollama.com/download
2. Run the installer
3. Open Command Prompt or PowerShell to verify:
   ```cmd
   ollama --version
   ```

### 2. Pull the Model
```cmd
ollama pull llama3:8b
```

### 3. Setup Dev Tools
```cmd
cd \path\to\car-demo-system
setup-ollama.bat
```

## Usage on Windows

Use `python` instead of `python3`, and use backslashes `\` for paths:

### Analyze Code
```cmd
python dev-tools\ollama-dev-assistant.py analyze B-car-demo-backend\B1-web-server\server.js
```

### Generate Documentation
```cmd
python dev-tools\ollama-dev-assistant.py document C-car-demo-in-car\C5-data-sensors\sensor_simulator.py --output docs\sensor-doc.md
```

### Generate Tests
```cmd
python dev-tools\ollama-dev-assistant.py generate-tests B-car-demo-backend\B2-iot-gateway\server.js --output tests\b2-gateway.test.js
```

### Code Review
```cmd
python dev-tools\ollama-dev-assistant.py review A-car-demo-frontend\A1-car-user-app\App.js
```

### Explain Code
```cmd
python dev-tools\ollama-dev-assistant.py explain C-car-demo-in-car\C1-cloud-communication\cloud_communicator.py
```

## Batch Processing on Windows

### Analyze Multiple Files

Create `analyze-all.bat`:
```batch
@echo off
for %%f in (B-car-demo-backend\B1-web-server\*.js) do (
    echo Analyzing %%f
    python dev-tools\ollama-dev-assistant.py analyze "%%f"
    echo.
)
```

### Generate Docs for All Python Files

Create `doc-all-python.bat`:
```batch
@echo off
if not exist docs\auto-generated mkdir docs\auto-generated

for /R C-car-demo-in-car %%f in (*.py) do (
    echo Documenting %%~nxf
    python dev-tools\ollama-dev-assistant.py document "%%f" --output "docs\auto-generated\%%~nf.md"
)
```

## PowerShell Examples

### Analyze Changed Files
```powershell
Get-ChildItem -Recurse -Include *.js,*.py | ForEach-Object {
    Write-Host "Analyzing $($_.Name)..."
    python dev-tools\ollama-dev-assistant.py analyze $_.FullName
}
```

### Generate Tests for All Services
```powershell
Get-ChildItem B-car-demo-backend\*\server.js | ForEach-Object {
    $testFile = "tests\$($_.Directory.Name).test.js"
    Write-Host "Generating tests for $($_.Name)..."
    python dev-tools\ollama-dev-assistant.py generate-tests $_.FullName --output $testFile
}
```

## VS Code Integration (Windows)

Add to `.vscode\tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Ollama: Analyze Current File",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}\\dev-tools\\ollama-dev-assistant.py",
        "analyze",
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
      "command": "python",
      "args": [
        "${workspaceFolder}\\dev-tools\\ollama-dev-assistant.py",
        "generate-tests",
        "${file}",
        "--output",
        "${workspaceFolder}\\tests\\${fileBasenameNoExtension}.test${fileExtname}"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## Troubleshooting

### "ollama not found"
- Make sure Ollama is installed from https://ollama.com/download
- Restart your terminal after installation
- Check if `C:\Users\YourName\AppData\Local\Programs\Ollama` is in your PATH

### "Model not found"
```cmd
ollama pull llama3:8b
```

### Python not found
- Install Python from https://python.org
- Make sure "Add Python to PATH" was checked during installation

### Slow performance
- Close other applications
- Use smaller models: `--model llama3:8b` is already optimized
- Increase timeout in the script if needed

## Model Recommendations for Windows

### Fast (Lower RAM)
```cmd
ollama pull llama3:8b
```
- RAM: ~8GB
- Speed: Fast
- Quality: Good

### Best Quality (More RAM)
```cmd
ollama pull codellama:13b
```
- RAM: ~16GB
- Speed: Moderate
- Quality: Excellent for code
