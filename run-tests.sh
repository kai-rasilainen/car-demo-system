#!/bin/bash

echo "🧪 Car Demo System - Test Suite Runner"
echo "======================================"

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

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        print_status $GREEN "✓ $name is running"
        return 0
    else
        print_status $RED "✗ $name is not running"
        return 1
    fi
}

# Function to start service if not running
ensure_service_running() {
    local url=$1
    local name=$2
    local start_command=$3
    
    if ! check_service "$url" "$name"; then
        print_status $YELLOW "Starting $name..."
        eval "$start_command" &
        
        # Wait for service to start
        local retries=0
        while [ $retries -lt 30 ]; do
            if check_service "$url" "$name"; then
                break
            fi
            sleep 2
            retries=$((retries + 1))
        done
        
        if [ $retries -eq 30 ]; then
            print_status $RED "Failed to start $name"
            return 1
        fi
    fi
    return 0
}

# Parse command line arguments
UNIT_TESTS=false
INTEGRATION_TESTS=false
E2E_TESTS=false
COVERAGE=false
WATCH=false
COMPONENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            UNIT_TESTS=true
            shift
            ;;
        --integration)
            INTEGRATION_TESTS=true
            shift
            ;;
        --e2e)
            E2E_TESTS=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        --component)
            COMPONENT="$2"
            shift 2
            ;;
        --all)
            UNIT_TESTS=true
            INTEGRATION_TESTS=true
            E2E_TESTS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit          Run unit tests"
            echo "  --integration   Run integration tests"
            echo "  --e2e           Run end-to-end tests"
            echo "  --coverage      Generate coverage report"
            echo "  --watch         Run tests in watch mode"
            echo "  --component     Run tests for specific component (b1|b2|c2)"
            echo "  --all           Run all test types"
            echo "  --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --unit --coverage"
            echo "  $0 --component b1"
            echo "  $0 --e2e"
            echo "  $0 --all"
            exit 0
            ;;
        *)
            print_status $RED "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Default to unit tests if no test type specified
if [ "$UNIT_TESTS" = false ] && [ "$INTEGRATION_TESTS" = false ] && [ "$E2E_TESTS" = false ]; then
    UNIT_TESTS=true
fi

print_status $BLUE "Test Configuration:"
echo "  Unit Tests: $UNIT_TESTS"
echo "  Integration Tests: $INTEGRATION_TESTS"
echo "  E2E Tests: $E2E_TESTS"
echo "  Coverage: $COVERAGE"
echo "  Watch Mode: $WATCH"
echo "  Component: ${COMPONENT:-'all'}"
echo ""

# Check prerequisites
print_status $YELLOW "1. Checking Prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_status $RED "Node.js is not installed"
    exit 1
fi
print_status $GREEN "✓ Node.js: $(node --version)"

# Check Python (for Python tests)
if ! command -v python3 &> /dev/null; then
    print_status $RED "Python3 is not installed"
    exit 1
fi
print_status $GREEN "✓ Python: $(python3 --version)"

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    print_status $RED "Redis is not installed"
    exit 1
fi

# Start Redis if not running
if ! redis-cli ping > /dev/null 2>&1; then
    print_status $YELLOW "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

if redis-cli ping > /dev/null 2>&1; then
    print_status $GREEN "✓ Redis is running"
else
    print_status $RED "✗ Failed to start Redis"
    exit 1
fi

# Install dependencies if needed
print_status $YELLOW "2. Installing Dependencies..."

cd /home/kai/projects/car-demo-repos/car-demo-backend
if [ ! -d "node_modules" ]; then
    print_status $YELLOW "Installing Node.js dependencies..."
    npm install
fi

# Install Python dependencies
if [ -d "/home/kai/projects/car-demo-repos/car-demo-venv" ]; then
    print_status $GREEN "✓ Python virtual environment exists"
    source /home/kai/projects/car-demo-repos/car-demo-venv/bin/activate
else
    print_status $YELLOW "Creating Python virtual environment..."
    cd /home/kai/projects/car-demo-repos
    python3 -m venv car-demo-venv
    source car-demo-venv/bin/activate
    pip install pytest pytest-asyncio pytest-mock fakeredis
fi

# Run tests based on configuration
print_status $YELLOW "3. Running Tests..."
cd /home/kai/projects/car-demo-repos/car-demo-backend

# Build Jest command
JEST_CMD="npx jest"
if [ "$COVERAGE" = true ]; then
    JEST_CMD="$JEST_CMD --coverage"
fi
if [ "$WATCH" = true ]; then
    JEST_CMD="$JEST_CMD --watch"
fi

# Component-specific tests
if [ -n "$COMPONENT" ]; then
    case $COMPONENT in
        b1)
            print_status $BLUE "Running B1 Web Server tests..."
            $JEST_CMD --testPathPattern=B1-web-server/tests
            ;;
        b2)
            print_status $BLUE "Running B2 IoT Gateway tests..."
            $JEST_CMD --testPathPattern=B2-iot-gateway/tests
            ;;
        c2)
            print_status $BLUE "Running C2 Central Broker tests..."
            cd /home/kai/projects/car-demo-repos/car-demo-system/car-demo-in-car/C2-central-broker
            $JEST_CMD --testPathPattern=tests
            ;;
        *)
            print_status $RED "Unknown component: $COMPONENT"
            exit 1
            ;;
    esac
else
    # Run selected test types
    if [ "$UNIT_TESTS" = true ]; then
        print_status $BLUE "Running Unit Tests..."
        
        # Node.js unit tests
        $JEST_CMD --testPathPattern=tests --testNamePattern='(?!.*integration)'
        
        # Python unit tests
        print_status $BLUE "Running Python Unit Tests..."
        cd /home/kai/projects/car-demo-repos
        source car-demo-venv/bin/activate
        
        # Run C1 tests
        if [ -f "car-demo-system/car-demo-in-car/C1-cloud-communication/tests/test_cloud_communication.py" ]; then
            cd car-demo-system/car-demo-in-car/C1-cloud-communication
            python -m pytest tests/ -v
            cd ../../../..
        fi
        
        # Run C5 tests
        if [ -f "car-demo-system/car-demo-in-car/C5-data-sensors/tests/test_sensor_simulator.py" ]; then
            cd car-demo-system/car-demo-in-car/C5-data-sensors
            python -m pytest tests/ -v
            cd ../../../..
        fi
    fi
    
    if [ "$E2E_TESTS" = true ]; then
        print_status $BLUE "Running End-to-End Tests..."
        
        # Ensure services are running for E2E tests
        print_status $YELLOW "Ensuring services are running for E2E tests..."
        
        # Note: In a real scenario, you'd start the services here
        print_status $YELLOW "Please ensure the following services are running:"
        echo "  - B1 Web Server (port 3001)"
        echo "  - B2 IoT Gateway (port 3002)" 
        echo "  - C2 Central Broker (port 3003)"
        echo ""
        print_status $YELLOW "Press Enter to continue with E2E tests, or Ctrl+C to cancel"
        read
        
        cd /home/kai/projects/car-demo-repos
        npx jest tests/e2e/ --runInBand --detectOpenHandles
    fi
fi

print_status $GREEN "✅ Test execution completed!"

# Generate test report summary
if [ "$COVERAGE" = true ]; then
    print_status $BLUE "Coverage report generated in coverage/ directory"
fi

print_status $YELLOW "Test Summary:"
echo "  Check the output above for detailed results"
echo "  Use --coverage flag to generate coverage reports"
echo "  Use --watch flag for continuous testing during development"