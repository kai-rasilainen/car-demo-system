# GitHub Repository Setup Guide

This guide provides detailed steps to create GitHub repositories for each component and push the migrated code.

## 📋 Overview

After running the migration script, you'll have 4 repositories to create on GitHub:

1. **car-demo-frontend** - Frontend applications (A1 + A2)
2. **car-demo-backend** - Backend services (B1-B4)
3. **car-demo-in-car** - In-car systems (C1-C5)
4. **car-demo-system** - Main orchestration

## 🌐 Step-by-Step GitHub Setup

### Method 1: Using GitHub Web Interface (Recommended)

#### Step 1: Create Repositories on GitHub

1. **Go to GitHub**: Open https://github.com in your browser
2. **Sign in** to your GitHub account (`kai-rasilainen`)
3. **Create each repository** by clicking the "+" icon in the top right, then "New repository"

For each repository, use these settings:

#### Repository 1: car-demo-frontend
```
Repository name: car-demo-frontend
Description: Frontend applications for car demo system (React Native + React)
Visibility: ✅ Public (or Private if preferred)
❌ Add a README file (we already have one)
❌ Add .gitignore (we already have one)
❌ Choose a license (optional - add later if needed)
```

#### Repository 2: car-demo-backend
```
Repository name: car-demo-backend
Description: Backend services and databases for car demo system (Node.js + MongoDB + PostgreSQL)
Visibility: ✅ Public (or Private if preferred)
❌ Add a README file
❌ Add .gitignore
❌ Choose a license
```

#### Repository 3: car-demo-in-car
```
Repository name: car-demo-in-car
Description: In-car systems and sensors for car demo system (Python + Redis)
Visibility: ✅ Public (or Private if preferred)
❌ Add a README file
❌ Add .gitignore
❌ Choose a license
```

#### Repository 4: car-demo-system
```
Repository name: car-demo-system
Description: Main orchestration repository for car demo system
Visibility: ✅ Public (or Private if preferred)
❌ Add a README file
❌ Add .gitignore
❌ Choose a license
```

#### Step 2: Push Local Repositories to GitHub

After creating all 4 repositories on GitHub, run these commands:

```bash
# Navigate to the migrated repositories
cd ../car-demo-repos

# 1. Push Frontend Repository
cd car-demo-frontend
git remote add origin https://github.com/kai-rasilainen/car-demo-frontend.git
git push -u origin main

cd ..

# 2. Push Backend Repository
cd car-demo-backend
git remote add origin https://github.com/kai-rasilainen/car-demo-backend.git
git push -u origin main

cd ..

# 3. Push In-Car Repository
cd car-demo-in-car
git remote add origin https://github.com/kai-rasilainen/car-demo-in-car.git
git push -u origin main

cd ..

# 4. Push Main Orchestration Repository
cd car-demo-system
git remote add origin https://github.com/kai-rasilainen/car-demo-system.git
git push -u origin main

cd ..
```

### Method 2: Using GitHub CLI (Alternative)

If you have GitHub CLI installed (`gh`), you can create and push all repositories with one script:

```bash
# Navigate to migrated repositories
cd ../car-demo-repos

# Create and push all repositories
repos=(
    "car-demo-frontend:Frontend applications for car demo system (React Native + React)"
    "car-demo-backend:Backend services and databases for car demo system (Node.js + MongoDB + PostgreSQL)"
    "car-demo-in-car:In-car systems and sensors for car demo system (Python + Redis)"
    "car-demo-system:Main orchestration repository for car demo system"
)

for repo_info in "${repos[@]}"; do
    IFS=':' read -r repo_name description <<< "$repo_info"
    
    echo "Creating and pushing $repo_name..."
    cd "$repo_name"
    
    # Create GitHub repository
    gh repo create "kai-rasilainen/$repo_name" \
        --description "$description" \
        --public \
        --source=. \
        --remote=origin \
        --push
    
    cd ..
done
```

## 🔧 Verification Steps

After pushing all repositories, verify everything is working:

### 1. Check Repository URLs

Visit each repository to confirm they were created successfully:

- https://github.com/kai-rasilainen/car-demo-frontend
- https://github.com/kai-rasilainen/car-demo-backend
- https://github.com/kai-rasilainen/car-demo-in-car
- https://github.com/kai-rasilainen/car-demo-system

### 2. Test Clone and Setup

Test that someone else can clone and set up your system:

```bash
# Create a fresh test directory
mkdir ~/test-car-demo && cd ~/test-car-demo

# Clone the main orchestration repo
git clone https://github.com/kai-rasilainen/car-demo-system.git
cd car-demo-system

# Run the setup script
./scripts/setup-all.sh

# This should clone all other repositories and set up the system
```

### 3. Test Individual Components

Test each component can be developed independently:

```bash
# Test backend
git clone https://github.com/kai-rasilainen/car-demo-backend.git
cd car-demo-backend
./scripts/dev-start.sh

# Test frontend (in another terminal)
git clone https://github.com/kai-rasilainen/car-demo-frontend.git
cd car-demo-frontend
./scripts/dev-start.sh

# Test in-car systems (in another terminal)
git clone https://github.com/kai-rasilainen/car-demo-in-car.git
cd car-demo-in-car
./scripts/start-all.sh
```

## 🎯 Repository Management

### Branch Protection (Optional)

For production repositories, consider setting up branch protection:

1. Go to each repository → Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### Issues and Project Management

Set up issues and project boards for each repository:

1. **Frontend Issues**: UI/UX bugs, mobile-specific issues
2. **Backend Issues**: API bugs, database issues, performance
3. **In-Car Issues**: Sensor simulation, communication problems
4. **Main Issues**: Integration problems, system-wide features

### Repository Topics

Add topics to each repository for better discoverability:

#### car-demo-frontend
Topics: `react`, `react-native`, `expo`, `frontend`, `mobile-app`, `car-demo`

#### car-demo-backend
Topics: `nodejs`, `express`, `mongodb`, `postgresql`, `api`, `backend`, `car-demo`

#### car-demo-in-car
Topics: `python`, `redis`, `iot`, `sensors`, `simulation`, `car-demo`

#### car-demo-system
Topics: `docker`, `orchestration`, `microservices`, `demo`, `car-system`

## 🚀 Continuous Integration Setup

Consider setting up GitHub Actions for each repository:

### Frontend CI (.github/workflows/frontend.yml)
```yaml
name: Frontend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm run install-all
      - run: npm run test-all
      - run: npm run build-all
```

### Backend CI (.github/workflows/backend.yml)
```yaml
name: Backend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm run install-all
      - run: npm run test-all
```

### In-Car Systems CI (.github/workflows/in-car.yml)
```yaml
name: In-Car Systems CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: ./scripts/setup-python.sh
      - run: npm run install-all
      - run: source .venv/bin/activate && python -m pytest
```

## 📝 Documentation Updates

After creating the repositories, update documentation:

1. **Update main README** with links to all repositories
2. **Create wiki pages** for each repository with detailed documentation
3. **Add contribution guidelines** (CONTRIBUTING.md) to each repository
4. **Create release notes** when you tag versions

## 🔄 Development Workflow

With separate repositories, establish a development workflow:

1. **Feature Development**: Create feature branches in respective repositories
2. **Integration Testing**: Use main orchestration repo to test component integration
3. **Releases**: Tag versions in each repository and update main orchestration
4. **Hotfixes**: Apply fixes to individual repositories and update orchestration

This completes the GitHub setup! Your car demo system is now properly split into focused, manageable repositories while maintaining the ability to work together as a complete system.