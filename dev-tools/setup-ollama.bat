@echo off
REM Setup script for Ollama development tools on Windows

echo Setting up Ollama Development Tools for Car Demo Project
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Ollama not found. Please install from https://ollama.com/download
    echo After installation, run this script again.
    pause
    exit /b 1
) else (
    echo [OK] Ollama is installed
)

echo.
echo Checking for recommended models...

REM Check for llama3:8b
ollama list | findstr /C:"llama3:8b" >nul
if %ERRORLEVEL% NEQ 0 (
    echo Pulling llama3:8b (recommended for general tasks)...
    ollama pull llama3:8b
) else (
    echo [OK] llama3:8b is available
)

echo.
echo Optional: You can pull codellama for better code analysis:
echo    ollama pull codellama
echo.

echo [OK] Setup complete!
echo.
echo Quick Start:
echo    REM Analyze code
echo    python dev-tools\ollama-dev-assistant.py analyze car-demo-backend\B1-web-server\server.js
echo.
echo    REM Generate documentation
echo    python dev-tools\ollama-dev-assistant.py document C-car-demo-in-car\C5-data-sensors\sensor_simulator.py
echo.
echo    REM Generate tests
echo    python dev-tools\ollama-dev-assistant.py generate-tests car-demo-backend\B2-iot-gateway\server.js
echo.
echo Full documentation: dev-tools\README.md
echo.
pause
