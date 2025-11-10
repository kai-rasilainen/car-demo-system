#!/bin/bash

# GitHub Repository Setup Script
# This script automates the creation and pushing of all migrated repositories

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
GITHUB_USER="kai-rasilainen"
REPOS_DIR=".."

print_header "GitHub Repository Setup"
echo "GitHub User: $GITHUB_USER"
echo "Repositories Directory: $REPOS_DIR"
echo ""

# Check if repos directory exists
if [ ! -d "$REPOS_DIR" ]; then
    print_error "Repositories directory not found: $REPOS_DIR"
    print_error "Please run ./migrate-to-repos.sh first"
    exit 1
fi

# Check if user wants to proceed
echo "This script will:"
echo "  1. Add GitHub remotes to each repository"
echo "  2. Push all repositories to GitHub"
echo ""
echo "Prerequisites:"
echo "  ✓ You must have created the GitHub repositories manually"
echo "  ✓ Repository names: A-car-demo-frontend, B-car-demo-backend, C-car-demo-in-car, car-demo-system"
echo ""
read -p "Have you created all 4 repositories on GitHub? (y/N): " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo ""
    print_warning "Please create the GitHub repositories first:"
    echo ""
    echo "1. Go to https://github.com/$GITHUB_USER"
    echo "2. Click '+' → 'New repository'"
    echo "3. Create these repositories (don't initialize with README/gitignore):"
    echo "   - A-car-demo-frontend"
    echo "   - B-car-demo-backend"
    echo "   - C-car-demo-in-car"
    echo "   - car-demo-system"
    echo ""
    echo "Then run this script again."
    exit 0
fi

cd "$REPOS_DIR"

# Repository configurations
declare -A repositories=(
    ["A-car-demo-frontend"]="Frontend applications for car demo system"
    ["B-car-demo-backend"]="Backend services and databases for car demo system"
    ["C-car-demo-in-car"]="In-car systems and sensors for car demo system"
    ["car-demo-system"]="Main orchestration repository for car demo system"
)

# Process each repository
for repo_name in "${!repositories[@]}"; do
    description="${repositories[$repo_name]}"
    
    print_header "Setting up $repo_name"
    
    if [ ! -d "$repo_name" ]; then
        print_error "Repository directory not found: $repo_name"
        continue
    fi
    
    cd "$repo_name"
    
    # Check if remote already exists
    if git remote get-url origin >/dev/null 2>&1; then
        print_warning "Remote 'origin' already exists, removing..."
        git remote remove origin
    fi
    
    # Add GitHub remote
    print_status "Adding GitHub remote..."
    git remote add origin "https://github.com/$GITHUB_USER/$repo_name.git"
    
    # Push to GitHub
    print_status "Pushing to GitHub..."
    if git push -u origin main --force; then
        print_status "✓ Successfully pushed $repo_name"
    else
        print_error "✗ Failed to push $repo_name"
        print_error "Please check:"
        print_error "  1. Repository exists on GitHub"
        print_error "  2. You have push permissions"
        print_error "  3. GitHub authentication is set up"
    fi
    
    cd ..
    echo ""
done

print_header "Setup Complete!"
echo ""
echo "🎉 All repositories have been pushed to GitHub!"
echo ""
echo "Repository URLs:"
for repo_name in "${!repositories[@]}"; do
    echo "  📦 https://github.com/$GITHUB_USER/$repo_name"
done
echo ""
echo "Next steps:"
echo "  1. Visit each repository to verify the code was pushed correctly"
echo "  2. Set up branch protection rules (optional)"
echo "  3. Add repository topics for better discoverability"
echo "  4. Set up GitHub Actions for CI/CD (optional)"
echo ""
echo "Test the integration:"
echo "  mkdir ~/test-setup && cd ~/test-setup"
echo "  git clone https://github.com/$GITHUB_USER/car-demo-system.git"
echo "  cd car-demo-system && ./scripts/setup-all.sh"

print_status "GitHub setup completed successfully!"