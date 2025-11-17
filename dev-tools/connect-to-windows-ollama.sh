#!/bin/bash

# Connect Ubuntu guest to Windows host Ollama instance

echo "🔗 Configuring Ubuntu to use Windows Ollama"
echo ""

# Get Windows host IP (typically the WSL host or VM host)
# For WSL, the host IP is in /etc/resolv.conf
# For VirtualBox/VMware, it's typically 10.0.2.2 or 192.168.x.1

echo "Detecting Windows host IP..."

# Try WSL method first
if grep -q microsoft /proc/version 2>/dev/null; then
    WINDOWS_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    echo "✅ Detected WSL environment"
    echo "   Windows host IP: $WINDOWS_IP"
else
    # For VirtualBox, the default gateway is usually the host
    WINDOWS_IP=$(ip route | grep default | awk '{print $3}')
    echo "✅ Detected VM environment"
    echo "   Default gateway (likely Windows host): $WINDOWS_IP"
fi

echo ""
echo "Testing connection to Windows Ollama at $WINDOWS_IP:11434..."

# Test if Ollama is accessible on Windows
if curl -s http://$WINDOWS_IP:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Successfully connected to Windows Ollama!"
    echo ""
    
    # Set environment variable
    export OLLAMA_HOST="http://$WINDOWS_IP:11434"
    
    # Add to current session
    echo "export OLLAMA_HOST=\"http://$WINDOWS_IP:11434\"" >> ~/.bashrc
    
    echo "✅ OLLAMA_HOST configured: http://$WINDOWS_IP:11434"
    echo ""
    echo "Available models on Windows Ollama:"
    curl -s http://$WINDOWS_IP:11434/api/tags | python3 -m json.tool 2>/dev/null || echo "(could not parse model list)"
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "To use in current terminal:"
    echo "   export OLLAMA_HOST=\"http://$WINDOWS_IP:11434\""
    echo ""
    echo "For new terminals, it's already added to ~/.bashrc"
    
else
    echo "❌ Cannot connect to Windows Ollama"
    echo ""
    echo "Please make sure:"
    echo "1. Ollama is running on Windows"
    echo "2. Windows Firewall allows connections on port 11434"
    echo "3. Ollama on Windows is configured to accept network connections"
    echo ""
    echo "To configure Ollama on Windows for network access:"
    echo "1. Set environment variable: OLLAMA_HOST=0.0.0.0:11434"
    echo "2. Restart Ollama"
    echo ""
    echo "Windows PowerShell (as Administrator):"
    echo "   [System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'Machine')"
    echo "   Restart-Service Ollama"
    echo ""
    echo "Or manually:"
    echo "   - Search for 'Environment Variables' in Windows"
    echo "   - Add OLLAMA_HOST = 0.0.0.0:11434"
    echo "   - Restart Ollama from Task Manager"
    
    exit 1
fi
