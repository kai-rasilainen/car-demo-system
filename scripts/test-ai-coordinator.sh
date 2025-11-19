#!/bin/bash
# Test script for AI Agent Coordinator

echo "🧪 Testing AI Agent Coordinator"
echo "================================"
echo ""

# Check if Ollama is running
echo "1. Checking Ollama availability on Windows host..."
if curl -s http://10.0.2.2:11434/api/tags > /dev/null 2>&1; then
    echo "   [OK] Ollama is running on Windows (10.0.2.2:11434)"
else
    echo "   ❌ Ollama is not accessible"
    echo "   Please ensure Ollama is running on Windows"
    echo "   And that it's listening on the network (not just localhost)"
    exit 1
fi

# Check if model exists
echo ""
echo "2. Checking for llama3:8b model..."
if curl -s http://10.0.2.2:11434/api/tags | grep -q "llama3:8b"; then
    echo "   [OK] llama3:8b model found"
else
    echo "   ❌ llama3:8b model not found"
    echo "   On Windows, run: ollama pull llama3:8b"
    exit 1
fi

# Test the coordinator
echo ""
echo "3. Running AI coordinator test..."
echo "   Request: 'Add tire pressure monitoring to dashboard'"
echo ""

cd "$(dirname "$0")/.."

python3 scripts/ai-agent-coordinator.py \
    "Add tire pressure monitoring to the car dashboard" \
    "test-analysis-report.md" \
    "http://10.0.2.2:11434" \
    "llama3:8b"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "[OK] Test completed successfully!"
    echo ""
    echo "[DOC] Report generated: test-analysis-report.md"
    echo ""
    echo "Preview:"
    echo "========="
    head -20 test-analysis-report.md
else
    echo "❌ Test failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
