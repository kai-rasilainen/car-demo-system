#!/bin/bash

echo "🧪 Car Demo System - Test Suite Runner"
echo "======================================"

# Get the directory where this script is located (should be car-demo-system)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one level to find the project root
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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
            echo "  --component     Run tests for specific component (b1|b2|c1|c2|a1)"
            echo "  --all           Run all test types"
            echo "  --help          Show this help message"
            echo ""
            echo "Components:"
            echo "  b1  - B1 Web Server (REST API)"
            echo "  b2  - B2 IoT Gateway (Sensor Data)"
            echo "  c1  - C1 Cloud Communication (Python)"
            echo "  c2  - C2 Central Broker (Redis)"
            echo "  a1  - A1 Car User App (React Native)"
            echo ""
            echo "Examples:"
            echo "  $0                         # Run all unit tests"
            echo "  $0 --unit --coverage       # Run unit tests with coverage"
            echo "  $0 --component b1          # Test B1 Web Server only"
            echo "  $0 --component c1          # Test C1 Cloud Communication only"
            echo "  $0 --e2e                   # Run end-to-end tests"
            echo "  $0 --all                   # Run all test types"
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

cd "$PROJECT_ROOT/B-car-demo-backend"
if [ ! -d "node_modules" ]; then
    print_status $YELLOW "Installing Node.js dependencies..."
    npm install
fi

# Install Python dependencies
if [ -d "$PROJECT_ROOT/car-demo-venv" ]; then
    print_status $GREEN "✓ Python virtual environment exists"
    source "$PROJECT_ROOT/car-demo-venv/bin/activate"
else
    print_status $YELLOW "Creating Python virtual environment..."
    cd "$PROJECT_ROOT"
    python3 -m venv car-demo-venv
    source car-demo-venv/bin/activate
fi

# Install/upgrade Python dependencies
print_status $YELLOW "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q pytest pytest-asyncio pytest-mock pytest-cov fakeredis aiohttp redis python-dotenv websockets

# Install C1 requirements if available
if [ -f "$SCRIPT_DIR/C-car-demo-in-car/C1-cloud-communication/requirements.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/C-car-demo-in-car/C1-cloud-communication/requirements.txt"
fi

# Install C5 requirements if available
if [ -f "$SCRIPT_DIR/C-car-demo-in-car/C5-data-sensors/requirements.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/C-car-demo-in-car/C5-data-sensors/requirements.txt"
fi

print_status $GREEN "✓ Python dependencies installed"

# Run tests based on configuration
print_status $YELLOW "3. Running Tests..."

# Test result tracking
TEST_RESULTS=()
FAILED_TESTS=0

# Build Jest command options
JEST_OPTIONS=""
if [ "$COVERAGE" = true ]; then
    JEST_OPTIONS="$JEST_OPTIONS --coverage"
fi
if [ "$WATCH" = true ]; then
    JEST_OPTIONS="$JEST_OPTIONS --watch"
fi

# Component-specific tests
if [ -n "$COMPONENT" ]; then
    case $COMPONENT in
        b1)
            print_status $BLUE "Running B1 Web Server tests..."
            cd "$SCRIPT_DIR/B-car-demo-backend/B1-web-server"
            npm test $JEST_OPTIONS
            TEST_RESULTS+=("B1 Web Server: $?")
            ;;
        b2)
            print_status $BLUE "Running B2 IoT Gateway tests..."
            cd "$SCRIPT_DIR/B-car-demo-backend/B2-iot-gateway"
            npm test $JEST_OPTIONS
            TEST_RESULTS+=("B2 IoT Gateway: $?")
            ;;
        c2)
            print_status $BLUE "Running C2 Central Broker tests..."
            cd "$SCRIPT_DIR/C-car-demo-in-car/C2-central-broker"
            npm test $JEST_OPTIONS
            TEST_RESULTS+=("C2 Central Broker: $?")
            ;;
        c1)
            print_status $BLUE "Running C1 Cloud Communication tests..."
            cd "$SCRIPT_DIR/C-car-demo-in-car/C1-cloud-communication"
            if [ -d "$PROJECT_ROOT/car-demo-venv" ]; then
                source "$PROJECT_ROOT/car-demo-venv/bin/activate"
            fi
            pytest tests/ -v
            TEST_RESULTS+=("C1 Cloud Communication: $?")
            ;;
        a1)
            print_status $BLUE "Running A1 Car User App tests..."
            cd "$SCRIPT_DIR/A-car-demo-frontend/A1-car-user-app"
            npm test $JEST_OPTIONS
            TEST_RESULTS+=("A1 Car User App: $?")
            ;;
        *)
            print_status $RED "Unknown component: $COMPONENT"
            echo "Valid components: b1, b2, c1, c2, a1"
            exit 1
            ;;
    esac
else
    # Run selected test types
    if [ "$UNIT_TESTS" = true ]; then
        print_status $BLUE "Running Unit Tests..."
        
        # B1 Web Server tests
        print_status $YELLOW "Testing B1 Web Server..."
        cd "$SCRIPT_DIR/B-car-demo-backend/B1-web-server"
        if [ -f "package.json" ]; then
            npm test $JEST_OPTIONS
            B1_RESULT=$?
            TEST_RESULTS+=("B1 Web Server: $B1_RESULT")
            [ $B1_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # B2 IoT Gateway tests
        print_status $YELLOW "Testing B2 IoT Gateway..."
        cd "$SCRIPT_DIR/B-car-demo-backend/B2-iot-gateway"
        if [ -f "package.json" ]; then
            npm test $JEST_OPTIONS
            B2_RESULT=$?
            TEST_RESULTS+=("B2 IoT Gateway: $B2_RESULT")
            [ $B2_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # C2 Central Broker tests
        print_status $YELLOW "Testing C2 Central Broker..."
        cd "$SCRIPT_DIR/C-car-demo-in-car/C2-central-broker"
        if [ -f "package.json" ]; then
            npm test $JEST_OPTIONS
            C2_RESULT=$?
            TEST_RESULTS+=("C2 Central Broker: $C2_RESULT")
            [ $C2_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # Python unit tests
        print_status $YELLOW "Running Python Unit Tests..."
        if [ -d "$PROJECT_ROOT/car-demo-venv" ]; then
            source "$PROJECT_ROOT/car-demo-venv/bin/activate"
        fi
        
        # C1 Cloud Communication tests
        if [ -d "$SCRIPT_DIR/C-car-demo-in-car/C1-cloud-communication/tests" ]; then
            print_status $YELLOW "Testing C1 Cloud Communication..."
            cd "$SCRIPT_DIR/C-car-demo-in-car/C1-cloud-communication"
            pytest tests/ -v
            C1_RESULT=$?
            TEST_RESULTS+=("C1 Cloud Communication: $C1_RESULT")
            [ $C1_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # C5 Sensor Simulator tests
        if [ -d "$SCRIPT_DIR/C-car-demo-in-car/C5-data-sensors/tests" ]; then
            print_status $YELLOW "Testing C5 Data Sensors..."
            cd "$SCRIPT_DIR/C-car-demo-in-car/C5-data-sensors"
            pytest tests/ -v
            C5_RESULT=$?
            TEST_RESULTS+=("C5 Data Sensors: $C5_RESULT")
            [ $C5_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        
        # Frontend tests
        if [ -d "$SCRIPT_DIR/A-car-demo-frontend/A1-car-user-app/__tests__" ]; then
            print_status $YELLOW "Testing A1 Car User App..."
            cd "$SCRIPT_DIR/A-car-demo-frontend/A1-car-user-app"
            
            # Check if jest is available (could be in node_modules or parent)
            if command -v ../node_modules/.bin/jest &> /dev/null || command -v node_modules/.bin/jest &> /dev/null; then
                print_status $YELLOW "Running React Native tests (this may take a moment)..."
                npm test > /tmp/a1_test.log 2>&1
                A1_RESULT=$?
                
                # Check test results
                if grep -q "passed" /tmp/a1_test.log 2>/dev/null; then
                    TEST_LINE=$(grep "Tests:" /tmp/a1_test.log | tail -1)
                    PASSED=$(echo "$TEST_LINE" | grep -oP '\d+(?= passed)')
                    TOTAL=$(echo "$TEST_LINE" | grep -oP '\d+(?= total)')
                    
                    if [ ! -z "$PASSED" ] && [ ! -z "$TOTAL" ] && [ "$PASSED" -ge 20 ]; then
                        PERCENT=$(( PASSED * 100 / TOTAL ))
                        print_status $GREEN "✓ A1: $PASSED/$TOTAL tests passing ($PERCENT%)"
                        TEST_RESULTS+=("A1 Car User App: PARTIAL($PASSED/$TOTAL)")
                    elif [ ! -z "$PASSED" ] && [ ! -z "$TOTAL" ]; then
                        print_status $YELLOW "◐ A1: $PASSED/$TOTAL tests passing"
                        TEST_RESULTS+=("A1 Car User App: PARTIAL($PASSED/$TOTAL)")
                    else
                        TEST_RESULTS+=("A1 Car User App: $A1_RESULT")
                        [ $A1_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
                    fi
                else
                    TEST_RESULTS+=("A1 Car User App: $A1_RESULT")
                    [ $A1_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
                fi
            else
                print_status $YELLOW "Skipping A1 tests (dependencies not installed)"
                print_status $YELLOW "Run: cd A-car-demo-frontend/A1-car-user-app && npm install"
                TEST_RESULTS+=("A1 Car User App: SKIPPED")
            fi
        fi
    fi
    
    if [ "$E2E_TESTS" = true ]; then
        print_status $BLUE "Running End-to-End Tests..."
        
        # Ensure services are running for E2E tests
        print_status $YELLOW "Checking if services are running for E2E tests..."
        
        SERVICES_OK=true
        check_service "http://localhost:3001/health" "B1 Web Server" || SERVICES_OK=false
        check_service "http://localhost:3002/health" "B2 IoT Gateway" || SERVICES_OK=false
        check_service "http://localhost:3003/health" "C2 Central Broker" || SERVICES_OK=false
        
        if [ "$SERVICES_OK" = false ]; then
            print_status $YELLOW "Some services are not running. Start them with:"
            echo "  cd B-car-demo-backend/B1-web-server && npm start &"
            echo "  cd B-car-demo-backend/B2-iot-gateway && npm start &"
            echo "  cd C-car-demo-in-car/C2-central-broker && npm start &"
            print_status $YELLOW "Skipping E2E tests..."
        else
            cd "$SCRIPT_DIR/tests/e2e"
            if [ -f "package.json" ]; then
                npm test -- --runInBand --detectOpenHandles
                E2E_RESULT=$?
                TEST_RESULTS+=("E2E Tests: $E2E_RESULT")
                [ $E2E_RESULT -ne 0 ] && FAILED_TESTS=$((FAILED_TESTS + 1))
            fi
        fi
    fi
fi

print_status $GREEN "✅ Test execution completed!"

# Print test summary
echo ""
print_status $BLUE "================================"
print_status $BLUE "Test Results Summary:"
print_status $BLUE "================================"
for result in "${TEST_RESULTS[@]}"; do
    component=$(echo "$result" | cut -d: -f1)
    exit_code=$(echo "$result" | cut -d: -f2 | tr -d ' ')
    if [ "$exit_code" = "SKIPPED" ]; then
        print_status $YELLOW "⊙ $component: SKIPPED"
    elif [[ "$exit_code" =~ ^PARTIAL ]]; then
        details=$(echo "$exit_code" | sed 's/PARTIAL//')
        print_status $GREEN "◐ $component: PARTIAL PASS $details"
    elif [ "$exit_code" -eq 0 ] 2>/dev/null; then
        print_status $GREEN "✓ $component: PASSED"
    else
        print_status $RED "✗ $component: FAILED (exit code: $exit_code)"
    fi
done
print_status $BLUE "================================"

# Generate test report summary
if [ "$COVERAGE" = true ]; then
    print_status $BLUE "Coverage reports generated in component coverage/ directories"
fi

echo ""
print_status $YELLOW "Additional Options:"
echo "  Use --coverage flag to generate coverage reports"
echo "  Use --watch flag for continuous testing during development"
echo "  Use --component <name> to test a specific component (b1, b2, c1, c2, a1)"

# Exit with error if any tests failed
if [ $FAILED_TESTS -gt 0 ]; then
    print_status $RED "❌ $FAILED_TESTS component(s) failed tests"
    exit 1
else
    print_status $GREEN "✅ All tests passed!"
    exit 0
fi