# AI Agent System - Quick Reference

## Architecture
```
User Request
     ↓
Agent A (analyzes with AI)
     ↓
  Needs B? -YES→ Agent B (analyzes with AI)
     |              ↓
     |          Needs C? -YES→ Agent C (analyzes with AI)
     |
     `-- Needs C directly? -YES→ Agent C (analyzes with AI)
```

## Commands

### Start Ollama
```bash
ollama serve
```

### Pull Model
```bash
ollama pull llama2
# or
ollama pull codellama
```

### Test AI Coordinator
```bash
cd car-demo-system
./scripts/test-ai-orchestrator.sh
```

### Run Manually
```bash
python3 scripts/ai-agent-orchestrator.py \
  "Add tire pressure monitoring" \
  "report.md" \
  "http://localhost:11434"
```

### Switch Jenkinsfile
```bash
# Backup current
cp Jenkinsfile Jenkinsfile.backup

# Use AI version
cp Jenkinsfile.ai Jenkinsfile
```

## Jenkins Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| FEATURE_REQUEST | "Add tire pressure..." | Feature description |
| USE_AI_AGENTS | true | Use AI (vs manual) |
| OLLAMA_MODEL | llama2 | Model to use |
| OUTPUT_FILE | ai-feature-analysis.md | Output filename |

## Files

| File | Purpose |
|------|---------|
| `scripts/ai-agent-orchestrator.py` | AI orchestration engine |
| `Jenkinsfile.ai` | New AI-driven pipeline |
| `Jenkinsfile.backup` | Original pipeline |
| `AI_AGENT_SYSTEM.md` | Full docs |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details |

## Agents

| Agent | Role | Decides |
|-------|------|---------|
| Agent A | Frontend & Coordinator | needs_agent_b, needs_agent_c |
| Agent B | Backend | needs_agent_c |
| Agent C | In-Car Systems | - |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect to Ollama | Start: `ollama serve` |
| Model not found | Pull: `ollama pull llama2` |
| Timeout | Increase timeout in .py |
| Bad JSON from AI | Use codellama model |
| No AI available | Set USE_AI_AGENTS=false |

## Output

### Success
```
analysis-reports/
|--- ai-feature-analysis.md       # Main report
|--- agent-log.txt                 # Execution log
|--- implementation-plan.md        # Step-by-step plan (generated)
`--- component-tasks/              # Per-component task files
     |--- task-A1.md
     |--- task-A2.md
     |--- task-B1.md
     |--- task-B2.md
     |--- task-B3.md
     |--- task-B4.md
     |--- task-C1.md
     |--- task-C2.md
     `--- task-C5.md
```

### Per-Component Task Files

After analysis, Jenkins generates **one task file per component** (A1, A2, B1-B4, C1, C2, C5).  
Each file includes:
- Excerpt from the analysis relevant to that component
- Suggested subtasks (interface changes, tests, deployment notes)
- Effort estimate placeholder
- Dependency notes

**Purpose**: Break down the feature into small, focused tasks for each component.  
Developers (or future automation) can turn these into GitHub issues or PRs.

**Example workflow**:
1. Jenkins runs AI analysis -> generates `ai-feature-analysis.md`
2. Jenkins runs `create-component-tasks.py` -> generates 9 task files
3. Developer reviews `component-tasks/task-B1.md` for backend API changes
4. Developer creates GitHub issue from the task file
5. Developer implements small PR for B1 component only

### Report Structure
```markdown
# AI-Driven Feature Analysis Report
- Feature Request
- Agents Involved  
- Total Effort

## Agent A Analysis
- Impact
- Components
- Changes
- Effort
- Risks

## Agent B Analysis (if needed)
...

## Agent C Analysis (if needed)
...
```

## Quick Start
```bash
# 1. Start Ollama
ollama serve

# 2. Test
./scripts/test-ai-orchestrator.sh

# 3. Deploy
cp Jenkinsfile.ai Jenkinsfile
git commit -am "AI agent system"
git push

# 4. Run in Jenkins
```

## Model Recommendations

| Model | Best For | Speed |
|-------|----------|-------|
| llama2 | General | Fast |
| codellama | Code analysis | Fast |
| deepseek-coder | Detailed code | Medium |
| mistral | Balanced | Fast |
| mixtral | Complex | Slow |

## Example Request

**Input**: "Add tire pressure monitoring to the car dashboard"

**Output**: 
- Agent A: Analyzes frontend (mobile + web)
- Agent A decides: needs backend (Agent B)
- Agent B: Analyzes backend (API, WebSocket, DB)
- Agent B decides: needs in-car data (Agent C)
- Agent C: Analyzes sensors and data flow
- Report: Combined analysis with 24hr effort estimate

## URLs

- **Ollama API**: http://localhost:11434
- **From Jenkins**: http://10.0.2.2:11434
- **Test tags**: `curl http://localhost:11434/api/tags`
- **Check model**: `ollama list`
