#!/bin/bash

# Car Demo System - Virtual Environment Recreation Script
# This script removes and recreates the Python virtual environment
# Use this when moving the project to a new location or user

echo "🔄 Recreating Python Virtual Environment..."
echo "=========================================="

# Get the directory where this script is located (should be car-demo-system)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Go up one level to find the project root
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/car-demo-venv"

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}\033[0m"
}

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'

# Deactivate if currently active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status $YELLOW "Deactivating current virtual environment..."
    deactivate 2>/dev/null || true
fi

# Remove old virtual environment
if [ -d "$VENV_DIR" ]; then
    print_status $YELLOW "Removing old virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create new virtual environment
print_status $YELLOW "Creating new virtual environment..."
cd "$PROJECT_ROOT"
python3 -m venv car-demo-venv

if [ ! -d "$VENV_DIR" ]; then
    print_status $RED "❌ Failed to create virtual environment"
    exit 1
fi

# Activate and install packages
print_status $YELLOW "Installing Python packages..."
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install pytest pytest-asyncio pytest-mock fakeredis

# Verify installation
print_status $GREEN "✅ Virtual environment recreated successfully!"
echo ""
echo "📦 Installed packages:"
pip list --format=columns
echo ""
print_status $GREEN "🚀 Ready to use! Run './activate-python.sh' to activate the environment."