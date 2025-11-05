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
repos=("car-demo-frontend" "car-demo-backend" "car-demo-in-car")
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

# Start all databases
echo "Starting databases..."
$DOCKER_COMPOSE up -d

echo "Setup complete!"
