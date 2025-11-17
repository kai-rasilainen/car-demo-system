# Using Windows Ollama from Ubuntu Guest

This guide shows how to use Ollama installed on Windows from your Ubuntu guest/VM.

## Prerequisites

1. ✅ Ollama installed on Windows
2. ✅ Windows and Ubuntu can communicate (same network or WSL/VM setup)

## Step 1: Configure Windows Ollama for Network Access

By default, Ollama only accepts connections from localhost. You need to configure it to accept network connections.

### Option A: PowerShell (Administrator)

```powershell
# Set environment variable to allow network access
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')

# Restart Ollama service
Stop-Process -Name "ollama" -Force
# Ollama will restart automatically, or start it manually
```

### Option B: Manual Configuration

1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "System variables", click "New"
   - Variable name: `OLLAMA_HOST`
   - Variable value: `0.0.0.0:11434`
4. Click OK
5. Restart Ollama:
   - Open Task Manager (Ctrl+Shift+Esc)
   - Find "Ollama" process
   - Right-click → End task
   - Ollama will restart automatically

### Step 2: Configure Windows Firewall

Allow incoming connections on port 11434:

```powershell
# PowerShell (Administrator)
New-NetFirewallRule -DisplayName "Ollama Server" -Direction Inbound -LocalPort 11434 -Protocol TCP -Action Allow
```

Or manually:
1. Windows Security → Firewall & network protection
2. Advanced settings → Inbound Rules → New Rule
3. Port → TCP → Specific local ports: 11434
4. Allow the connection
5. Apply to all profiles

## Step 3: Connect Ubuntu to Windows Ollama

Run the connection script:

```bash
cd /home/kai/projects/car-demo-repos/car-demo-system
./dev-tools/connect-to-windows-ollama.sh
```

This script will:
- Auto-detect your Windows host IP
- Test the connection
- Configure `OLLAMA_HOST` environment variable
- Add it to your `~/.bashrc` for persistence

### Manual Connection (if script doesn't work)

1. Find your Windows IP:
   ```bash
   # WSL
   grep nameserver /etc/resolv.conf | awk '{print $2}'
   
   # VirtualBox/VMware
   ip route | grep default | awk '{print $3}'
   ```

2. Set the environment variable:
   ```bash
   export OLLAMA_HOST="http://YOUR_WINDOWS_IP:11434"
   
   # Add to .bashrc for persistence
   echo 'export OLLAMA_HOST="http://YOUR_WINDOWS_IP:11434"' >> ~/.bashrc
   ```

3. Test the connection:
   ```bash
   ollama list
   ```

## Step 4: Verify Setup

```bash
# Check available models on Windows
ollama list

# Test with a simple prompt
ollama run llama3:8b "Hello, this is a test from Ubuntu!"
```

## Using with Dev Tools

Once connected, the dev tools will automatically use Windows Ollama:

```bash
# These will now use Windows Ollama
python3 dev-tools/ollama-dev-assistant.py analyze file.js
python3 dev-tools/ollama-dev-assistant.py document file.py
```

## Troubleshooting

### "Connection refused"

Check Windows Ollama is running:
```powershell
# Windows PowerShell
Get-Process ollama
```

If not running, start it:
```powershell
ollama serve
```

### "Cannot connect" 

1. Verify Windows IP:
   ```bash
   ping YOUR_WINDOWS_IP
   ```

2. Test Ollama port:
   ```bash
   curl http://YOUR_WINDOWS_IP:11434/api/tags
   ```

3. Check Windows firewall is allowing port 11434

4. Verify OLLAMA_HOST on Windows:
   ```powershell
   [System.Environment]::GetEnvironmentVariable('OLLAMA_HOST', 'Machine')
   # Should show: 0.0.0.0:11434
   ```

### Models not showing

Pull models on Windows first:
```powershell
# Windows
ollama pull llama3:8b
```

Then check from Ubuntu:
```bash
ollama list
```

## Benefits of Using Windows Ollama

- ✅ Better GPU support (if you have NVIDIA GPU on Windows)
- ✅ No need to download models twice
- ✅ Saves disk space on Ubuntu
- ✅ Better performance if Windows has more RAM/CPU

## Switching Back to Local Ubuntu Ollama

If you want to use local Ollama again:

```bash
# Remove the environment variable
unset OLLAMA_HOST

# Remove from .bashrc
sed -i '/OLLAMA_HOST/d' ~/.bashrc
```

## Network Configuration Reference

### Common Windows Host IPs

| Environment | Typical IP | How to Find |
|------------|------------|-------------|
| WSL 2 | Dynamic | `grep nameserver /etc/resolv.conf` |
| VirtualBox NAT | `10.0.2.2` | Default gateway |
| VirtualBox Bridged | `192.168.x.x` | `ip route` |
| VMware NAT | `192.168.x.1` | Default gateway |
| Hyper-V | `172.x.x.1` | Default gateway |

### Ollama Default Ports

- Default: `11434`
- API endpoint: `http://IP:11434/api/`
- Tags endpoint: `http://IP:11434/api/tags`
