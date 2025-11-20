# 🚗 Car Demo System - Developer Setup Guide

## For New Developers Joining the Project

### 🎯 **Quick Start (Recommended)**

For full system development with all components:

```bash
# Clone the main orchestration repository
git clone https://github.com/kai-rasilainen/car-demo-system.git
cd car-demo-system

# The orchestration repo contains everything via submodules
git submodule update --init --recursive

# Run the complete setup and testing
./activate-python.sh  # Sets up Python environment
./test-system-complete.sh  # Tests the entire system
```

---

## 🏗️ **Development Scenarios**

### **Scenario 1: Full Stack Developer**
*Working on the complete system*

```bash
git clone https://github.com/kai-rasilainen/car-demo-system.git
cd car-demo-system
git submodule update --init --recursive
```

**What you get:**
- Complete orchestration setup
- All components (frontend, backend, in-car)
- Testing scripts and automation
- Python virtual environment setup

---

### **Scenario 2: Backend Developer** 
*Working only on APIs and services*

```bash
git clone https://github.com/kai-rasilainen/car-demo-backend.git
cd car-demo-backend
```

**What you get:**
- B1 Web Server (REST API)
- B2 IoT Gateway (WebSocket + MQTT)
- B3 Real-time Database (MongoDB)
- B4 Static Database (PostgreSQL)

---

### **Scenario 3: Frontend Developer**
*Working on mobile and web apps*

```bash
git clone https://github.com/kai-rasilainen/car-demo-frontend.git
cd car-demo-frontend
```

**What you get:**
- A1 Mobile App (React Native/Expo)
- A2 Staff Web App (React)

---

### **Scenario 4: IoT/Hardware Developer**
*Working on in-car systems*

```bash
git clone https://github.com/kai-rasilainen/car-demo-in-car.git
cd car-demo-in-car
```

**What you get:**
- C1 Cloud Communication (Python)
- C2 Central Broker (Node.js + Redis)
- C5 Data Sensors (Python simulators)

---

## 🛠️ **Prerequisites & Setup**

### **Required Software:**
```bash
# Node.js & npm
node --version  # Should be v18+ 
npm --version

# Python 
python3 --version  # Should be 3.8+

# Redis (for real-time data)
sudo apt install redis-server  # Ubuntu/Debian
redis-cli ping  # Should return PONG

# Docker (optional, for databases)
docker --version
```

### **Initial Setup Commands:**

#### **For Full System (car-demo-system):**
```bash
# 1. Clone and setup
git clone https://github.com/kai-rasilainen/car-demo-system.git
cd car-demo-system

# 2. Setup Python environment
python3 -m venv car-demo-venv
source car-demo-venv/bin/activate
pip install -r car-demo-in-car/requirements.txt

# 3. Install Node.js dependencies
cd car-demo-backend && npm install && npm run install-all && cd ..
cd car-demo-in-car/C2-central-broker && npm install && cd ../..

# 4. Start Redis
redis-server --daemonize yes

# 5. Test the system
./test-system-complete.sh
```

#### **For Backend Only (car-demo-backend):**
```bash
# 1. Clone
git clone https://github.com/kai-rasilainen/car-demo-backend.git
cd car-demo-backend

# 2. Install dependencies
npm install
npm run install-all

# 3. Start services
npm run dev-all
```

---

## 🚀 **Testing Your Setup**

### **Quick Health Check:**
```bash
# Check if services are running
curl http://localhost:3001/health  # B1 Web Server
curl http://localhost:3003/health  # C2 Central Broker

# Test car data API
curl http://localhost:3001/api/car/ABC-123
curl http://localhost:3003/api/cars
```

### **Python Components:**
```bash
# Activate Python environment
source car-demo-venv/bin/activate

# Test sensor simulation
cd car-demo-in-car/C1-cloud-communication
python test_c2_simulator.py
```

---

## 📁 **Repository Structure**

```
car-demo-system/           # 🏠 Main orchestration
|--- car-demo-backend/      # 🔗 Git submodule
|--- car-demo-frontend/     # 🔗 Git submodule  
|--- car-demo-in-car/       # 🔗 Git submodule
|--- scripts/               # 🛠️ Setup automation
|--- activate-python.sh     # 🐍 Python env helper
|--- test-system*.sh        # 🧪 Testing scripts
`--- docker-compose.yml     # 🐳 Database services

car-demo-backend/          # 🎯 Standalone backend
|--- B1-web-server/         # REST API
|--- B2-iot-gateway/        # WebSocket + MQTT
|--- B3-realtime-database/  # MongoDB
`--- B4-static-database/    # PostgreSQL

car-demo-frontend/         # 🎯 Standalone frontend
|--- A1-car-user-app/       # Mobile app
`--- A2-rental-staff-app/   # Web app

car-demo-in-car/           # 🎯 Standalone in-car
|--- C1-cloud-communication/ # Python
|--- C2-central-broker/      # Node.js + Redis
`--- C5-data-sensors/        # Python sensors
```

---

## 🤝 **Development Workflow**

### **For Team Development:**

1. **Choose your focus area** (full-stack, backend, frontend, or IoT)
2. **Clone the appropriate repository** (see scenarios above)
3. **Set up dependencies** using the setup commands
4. **Test your setup** with the health check commands
5. **Start developing!**

### **Working with the Full System:**
- Use `car-demo-system` for integration work
- Use individual repos (`car-demo-backend`, etc.) for focused development
- The submodules stay in sync automatically

### **Pushing Changes:**
```bash
# For individual components
cd car-demo-backend  # or car-demo-frontend, car-demo-in-car
git add .
git commit -m "your changes"
git push origin main

# For orchestration changes
cd car-demo-system
git add .
git commit -m "system-wide changes"
git push origin main
```

---

## 📞 **Getting Help**

- **System not starting?** Run `./test-system-complete.sh` for diagnostics
- **Port conflicts?** Check the Service URLs section - Jenkins uses 8080
- **Python issues?** Use `./activate-python.sh` to verify environment
- **Database problems?** Redis must be running for core functionality

## 🎯 **What's Working Out of the Box**

✅ **REST API** - Car data, health checks  
✅ **Real-time data** - Redis-based storage  
✅ **Python sensors** - Realistic car data simulation  
✅ **WebSocket** - Real-time communication (port 8081)  
✅ **Testing scripts** - Automated validation  
✅ **Virtual environment** - Python dependency isolation  

---

**Happy coding! 🚀**