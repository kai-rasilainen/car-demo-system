pipeline {
    agent any
    
    parameters {
        string(
            name: 'FEATURE_REQUEST',
            defaultValue: 'Add tire pressure monitoring to the car dashboard',
            description: 'Feature request to analyze'
        )
        booleanParam(
            name: 'USE_AI_AGENTS',
            defaultValue: true,
            description: 'Use AI agents for analysis'
        )
        booleanParam(
            name: 'USE_MOCK_DATA',
            defaultValue: true,
            description: 'Start B1 server with mock data'
        )
        string(
            name: 'OLLAMA_MODEL',
            defaultValue: 'llama3:8b',
            description: 'Ollama model to use'
        )
        string(
            name: 'OUTPUT_FILE',
            defaultValue: 'ai-feature-analysis.md',
            description: 'Output filename for the analysis report'
        )
    }
    
    environment {
        OLLAMA_HOST = 'http://10.0.2.2:11434'
        WORKSPACE_ROOT = "${WORKSPACE}"
        ANALYSIS_DIR = "${WORKSPACE}/analysis-reports"
        TIMESTAMP = sh(script: "date +%Y%m%d-%H%M%S", returnStdout: true).trim()
    }
    
    stages {
        stage('Clean Workspace') {
            steps {
                echo "[CLEAN] Cleaning workspace..."
                deleteDir()
                echo "[OK] Workspace cleaned"
            }
        }
        
        stage('Checkout') {
            steps {
                echo "[GIT] Checking out code..."
                checkout scm
                echo "[OK] Code checked out"
            }
        }
        
        stage('Setup') {
            steps {
                echo "[AI] AI-Driven Multi-Agent Feature Analysis"
                echo "=========================================="
                echo "Request: ${params.FEATURE_REQUEST}"
                echo "AI Agents: ${params.USE_AI_AGENTS}"
                echo "Mock Data: ${params.USE_MOCK_DATA}"
                echo "Model: ${params.OLLAMA_MODEL}"
                echo "Timestamp: ${env.TIMESTAMP}"
                echo ""
                echo "Flow: Agent A → AI decides if B needed → AI decides if C needed"
                
                sh '''
                    mkdir -p ${ANALYSIS_DIR}
                    chmod +x scripts/ai-agent-orchestrator.py
                    chmod +x scripts/generate-implementation-plan.py
                    chmod +x scripts/create-component-tasks.py
                '''
            }
        }
        
        stage('Validate Ollama') {
            when {
                expression { params.USE_AI_AGENTS == true }
            }
            steps {
                script {
                    echo "[CHECK] Checking Ollama connection..."
                    try {
                        sh '''
                            curl -s ${OLLAMA_HOST}/api/tags > /dev/null || {
                                echo "[ERROR] Cannot connect to Ollama at ${OLLAMA_HOST}"
                                echo "Please ensure Ollama is running"
                                exit 1
                            }
                            echo "[OK] Ollama is available at ${OLLAMA_HOST}"
                            
                            # Check if model is available
                            if curl -s ${OLLAMA_HOST}/api/tags | grep -q "llama3:8b"; then
                                echo "[OK] Model llama3:8b is available"
                            else
                                echo "[WARN]  Model llama3:8b may need to be pulled first"
                                echo "Run on Windows: ollama pull llama3:8b"
                            fi
                        '''
                    } catch (Exception e) {
                        error("Ollama is not available. Please start Ollama first.")
                    }
                }
            }
        }
        
        stage('Start Mock Data Server') {
            when {
                expression { params.USE_MOCK_DATA == true }
            }
            steps {
                script {
                    echo "[MOCK] Starting B1 web server with mock tire pressure data..."
                    try {
                        sh '''#!/bin/bash
                            set -e  # Exit on error
                            
                            echo "[INFO] Current workspace: $(pwd)"
                            echo "[INFO] Workspace contents:"
                            ls -la
                            
                            # Remove old directory if it exists and is empty/broken
                            if [ -d "B-car-demo-backend" ] && [ -z "$(ls -A B-car-demo-backend 2>/dev/null)" ]; then
                                echo "[WARN] B-car-demo-backend exists but is empty, removing..."
                                rm -rf B-car-demo-backend
                            fi
                            
                            # Clone B-car-demo-backend if not present
                            if [ ! -d "B-car-demo-backend/.git" ]; then
                                echo "[INFO] Cloning B-car-demo-backend repository..."
                                git clone -b feature/ai-agent-system https://github.com/kai-rasilainen/B-car-demo-backend.git 2>&1
                                
                                if [ ! -d "B-car-demo-backend/.git" ]; then
                                    echo "[ERROR] Failed to clone B-car-demo-backend - no .git directory created"
                                    echo "[INFO] Attempting clone without specifying branch..."
                                    rm -rf B-car-demo-backend
                                    git clone https://github.com/kai-rasilainen/B-car-demo-backend.git 2>&1
                                    
                                    if [ -d "B-car-demo-backend/.git" ]; then
                                        echo "[INFO] Clone succeeded, checking out feature/ai-agent-system..."
                                        cd B-car-demo-backend
                                        git checkout feature/ai-agent-system 2>&1 || git checkout main 2>&1
                                        cd ..
                                    else
                                        echo "[ERROR] Clone failed completely"
                                        exit 1
                                    fi
                                fi
                            else
                                echo "[INFO] B-car-demo-backend already exists, pulling latest..."
                                cd B-car-demo-backend
                                git fetch origin 2>&1
                                git checkout feature/ai-agent-system 2>&1 || git checkout main 2>&1
                                git pull 2>&1 || true
                                cd ..
                            fi
                            
                            # Verify B1 web server directory exists
                            echo "[INFO] Checking for B1-web-server..."
                            if [ ! -d "B-car-demo-backend/B1-web-server" ]; then
                                echo "[ERROR] B1-web-server directory not found"
                                echo "[INFO] B-car-demo-backend contents:"
                                ls -la B-car-demo-backend/
                                exit 1
                            fi
                            
                            B1_DIR="B-car-demo-backend/B1-web-server"
                            echo "[INFO] Found B1 server at: $B1_DIR"
                            cd "$B1_DIR"
                            
                            # Check package.json exists
                            if [ ! -f "package.json" ]; then
                                echo "[ERROR] package.json not found in B1-web-server"
                                ls -la
                                exit 1
                            fi
                            
                            # Install dependencies if needed
                            if [ ! -d "node_modules" ]; then
                                echo "[INFO] Installing npm dependencies..."
                                npm install
                            fi
                            
                            # Kill any existing server on port 3001
                            lsof -ti:3001 | xargs kill -9 2>/dev/null || true
                            sleep 1
                            
                            # Start server in background with mock data
                            USE_MOCK_DATA=true nohup npm start > ${WORKSPACE}/b1-server.log 2>&1 &
                            
                            # Wait for server to start
                            echo "[INFO] Waiting for server to start..."
                            for i in {1..30}; do
                                if curl -s http://localhost:3001/health > /dev/null; then
                                    echo "[OK] B1 server is running on port 3001"
                                    echo "[OK] Mock data endpoints:"
                                    echo "  - GET http://localhost:3001/api/monitoring/tire-pressure/{carId}"
                                    echo "  - GET http://localhost:3001/api/monitoring/tire-pressure/{carId}/history"
                                    exit 0
                                fi
                                sleep 1
                            done
                            
                            echo "[ERROR] Server failed to start within 30 seconds"
                            echo "[INFO] Server log:"
                            cat ${WORKSPACE}/b1-server.log
                            exit 1
                        '''
                    } catch (Exception e) {
                        echo "[WARN] Could not start mock data server: ${e.message}"
                        echo "[INFO] You can start it manually with: cd B-car-demo-backend/B1-web-server && USE_MOCK_DATA=true npm start"
                    }
                }
            }
        }
        
        stage('AI Agent Analysis') {
            when {
                expression { params.USE_AI_AGENTS == true }
            }
            steps {
                echo "[AI] Running AI-driven agent analysis..."
                echo "Agent A will analyze and determine if Agents B or C are needed..."
                
                script {
                    try {
                        sh """#!/bin/bash
                            cd ${WORKSPACE}
                            
                            echo "Starting AI orchestrator..."
                            python3 scripts/ai-agent-orchestrator.py \\
                                "${params.FEATURE_REQUEST}" \\
                                "${ANALYSIS_DIR}/${params.OUTPUT_FILE}" \\
                                "${OLLAMA_HOST}" \\
                                "${params.OLLAMA_MODEL}"
                            
                            EXIT_CODE=\$?
                            
                            if [ \$EXIT_CODE -ne 0 ]; then
                                echo "[ERROR] AI agent analysis failed with exit code \$EXIT_CODE"
                                exit \$EXIT_CODE
                            fi
                            
                            echo "[OK] AI agent analysis completed successfully"
                        """
                        
                        // Read and display the results
                        def report = readFile("${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}")
                        echo "\n[REPORT] Generated Report Preview:"
                        echo "=" * 50
                        echo report.take(500) + "..."
                        
                    } catch (Exception e) {
                        error("AI agent analysis failed: ${e.message}")
                    }
                }
            }
        }

        stage('Create Component Tasks') {
            when {
                expression { params.USE_AI_AGENTS == true }
            }
            steps {
                echo "[TASKS] Creating per-component task files from analysis report..."

                script {
                    try {
                        sh """#!/bin/bash
                            set -e
                            cd \${WORKSPACE}
                            
                            echo "[INFO] Creating component tasks..."
                            echo "  Input: \${ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                            echo "  Output: \${ANALYSIS_DIR}/component-tasks"
                            
                            # Check if analysis file exists
                            if [ ! -f "\${ANALYSIS_DIR}/${params.OUTPUT_FILE}" ]; then
                                echo "[ERROR] Analysis file not found: \${ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                                echo "  Available files in \${ANALYSIS_DIR}:"
                                ls -la \${ANALYSIS_DIR}/ || echo "  (directory does not exist)"
                                exit 1
                            fi
                            
                            # Check if script exists
                            if [ ! -f "scripts/create-component-tasks.py" ]; then
                                echo "[ERROR] Script not found: scripts/create-component-tasks.py"
                                exit 1
                            fi
                            
                            # Run the script
                            python3 scripts/create-component-tasks.py \\
                                "\${ANALYSIS_DIR}/${params.OUTPUT_FILE}" \\
                                "\${ANALYSIS_DIR}/component-tasks"
                            
                            EXIT_CODE=\$?
                            if [ \$EXIT_CODE -ne 0 ]; then
                                echo "[ERROR] Script exited with code \$EXIT_CODE"
                                exit \$EXIT_CODE
                            fi
                            
                            echo ""
                            echo "[INFO] Generated component task files:"
                            ls -lh \${ANALYSIS_DIR}/component-tasks/ 2>/dev/null || {
                                echo "[ERROR] component-tasks directory not created"
                                exit 1
                            }
                            
                            FILE_COUNT=\$(ls \${ANALYSIS_DIR}/component-tasks/ | wc -l)
                            echo "[INFO] Total files created: \$FILE_COUNT"
                            
                            if [ \$FILE_COUNT -eq 0 ]; then
                                echo "[ERROR] No task files were created"
                                exit 1
                            fi
                        """

                        echo "[OK] Component task files created in ${ANALYSIS_DIR}/component-tasks"

                    } catch (Exception e) {
                        echo "[ERROR] Failed to create component tasks: ${e.message}"
                        echo "[INFO] This stage requires the AI analysis to complete successfully first"
                        error("Component task generation failed")
                    }
                }
            }
        }
        
        stage('Generate Implementation Plan') {
            when {
                expression { params.USE_AI_AGENTS == true }
            }
            steps {
                echo "[PLAN] Generating suggested implementation plan..."
                
                script {
                    try {
                        sh """#!/bin/bash
                            cd ${WORKSPACE}
                            
                            chmod +x scripts/generate-implementation-plan.py
                            python3 scripts/generate-implementation-plan.py \\
                                "${ANALYSIS_DIR}" \\
                                "implementation-plan.md"
                        """
                        
                        echo "[OK] Implementation plan generated successfully"
                        
                    } catch (Exception e) {
                        echo "[WARN] Could not generate implementation plan: ${e.message}"
                    }
                }
            }
        }
        
        stage('Fallback: Manual Analysis') {
            when {
                expression { params.USE_AI_AGENTS == false }
            }
            steps {
                echo "[DOC] Running manual (hardcoded) analysis..."
                
                script {
                    def manualReport = """# Manual Feature Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}
**Mode**: Manual (AI agents disabled)

## Note
This is a fallback manual analysis. For dynamic AI-driven analysis that automatically 
orchestrates agents, enable USE_AI_AGENTS parameter.

## Agent A - Frontend Analysis
- Mobile app changes needed
- Web app updates required
- API integration required

## Next Steps
1. Enable AI agents for detailed analysis
2. Ensure Ollama is running
3. Re-run pipeline with USE_AI_AGENTS=true
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}", text: manualReport
                    echo "[OK] Manual report generated"
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                echo "[ARCHIVE] Archiving analysis results..."
                
                script {
                    // Archive only the analysis reports and component tasks
                    archiveArtifacts artifacts: "analysis-reports/**/*.md", 
                                     allowEmptyArchive: true
                    
                    // List generated files
                    sh '''
                        echo ""
                        echo "[INFO] Generated Files:"
                        echo "=================="
                        echo "[DOC] Analysis Report:"
                        ls -lh ${ANALYSIS_DIR}/*.md | grep -v implementation
                        echo ""
                        echo "[PLAN] Implementation Plan:"
                        ls -lh ${ANALYSIS_DIR}/implementation-plan.md 2>/dev/null || echo "  (not generated)"
                        echo ""
                        if [ -d "${ANALYSIS_DIR}/component-tasks" ]; then
                            echo "[TASKS] Component Task Files:"
                            ls -lh ${ANALYSIS_DIR}/component-tasks/
                            echo "  Total: $(ls ${ANALYSIS_DIR}/component-tasks/ | wc -l) files"
                        else
                            echo "[TASKS] Component tasks: (not generated)"
                        fi
                    '''
                    
                    echo "[OK] Results archived"
                    echo ""
                    echo "[DOC] Report saved to: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                    echo "[PLAN] Implementation plan: ${env.ANALYSIS_DIR}/implementation-plan.md"
                    echo "[TASKS] Component tasks: ${env.ANALYSIS_DIR}/component-tasks/"
                }
            }
        }
    }
    
    post {
        success {
            echo "[OK] Feature analysis completed successfully!"
            echo ""
            echo "[INFO] Results:"
            echo "  - Analysis Report: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
            echo "  - Implementation Plan: ${env.ANALYSIS_DIR}/implementation-plan.md"
            echo "  - Component Tasks: ${env.ANALYSIS_DIR}/component-tasks/"
            echo ""
            echo "[AI] Agents were dynamically orchestrated based on AI analysis"
            echo "[TASKS] Component-specific task files with code templates created"
            
            script {
                if (params.USE_MOCK_DATA == true) {
                    echo ""
                    echo "[MOCK] B1 mock data server is still running"
                    echo "  - Access at: http://localhost:3001/api/monitoring/tire-pressure/{carId}"
                    echo "  - Stop with: lsof -ti:3001 | xargs kill"
                }
            }
        }
        failure {
            echo "[ERROR] Feature analysis failed"
            echo "Check the logs for details"
        }
        always {
            echo ""
            echo "Pipeline completed at: " + new Date().toString()
        }
    }
}
