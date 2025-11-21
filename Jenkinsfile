pipeline {
    agent any
    
    parameters {
        string(
            name: 'FEATURE_REQUEST',
            defaultValue: 'Add tire pressure monitoring to the car dashboard',
            description: 'Describe the feature you want to analyze - will be sent to Agent A who will coordinate with other agents as needed'
        )
        booleanParam(
            name: 'USE_AI_AGENTS',
            defaultValue: true,
            description: 'Use AI to dynamically orchestrate agents and generate analysis (requires Ollama)'
        )
        string(
            name: 'OLLAMA_MODEL',
            defaultValue: 'llama3:8b',
            description: 'Ollama model to use (llama3:8b, codellama, mistral, etc.)'
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
                echo "Model: ${params.OLLAMA_MODEL}"
                echo "Timestamp: ${env.TIMESTAMP}"
                echo ""
                echo "Flow: Agent A → AI decides if B needed → AI decides if C needed"
                
                sh '''
                    mkdir -p ${ANALYSIS_DIR}
                    chmod +x scripts/ai-agent-coordinator.py
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
                    echo "🔍 Checking Ollama connection..."
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
                                echo "⚠️  Model llama3:8b may need to be pulled first"
                                echo "Run on Windows: ollama pull llama3:8b"
                            fi
                        '''
                    } catch (Exception e) {
                        error("Ollama is not available. Please start Ollama first.")
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
                            
                            echo "Starting AI coordinator..."
                            python3 scripts/ai-agent-coordinator.py \\
                                "${params.FEATURE_REQUEST}" \\
                                "${ANALYSIS_DIR}/${params.OUTPUT_FILE}" \\
                                "${OLLAMA_HOST}" \\
                                "${params.OLLAMA_MODEL}" \\
                                2>&1 | tee ${ANALYSIS_DIR}/agent-log.txt
                            
                            EXIT_CODE=\${PIPESTATUS[0]}
                            
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
                        sh '''#!/bin/bash
                            cd ${WORKSPACE}

                            python3 scripts/create-component-tasks.py \
                                "${ANALYSIS_DIR}/${params.OUTPUT_FILE}" \
                                "${ANALYSIS_DIR}/component-tasks"
                        '''

                        echo "[OK] Component task files created in ${ANALYSIS_DIR}/component-tasks"

                    } catch (Exception e) {
                        echo "[WARN] Failed to create component tasks: ${e.message}"
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
                    // Archive the report, implementation plan, and code examples
                    archiveArtifacts artifacts: "analysis-reports/**/*.md, analysis-reports/**/*.txt, analysis-reports/**/code-examples/**/*", 
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
                        if [ -d "${ANALYSIS_DIR}/code-examples" ]; then
                            echo "[CODE] Code Examples:"
                            ls -lh ${ANALYSIS_DIR}/code-examples/
                        fi
                    '''
                    
                    echo "[OK] Results archived"
                    echo ""
                    echo "[DOC] Report saved to: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                    echo "[PLAN] Implementation plan: ${env.ANALYSIS_DIR}/implementation-plan.md"
                    echo "[CODE] Code examples: ${env.ANALYSIS_DIR}/code-examples/"
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
            echo "  - Code examples: ${env.ANALYSIS_DIR}/code-examples/"
            echo "    • frontend-component.jsx"
            echo "    • backend-api.js"
            echo "    • sensor-integration.py"
            echo "    • ui-design-spec.md"
            echo "  - Agent Log: ${env.ANALYSIS_DIR}/agent-log.txt"
            echo ""
            echo "[AI] Agents were dynamically orchestrated based on AI analysis"
            echo "[CODE] Code examples generated automatically"
            echo "[PLAN] Step-by-step implementation plan created"
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
