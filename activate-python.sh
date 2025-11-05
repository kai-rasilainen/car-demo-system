#!/bin/bash

# Car Demo System - Python Virtual Environment Setup
echo "🐍 Activating Car Demo Python Environment..."

# Activate virtual environment
source /home/kai/projects/car-demo-repos/car-demo-venv/bin/activate

# Verify activation
echo "✅ Virtual environment activated:"
echo "Python: $(python --version)"
echo "Location: $(which python)"
echo "Pip: $(pip --version)"

# Show installed packages
echo ""
echo "📦 Installed Python packages:"
pip list --format=table

echo ""
echo "🚀 Ready to run Python components!"
echo "Usage examples:"
echo "cd car-demo-in-car/C1-cloud-communication && python cloud_communicator.py"
echo "cd car-demo-in-car/C5-data-sensors && python sensor_simulator.py"
echo "cd car-demo-in-car/C1-cloud-communication && python test_c2_simulator.py"
echo ""
echo "To deactivate: deactivate"