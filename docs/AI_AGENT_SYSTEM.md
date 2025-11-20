# AI-Driven Multi-Agent Coordination System

## Overview

This system uses **AI (Ollama)** to dynamically coordinate multiple agents for feature analysis. Unlike the previous hardcoded approach, agents now use AI to:

1. **Analyze feature requests intelligently**
2. **Determine dependencies dynamically** 
3. **Coordinate with other agents as needed**
4. **Generate analysis without hardcoded templates**

## Architecture

```
User Request
     ↓
Agent A (Frontend & Coordinator)
     ↓ (AI decides)
     ├─→ Agent B needed? → Agent B (Backend)
     │                          ↓ (AI decides)
     │                          └─→ Agent C needed? → Agent C (In-Car)
     │
     └─→ Agent C needed directly? → Agent C (In-Car)
```

### Agent Responsibilities

**Agent A - Frontend & Coordinator**
- React Native mobile app (A1)
- React web staff app (A2)
- User interface design
- API integration
- **Coordinates all other agents**

**Agent B - Backend**
- REST API server (B1)
- IoT Gateway (B2)  
- MongoDB database (B3)
- PostgreSQL database (B4)
- WebSocket communications

**Agent C - In-Car Systems**
- Cloud communication (C1)
- Redis message broker (C2)
- CAN bus interface (C3)
- Vehicle controller (C4)
- Data sensors (C5)

## How It Works

### 1. AI-Driven Analysis

Each agent uses Ollama to analyze the feature request with context about:
- Their responsibilities
- System architecture
- Previous agent analyses (if any)

### 2. Dynamic Dependency Detection

Agents use AI to determine:
- `needs_agent_b`: Does this feature require backend changes?
- `needs_agent_c`: Does this feature require in-car system changes?

### 3. Cascading Coordination

```python
Agent A analyzes → determines needs_agent_b=true
  ↓
Agent B analyzes → determines needs_agent_c=true
  ↓
Agent C analyzes → provides in-car analysis
```

### 4. Report Generation

The system generates a comprehensive markdown report with:
- Impact analysis from each involved agent
- Component changes required
- Effort estimates
- Risks and challenges
- Total effort calculation

## Setup

### Prerequisites

1. **Ollama Running**
   ```bash
   # On host machine
   ollama serve
   
   # Pull a model
   ollama pull llama2
   # or
   ollama pull codellama
   ollama pull deepseek-coder
   ```

2. **Python 3 with requests**
   ```bash
   pip install requests
   ```

3. **Network Access**
   - Jenkins must be able to reach Ollama at `http://10.0.2.2:11434`
   - Adjust `OLLAMA_HOST` in Jenkinsfile if needed

## Usage

### Jenkins Pipeline

1. **Use New AI-Driven Jenkinsfile**
   ```bash
   # Replace old Jenkinsfile
   cp Jenkinsfile.ai Jenkinsfile
   
   # Or keep both and point Jenkins to Jenkinsfile.ai
   ```

2. **Configure Jenkins Pipeline**
   - Pipeline script from SCM
   - Point to `Jenkinsfile.ai` (or renamed `Jenkinsfile`)

3. **Run with Parameters**
   - `FEATURE_REQUEST`: Your feature description
   - `USE_AI_COORDINATION`: `true` (use AI) or `false` (fallback)
   - `OLLAMA_MODEL`: Model to use (llama2, codellama, etc.)
   - `OUTPUT_FILE`: Output filename

### Command Line (Direct)

```bash
cd car-demo-system

python3 scripts/ai-agent-coordinator.py \
  "Add tire pressure monitoring to dashboard" \
  "analysis-report.md" \
  "http://localhost:11434"
```

### Example Output

```
🤖 Starting AI-driven analysis for: Add tire pressure monitoring to dashboard
📊 Agent A: Analyzing request and determining dependencies...
📊 Agent B: Backend analysis needed...
📊 Agent C: In-car system analysis needed...

✅ Analysis complete. Report saved to: analysis-report.md
```

## Benefits

### vs Hardcoded Approach

| Feature | Hardcoded | AI-Driven |
|---------|-----------|-----------|
| Flexibility | Fixed templates | Dynamic analysis |
| Context Awareness | Limited | Full context |
| Dependency Detection | Manual | Automatic |
| Accuracy | Generic | Feature-specific |
| Maintenance | High effort | Self-adapting |

### Key Advantages

1. **No hardcoded templates** - Every analysis is unique
2. **Smart coordination** - Only involves agents that are truly needed
3. **Context-aware** - Each agent sees previous analyses
4. **Scalable** - Easy to add new agents or responsibilities
5. **Self-improving** - Better models = better analysis

## Configuration

### Ollama Host

Edit in Jenkinsfile:
```groovy
environment {
    OLLAMA_HOST = 'http://10.0.2.2:11434'  // Change as needed
}
```

Or pass as parameter to Python script:
```bash
python3 scripts/ai-agent-coordinator.py "request" "output.md" "http://your-host:11434"
```

### AI Model Selection

Choose models based on your needs:

- **llama2**: Good general purpose, fast
- **codellama**: Specialized for code analysis  
- **deepseek-coder**: Excellent for detailed code understanding
- **mistral**: Fast and accurate
- **mixtral**: More capable, slower

Edit `OLLAMA_MODEL` parameter in Jenkins or:

```python
# In ai-agent-coordinator.py
class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.model = "codellama"  # Change here
```

## Troubleshooting

### Ollama Not Available

```
❌ Cannot connect to Ollama at http://10.0.2.2:11434
```

**Solutions:**
1. Start Ollama: `ollama serve`
2. Check firewall/network
3. Verify host address
4. Test: `curl http://10.0.2.2:11434/api/tags`

### Model Not Found

```
⚠️ Model may need to be pulled first
```

**Solution:**
```bash
ollama pull llama2
```

### JSON Parsing Errors

If AI response isn't valid JSON:
- The system falls back to default analysis structure
- Try a different model (codellama is better with structured output)
- Check Ollama logs

### Timeout Issues

Large models may timeout:
```python
# Increase timeout in ai-agent-coordinator.py
response = requests.post(url, json=payload, timeout=300)  # 5 minutes
```

## Extending the System

### Add New Agent

```python
# In ai-agent-coordinator.py
self.agent_d = Agent(
    name="Agent D",
    role="Your Role",
    responsibilities=[
        "Responsibility 1",
        "Responsibility 2"
    ],
    ollama=self.ollama
)
```

### Add New Analysis Fields

```python
# In Agent.analyze() system_prompt
"""
...
Respond in JSON format with these keys:
- impact: string
- components: list
- changes: list
- needs_agent_b: boolean
- needs_agent_c: boolean
- effort_hours: number
- risks: list
- security_concerns: list  # NEW
- performance_impact: string  # NEW
"""
```

### Customize Prompts

Edit the `system_prompt` and `prompt` in `Agent.analyze()` method to guide AI behavior.

## Files

```
car-demo-system/
├── Jenkinsfile.ai              # New AI-driven pipeline
├── Jenkinsfile.backup          # Old hardcoded pipeline  
├── scripts/
│   └── ai-agent-coordinator.py # AI coordination logic
└── AI_AGENT_SYSTEM.md          # This file
```

## Comparison: Old vs New

### Old Approach (Jenkinsfile.backup)
```groovy
stage('Agent A') {
    def hardcodedReport = """
    # Hardcoded analysis
    - Change component X
    - Add feature Y
    """
}
```

### New Approach (Jenkinsfile.ai)
```groovy
stage('AI Agent Coordination') {
    sh "python3 scripts/ai-agent-coordinator.py ..."
    // AI generates analysis dynamically
}
```

## Next Steps

1. **Test the system**
   ```bash
   # Start Ollama
   ollama serve
   ollama pull llama2
   
   # Test coordinator directly
   python3 scripts/ai-agent-coordinator.py \
     "Add battery status display" \
     "test-report.md"
   ```

2. **Update Jenkins**
   - Backup current pipeline
   - Switch to Jenkinsfile.ai
   - Configure parameters
   - Run test build

3. **Iterate and improve**
   - Adjust prompts for better results
   - Try different models
   - Add more agents as needed

## Support

For issues or questions:
1. Check Ollama logs
2. Verify network connectivity
3. Test with simpler requests first
4. Review generated JSON in coordination-log.txt
