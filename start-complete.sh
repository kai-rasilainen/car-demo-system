#!/bin/bash

echo "🚀 Car Demo System - Complete Startup"
echo "===================================="

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
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Detect docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Parse command line arguments
START_DATABASES_ONLY=false
START_BACKEND_ONLY=false
START_FRONTEND_ONLY=false
START_INCAR_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --databases-only)
            START_DATABASES_ONLY=true
            shift
            ;;
        --backend-only)
            START_BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            START_FRONTEND_ONLY=true
            shift
            ;;
        --incar-only)
            START_INCAR_ONLY=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --databases-only    Start only database containers"
            echo "  --backend-only      Start databases + backend services"
            echo "  --frontend-only     Start databases + frontend applications"
            echo "  --incar-only        Start databases + in-car systems"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  Start complete system (all components)"
            echo "  $0 --databases-only Start only databases (for development)"
            echo "  $0 --backend-only   Start databases and backend services"
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to check if a service is responding
check_service() {
    local url=$1
    local name=$2
    local timeout=${3:-30}
    
    print_status $BLUE "Checking $name at $url..."
    
    for i in $(seq 1 $timeout); do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_status $GREEN "✓ $name is responding"
            return 0
        fi
        sleep 1
    done
    
    print_status $YELLOW "⚠ $name is not responding (this might be normal if it's still starting)"
    return 1
}

print_status $BLUE "Starting Car Demo System..."
echo ""

# Step 1: Start databases
print_status $YELLOW "1. Starting Database Containers..."
cd "$SCRIPT_DIR"
$DOCKER_COMPOSE up -d

print_status $GREEN "✓ Database containers started"
print_status $BLUE "Waiting for databases to initialize..."
sleep 15

# Check if databases are ready
print_status $BLUE "Verifying database connections..."
docker ps --filter "name=car-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

if [ "$START_DATABASES_ONLY" = true ]; then
    print_status $GREEN "✅ Databases started successfully!"
    echo ""
    print_status $BLUE "Database URLs:"
    echo "  MongoDB:    mongodb://admin:password@localhost:27017/cardata"
    echo "  PostgreSQL: postgresql://postgres:password@localhost:5432/carinfo"
    echo "  Redis:      redis://localhost:6379"
    echo ""
    print_status $YELLOW "To start other components:"
    echo "  Backend:  cd car-demo-backend && ./scripts/dev-start.sh"
    echo "  Frontend: cd car-demo-frontend && ./scripts/dev-start.sh"
    echo "  In-car:   cd car-demo-in-car && ./scripts/start-all.sh"
    exit 0
fi

echo ""

# Step 2: Start Backend (if not frontend/incar only)
if [ "$START_FRONTEND_ONLY" != true ] && [ "$START_INCAR_ONLY" != true ]; then
    print_status $YELLOW "2. Starting Backend Services..."
    
    if [ -d "$PROJECT_ROOT/car-demo-backend" ]; then
        cd "$PROJECT_ROOT/car-demo-backend"
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_status $BLUE "Installing backend dependencies..."
            npm install
        fi
        
        # Install dependencies for all backend components
        print_status $BLUE "Installing backend component dependencies..."
        npm run install-all 2>/dev/null || {
            print_status $YELLOW "npm run install-all not available, installing manually..."
            for dir in B1-web-server B2-iot-gateway; do
                if [ -d "$dir" ]; then
                    print_status $BLUE "Installing $dir dependencies..."
                    cd "$dir" && npm install && cd ..
                fi
            done
        }
        
        # Start backend services in background
        print_status $BLUE "Starting backend services..."
        npm run dev-all > backend.log 2>&1 &
        BACKEND_PID=$!
        
        cd "$SCRIPT_DIR"
        print_status $GREEN "✓ Backend services starting (PID: $BACKEND_PID)"
        
        # Give backend time to start
        sleep 10
        
        # Check backend services
        check_service "http://localhost:3001" "B1 Web Server" 10
        check_service "http://localhost:3002" "B2 IoT Gateway" 10
    else
        print_status $YELLOW "⚠ Backend directory not found, skipping..."
    fi
fi

if [ "$START_BACKEND_ONLY" = true ]; then
    print_status $GREEN "✅ Backend services started!"
    echo ""
    print_status $BLUE "Service URLs:"
    echo "  B1 Web Server: http://localhost:3001"
    echo "  B2 IoT Gateway: http://localhost:3002"
    echo ""
    print_status $YELLOW "Backend logs: tail -f car-demo-backend/backend.log"
    exit 0
fi

echo ""

# Step 3: Start In-Car Systems (if not frontend/backend only)
if [ "$START_FRONTEND_ONLY" != true ] && [ "$START_BACKEND_ONLY" != true ]; then
    print_status $YELLOW "3. Starting In-Car Systems..."
    
    if [ -d "$PROJECT_ROOT/car-demo-in-car" ]; then
        cd "$PROJECT_ROOT/car-demo-in-car"
        
        # Activate Python environment
        if [ -d "$PROJECT_ROOT/car-demo-venv" ]; then
            source "$PROJECT_ROOT/car-demo-venv/bin/activate"
            print_status $GREEN "✓ Python virtual environment activated"
        else
            print_status $YELLOW "⚠ Python virtual environment not found"
        fi
        
        # Start C2 central broker
        if [ -d "C2-central-broker" ]; then
            print_status $BLUE "Starting C2 Central Broker..."
            cd C2-central-broker
            if [ ! -d "node_modules" ]; then
                npm install
            fi
            npm start > ../c2-broker.log 2>&1 &
            C2_PID=$!
            cd ..
            print_status $GREEN "✓ C2 Central Broker starting (PID: $C2_PID)"
        fi
        
        # Start C5 sensor simulators
        if [ -d "C5-data-sensors" ]; then
            print_status $BLUE "Starting C5 Sensor Simulators..."
            cd C5-data-sensors
            python sensor_simulator.py > ../c5-sensors.log 2>&1 &
            C5_PID=$!
            cd ..
            print_status $GREEN "✓ C5 Sensor Simulators starting (PID: $C5_PID)"
        fi
        
        # Start C1 cloud communication
        if [ -d "C1-cloud-communication" ]; then
            print_status $BLUE "Starting C1 Cloud Communication..."
            cd C1-cloud-communication
            python cloud_communicator.py > ../c1-cloud.log 2>&1 &
            C1_PID=$!
            cd ..
            print_status $GREEN "✓ C1 Cloud Communication starting (PID: $C1_PID)"
        fi
        
        cd "$SCRIPT_DIR"
        
        # Give in-car systems time to start
        sleep 5
        
        # Check in-car services
        check_service "http://localhost:3003" "C2 Central Broker" 10
    else
        print_status $YELLOW "⚠ In-car directory not found, skipping..."
    fi
fi

if [ "$START_INCAR_ONLY" = true ]; then
    print_status $GREEN "✅ In-Car systems started!"
    echo ""
    print_status $BLUE "Service URLs:"
    echo "  C2 Central Broker: http://localhost:3003"
    echo ""
    print_status $YELLOW "In-car logs:"
    echo "  C2 Broker: tail -f car-demo-in-car/c2-broker.log"
    echo "  C5 Sensors: tail -f car-demo-in-car/c5-sensors.log"
    echo "  C1 Cloud: tail -f car-demo-in-car/c1-cloud.log"
    exit 0
fi

echo ""

# Step 4: Start Frontend
if [ "$START_BACKEND_ONLY" != true ] && [ "$START_INCAR_ONLY" != true ]; then
    print_status $YELLOW "4. Starting Frontend Applications..."
    
    if [ -d "$PROJECT_ROOT/car-demo-frontend" ]; then
        cd "$PROJECT_ROOT/car-demo-frontend"
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_status $BLUE "Installing frontend dependencies..."
            npm install
        fi
        
        # Start frontend applications
        print_status $BLUE "Starting frontend applications..."
        npm run dev-all > frontend.log 2>&1 &
        FRONTEND_PID=$!
        
        cd "$SCRIPT_DIR"
        print_status $GREEN "✓ Frontend applications starting (PID: $FRONTEND_PID)"
        
        # Give frontend time to start
        sleep 10
        
        # Check frontend services
        check_service "http://localhost:3000" "A2 Web App" 10
        # Note: A1 Mobile (Expo) typically runs on port 19006 but may vary
    else
        print_status $YELLOW "⚠ Frontend directory not found, skipping..."
    fi
fi

echo ""
print_status $GREEN "🎉 Car Demo System Startup Complete!"
echo ""

print_status $BLUE "🌐 Service URLs:"
echo "  📱 A1 Mobile App:    http://localhost:19006 (Expo - may vary)"
echo "  🌐 A2 Web App:       http://localhost:3000"
echo "  🔧 B1 Web Server:    http://localhost:3001"
echo "  🚗 B2 IoT Gateway:   http://localhost:3002"
echo "  📡 C2 Central Broker: http://localhost:3003"
echo ""

print_status $BLUE "💾 Database URLs:"
echo "  🍃 MongoDB:    mongodb://admin:password@localhost:27017/cardata"
echo "  🐘 PostgreSQL: postgresql://postgres:password@localhost:5432/carinfo"
echo "  🔴 Redis:      redis://localhost:6379"
echo ""

print_status $BLUE "📋 Logs:"
if [ -f "$PROJECT_ROOT/car-demo-backend/backend.log" ]; then
    echo "  Backend:  tail -f car-demo-backend/backend.log"
fi
if [ -f "$PROJECT_ROOT/car-demo-frontend/frontend.log" ]; then
    echo "  Frontend: tail -f car-demo-frontend/frontend.log"
fi
if [ -f "$PROJECT_ROOT/car-demo-in-car/c2-broker.log" ]; then
    echo "  C2 Broker: tail -f car-demo-in-car/c2-broker.log"
fi
if [ -f "$PROJECT_ROOT/car-demo-in-car/c5-sensors.log" ]; then
    echo "  C5 Sensors: tail -f car-demo-in-car/c5-sensors.log"
fi
if [ -f "$PROJECT_ROOT/car-demo-in-car/c1-cloud.log" ]; then
    echo "  C1 Cloud: tail -f car-demo-in-car/c1-cloud.log"
fi

echo ""
print_status $YELLOW "🛑 To stop everything: ./stop-all.sh"
print_status $BLUE "📊 To run tests: ./run-tests.sh --all"