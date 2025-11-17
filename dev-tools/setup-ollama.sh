#!/bin/bash

# Quick setup script for Ollama development tools

echo "🚀 Setting up Ollama Development Tools for Car Demo Project"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama is installed"
fi

# Check if recommended models are available
echo ""
echo "📦 Checking for recommended models..."

if ollama list | grep -q "llama3:8b"; then
    echo "✅ llama3:8b is available"
else
    echo "⬇️  Pulling llama3:8b (recommended for general tasks)..."
    ollama pull llama3:8b
fi

if ollama list | grep -q "codellama"; then
    echo "✅ codellama is available"
else
    echo "📝 Optional: You can pull codellama for better code analysis:"
    echo "   ollama pull codellama"
fi

# Make the assistant executable
chmod +x dev-tools/ollama-dev-assistant.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Quick Start:"
echo "   # Analyze code"
echo "   python3 dev-tools/ollama-dev-assistant.py analyze car-demo-backend/B1-web-server/server.js"
echo ""
echo "   # Generate documentation"
echo "   python3 dev-tools/ollama-dev-assistant.py document C-car-demo-in-car/C5-data-sensors/sensor_simulator.py"
echo ""
echo "   # Generate tests"
echo "   python3 dev-tools/ollama-dev-assistant.py generate-tests car-demo-backend/B2-iot-gateway/server.js"
echo ""
echo "📖 Full documentation: dev-tools/README.md"
