#!/bin/bash
set -e

echo "Setting up complete car demo system..."

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Clone all repositories if not present
repos=("A-A-car-demo-frontend" "B-B-car-demo-backend" "C-C-car-demo-in-car")
base_url="https://github.com/kai-rasilainen"

for repo in "${repos[@]}"; do
    if [ ! -d "$repo" ]; then
        echo "Cloning $repo..."
        git clone "$base_url/$repo.git"
    else
        echo "$repo already exists, pulling latest..."
        cd "$repo" && git pull && cd ..
    fi
done

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYSTEM_DIR="$(dirname "$SCRIPT_DIR")"
IN_CAR_DIR="$SYSTEM_DIR/C-C-car-demo-in-car"
VENV_DIR="$IN_CAR_DIR/venv"

# Create and configure Python virtual environment for C-car-demo-in-car
if [ -d "$IN_CAR_DIR" ]; then
    echo "Setting up Python virtual environment for in-car components..."
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        cd "$IN_CAR_DIR"
        python3 -m venv venv
        
        echo "Upgrading pip..."
        source venv/bin/activate
        pip install --upgrade pip
        
        echo "Installing dependencies..."
        pip install pytest pytest-asyncio pytest-mock fakeredis
        
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        if [ -f "C1-requirements.txt" ]; then
            pip install -r C1-requirements.txt
        fi
        if [ -f "C5-requirements.txt" ]; then
            pip install -r C5-requirements.txt
        fi
        
        deactivate
        echo "Python virtual environment created at: $VENV_DIR"
    else
        echo "Virtual environment already exists at: $VENV_DIR"
    fi
    
    cd "$SYSTEM_DIR"
fi

# Start all databases
echo "Starting databases..."
$DOCKER_COMPOSE up -d

echo "Setup complete!"
