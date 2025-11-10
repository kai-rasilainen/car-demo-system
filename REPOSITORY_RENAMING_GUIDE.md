# Repository Renaming Guide

## What Changed

All scripts in `car-demo-system` have been updated to use the new repository naming convention:
- `car-demo-backend` → `B-car-demo-backend`
- `car-demo-frontend` → `A-car-demo-frontend`
- `car-demo-in-car` → `C-car-demo-in-car`

## Steps to Complete the Renaming

### 1. Rename GitHub Repositories

Go to GitHub and rename each repository:

**A-car-demo-frontend:**
1. Go to: https://github.com/kai-rasilainen/car-demo-frontend
2. Settings → Repository name
3. Change to: `A-car-demo-frontend`
4. Click "Rename"

**B-car-demo-backend:**
1. Go to: https://github.com/kai-rasilainen/car-demo-backend
2. Settings → Repository name
3. Change to: `B-car-demo-backend`
4. Click "Rename"

**C-car-demo-in-car:**
1. Go to: https://github.com/kai-rasilainen/car-demo-in-car
2. Settings → Repository name
3. Change to: `C-car-demo-in-car`
4. Click "Rename"

### 2. Update Local Repository Remotes

After renaming on GitHub, update your existing local clones:

```bash
cd /home/kai/projects/car-demo-repos/car-demo-system

# Rename local directories
mv car-demo-backend B-car-demo-backend
mv car-demo-frontend A-car-demo-frontend
mv car-demo-in-car C-car-demo-in-car

# Update git remotes
cd B-car-demo-backend
git remote set-url origin https://github.com/kai-rasilainen/B-car-demo-backend.git

cd ../A-car-demo-frontend
git remote set-url origin https://github.com/kai-rasilainen/A-car-demo-frontend.git

cd ../C-car-demo-in-car
git remote set-url origin https://github.com/kai-rasilainen/C-car-demo-in-car.git

cd ..
```

### 3. Commit Updated Scripts

```bash
cd /home/kai/projects/car-demo-repos/car-demo-system
git add -A
git commit -m "Update scripts to use renamed repositories (A-, B-, C- prefixes)"
git push
```

### 4. Test the Setup

After renaming, test that everything works:

```bash
cd /home/kai/projects/car-demo-repos/car-demo-system
./stop-all.sh
./start-complete.sh
```

## Files Updated

The following files have been updated with new repository names:
- `activate-python.sh`
- `docker-compose.yml`
- `run-tests.sh`
- `start-complete.sh`
- `stop-all.sh`
- `test-system.sh`
- `test-system-complete.sh`
- `scripts/setup-all.sh`
- `scripts/setup-github-repos.sh`
- `scripts/start-all.sh`

## Naming Convention

All repositories now follow this pattern:
- **A-** prefix: Frontend components (user apps)
  - `A-car-demo-frontend/`
    - `A1-car-user-app/` (React Native)
    - `A2-rental-staff-app/` (React Web)

- **B-** prefix: Backend components (APIs, databases)
  - `B-car-demo-backend/`
    - `B1-web-server/` (REST API)
    - `B2-iot-gateway/` (WebSocket + MQTT)
    - `B3-realtime-database/` (MongoDB)
    - `B4-static-database/` (PostgreSQL)

- **C-** prefix: In-car components (embedded systems)
  - `C-car-demo-in-car/`
    - `C1-cloud-communication/` (Python)
    - `C2-central-broker/` (Node.js + Redis)
    - `C5-data-sensors/` (Python)

## Notes

- GitHub automatically sets up redirects from old URLs to new ones
- Existing clones will continue to work with the old URLs temporarily
- Update remotes to avoid confusion and ensure long-term compatibility
- The `car-demo-system` orchestration repository name stays unchanged
