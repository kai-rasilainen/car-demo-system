#!/bin/bash

echo "🛑 Car Demo System - Stop All Containers"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Function to stop containers in a directory
stop_containers() {
    local dir=$1
    local desc=$2
    
    if [ -f "$dir/docker-compose.yml" ]; then
        print_status $BLUE "Stopping $desc containers..."
        cd "$dir"
        $DOCKER_COMPOSE down
        cd "$SCRIPT_DIR"
        print_status $GREEN "✓ $desc containers stopped"
    else
        print_status $YELLOW "⚠ No docker-compose.yml found in $dir"
    fi
}

# Parse command line arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --volumes|-v)
            REMOVE_VOLUMES=true
            shift
            ;;
        --images|-i)
            REMOVE_IMAGES=true
            shift
            ;;
        --all|-a)
            REMOVE_VOLUMES=true
            REMOVE_IMAGES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Stops all Car Demo System processes and containers"
            echo ""
            echo "Options:"
            echo "  --volumes, -v    Also remove volumes (deletes all data)"
            echo "  --images, -i     Also remove images (saves disk space)"
            echo "  --all, -a        Remove volumes and images"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "What it stops:"
            echo "  - npm dev processes"
            echo "  - Node.js server processes"
            echo "  - Python sensor and cloud processes"
            echo "  - Docker containers (MongoDB, PostgreSQL, Redis)"
            echo ""
            echo "Examples:"
            echo "  $0               Stop all processes and containers"
            echo "  $0 --volumes     Stop containers and remove volumes"
            echo "  $0 --all         Stop everything and clean up completely"
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_status $YELLOW "Stopping all Car Demo System containers..."
echo ""

# Stop Node.js and Python processes first
print_status $BLUE "Stopping Node.js and Python processes..."

# Kill npm processes (all npm processes including start, dev, test, etc.)
NPM_PIDS=$(pgrep -f "npm" 2>/dev/null)
if [ -n "$NPM_PIDS" ]; then
    pkill -f "npm" 2>/dev/null
    print_status $GREEN "✓ npm processes stopped (PIDs: $NPM_PIDS)"
fi

# Kill node processes related to car-demo
NODE_PIDS=$(pgrep -f "node.*server.js" 2>/dev/null)
if [ -n "$NODE_PIDS" ]; then
    pkill -f "node.*server.js" 2>/dev/null
    print_status $GREEN "✓ Node.js server processes stopped (PIDs: $NODE_PIDS)"
fi

# Kill Python processes related to car-demo
SENSOR_PIDS=$(pgrep -f "python.*sensor_simulator.py" 2>/dev/null)
if [ -n "$SENSOR_PIDS" ]; then
    pkill -f "python.*sensor_simulator.py" 2>/dev/null
    print_status $GREEN "✓ Sensor simulator processes stopped (PIDs: $SENSOR_PIDS)"
fi

CLOUD_PIDS=$(pgrep -f "python.*cloud_communicator.py" 2>/dev/null)
if [ -n "$CLOUD_PIDS" ]; then
    pkill -f "python.*cloud_communicator.py" 2>/dev/null
    print_status $GREEN "✓ Cloud communicator processes stopped (PIDs: $CLOUD_PIDS)"
fi

# Check if any processes were stopped
if [ -z "$NPM_PIDS" ] && [ -z "$NODE_PIDS" ] && [ -z "$SENSOR_PIDS" ] && [ -z "$CLOUD_PIDS" ]; then
    print_status $YELLOW "⚠ No running processes found"
fi

echo ""

# Stop main system containers
cd "$SCRIPT_DIR"
if [ -f "docker-compose.yml" ]; then
    print_status $BLUE "Stopping main system containers..."
    if [ "$REMOVE_VOLUMES" = true ]; then
        $DOCKER_COMPOSE down -v
        print_status $YELLOW "🗑️ Volumes removed (all database data deleted)"
    else
        $DOCKER_COMPOSE down
    fi
    print_status $GREEN "✓ Main system containers stopped"
else
    print_status $YELLOW "⚠ No main docker-compose.yml found"
fi

echo ""
print_status $BLUE "Checking for individual component containers..."

# Check and stop individual components
# Note: These may not exist depending on setup
if [ -d "car-demo-backend" ]; then
    stop_containers "car-demo-backend" "Backend"
    stop_containers "car-demo-backend/B3-realtime-database" "MongoDB"
    stop_containers "car-demo-backend/B4-static-database" "PostgreSQL"
fi

if [ -d "car-demo-in-car" ]; then
    stop_containers "car-demo-in-car" "In-car"
    stop_containers "car-demo-in-car/C2-central-broker" "Redis"
fi

# Also check parent directory structure
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -d "$PARENT_DIR/car-demo-backend" ]; then
    stop_containers "$PARENT_DIR/car-demo-backend" "Backend (parent dir)"
    stop_containers "$PARENT_DIR/car-demo-backend/B3-realtime-database" "MongoDB (parent dir)"
    stop_containers "$PARENT_DIR/car-demo-backend/B4-static-database" "PostgreSQL (parent dir)"
fi

if [ -d "$PARENT_DIR/car-demo-in-car" ]; then
    stop_containers "$PARENT_DIR/car-demo-in-car" "In-car (parent dir)"
    stop_containers "$PARENT_DIR/car-demo-in-car/C2-central-broker" "Redis (parent dir)"
fi

# Remove car-demo specific containers by name (fallback)
print_status $BLUE "Removing any remaining car-demo containers..."
docker rm -f car-data-mongodb car-info-postgres car-central-broker 2>/dev/null || true

# Remove images if requested
if [ "$REMOVE_IMAGES" = true ]; then
    print_status $YELLOW "🗑️ Removing Docker images..."
    docker rmi mongo:4.4 postgres:15 redis:7-alpine 2>/dev/null || true
    print_status $GREEN "✓ Images removed"
fi

# Clean up orphaned containers and networks
print_status $BLUE "Cleaning up orphaned resources..."
docker container prune -f >/dev/null 2>&1 || true
docker network prune -f >/dev/null 2>&1 || true

echo ""
print_status $GREEN "✅ All Car Demo System containers stopped!"

# Show final status
echo ""
print_status $BLUE "Current Docker status:"
echo ""
REMAINING=$(docker ps -a --filter "name=car-" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
if [ -n "$REMAINING" ]; then
    echo "$REMAINING"
else
    print_status $GREEN "✓ No car-demo containers remaining"
fi

echo ""
if [ "$REMOVE_VOLUMES" = true ]; then
    print_status $YELLOW "⚠️ Note: All database data has been deleted!"
    print_status $YELLOW "   Next startup will create fresh databases."
else
    print_status $GREEN "💾 Database volumes preserved."
    print_status $GREEN "   Data will be available on next startup."
fi