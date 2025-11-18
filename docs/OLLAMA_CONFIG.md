# Ollama Configuration for WSL/Ubuntu Guest

## Current Setup

- **Ollama Location**: Windows host (not in Ubuntu guest)
- **Ollama URL**: `http://10.0.2.2:11434`
- **Model**: `llama3:8b`

## Network Configuration

### Why 10.0.2.2?

In VirtualBox/WSL, `10.0.2.2` is the default gateway that routes to the Windows host from the guest OS.

```
Ubuntu Guest (10.0.2.15) → 10.0.2.2 → Windows Host
```

### Verify Connection

```bash
# Test Ollama connectivity
curl http://10.0.2.2:11434/api/tags

# Should return JSON with available models
```

## Available Models

From your Ollama instance:

1. **llama3:8b** ← Currently configured
2. granite4:micro-h
3. nomic-embed-text:latest
4. codellama:latest

## Configuration Files Updated

All files are now configured to use:
- Host: `http://10.0.2.2:11434` (Windows host)
- Model: `llama3:8b`

### Files:
1. `scripts/ai-agent-coordinator.py` - Default host and model
2. `Jenkinsfile.ai` - Default OLLAMA_HOST and model parameter
3. `scripts/test-ai-coordinator.sh` - Test script

## Testing

### Quick Test
```bash
cd car-demo-system
./scripts/test-ai-coordinator.sh
```

### Manual Test
```bash
python3 scripts/ai-agent-coordinator.py \
  "Add tire pressure monitoring" \
  "test-report.md" \
  "http://10.0.2.2:11434" \
  "llama3:8b"
```

## Jenkins Configuration

Jenkins will automatically use:
- `OLLAMA_HOST` environment variable: `http://10.0.2.2:11434`
- `OLLAMA_MODEL` parameter default: `llama3:8b`

You can override the model in Jenkins parameters if you want to try different models like `codellama:latest`.

## Troubleshooting

### Cannot Connect

**Symptom**: `curl http://10.0.2.2:11434/api/tags` fails

**Solutions**:
1. Ensure Ollama is running on Windows:
   ```powershell
   # In PowerShell
   ollama serve
   ```

2. Check Windows Firewall:
   - Allow Ollama through firewall
   - Port 11434 must be accessible

3. Verify Ollama is listening on network (not just localhost):
   ```powershell
   # Check Ollama settings
   # Should listen on 0.0.0.0:11434, not 127.0.0.1:11434
   ```

### Model Not Found

**Symptom**: "llama3:8b" not found

**Solution**:
```powershell
# On Windows
ollama pull llama3:8b
```

### Different Network Setup

If `10.0.2.2` doesn't work, find your Windows IP:

```powershell
# On Windows
ipconfig
# Look for "IPv4 Address" on the adapter connected to VirtualBox/WSL
```

Then update in files:
- `OLLAMA_HOST` in `Jenkinsfile.ai`
- Default host in `ai-agent-coordinator.py`
- Test script

## Performance

**llama3:8b** performance:
- Model size: ~4.7GB
- Response time: ~2-10 seconds per agent (depends on prompt complexity)
- Quality: Excellent for code analysis and structured output

### Alternative Models

Try these if you need different tradeoffs:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| llama3:8b | 4.7GB | Medium | High | Balanced (current) |
| codellama | 3.8GB | Fast | High | Code-specific |
| granite4:micro-h | 1.9GB | Very Fast | Good | Quick analysis |

To change model:
1. Pull it: `ollama pull <model>`
2. Update `OLLAMA_MODEL` in Jenkins parameter
3. Or pass as 4th argument to Python script
