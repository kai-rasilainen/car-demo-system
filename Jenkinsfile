pipeline {
    agent any
    
    parameters {
        string(
            name: 'FEATURE_REQUEST',
            defaultValue: 'Add tire pressure monitoring to the car dashboard',
            description: 'Describe the feature you want to analyze - will be sent to Agent A who will coordinate with other agents as needed'
        )
        booleanParam(
            name: 'USE_AI_COORDINATION',
            defaultValue: true,
            description: 'Use AI to dynamically coordinate agents and generate analysis (requires Ollama)'
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
                echo "🧹 Cleaning workspace..."
                deleteDir()
                echo "✅ Workspace cleaned"
            }
        }
        
        stage('Checkout') {
            steps {
                echo "📥 Checking out code..."
                checkout scm
                echo "✅ Code checked out"
            }
        }
        
        stage('Setup') {
            steps {
                echo "🤖 AI-Driven Multi-Agent Feature Analysis"
                echo "=========================================="
                echo "Request: ${params.FEATURE_REQUEST}"
                echo "AI Coordination: ${params.USE_AI_COORDINATION}"
                echo "Model: ${params.OLLAMA_MODEL}"
                echo "Timestamp: ${env.TIMESTAMP}"
                echo ""
                echo "Flow: Agent A → AI decides if B needed → AI decides if C needed"
                
                sh '''
                    mkdir -p ${ANALYSIS_DIR}
                    chmod +x scripts/ai-agent-coordinator.py
                '''
            }
        }
        
        stage('Validate Ollama') {
            when {
                expression { params.USE_AI_COORDINATION == true }
            }
            steps {
                script {
                    echo "🔍 Checking Ollama connection..."
                    try {
                        sh '''
                            curl -s ${OLLAMA_HOST}/api/tags > /dev/null || {
                                echo "❌ Cannot connect to Ollama at ${OLLAMA_HOST}"
                                echo "Please ensure Ollama is running"
                                exit 1
                            }
                            echo "✅ Ollama is available at ${OLLAMA_HOST}"
                            
                            # Check if model is available
                            if curl -s ${OLLAMA_HOST}/api/tags | grep -q "llama3:8b"; then
                                echo "✅ Model llama3:8b is available"
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
        
        stage('AI Agent Coordination') {
            when {
                expression { params.USE_AI_COORDINATION == true }
            }
            steps {
                echo "🤖 Running AI-driven agent coordination..."
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
                                2>&1 | tee ${ANALYSIS_DIR}/coordination-log.txt
                            
                            EXIT_CODE=\${PIPESTATUS[0]}
                            
                            if [ \$EXIT_CODE -ne 0 ]; then
                                echo "❌ AI coordination failed with exit code \$EXIT_CODE"
                                exit \$EXIT_CODE
                            fi
                            
                            echo "✅ AI coordination completed successfully"
                        """
                        
                        // Read and display the results
                        def report = readFile("${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}")
                        echo "\n📊 Generated Report Preview:"
                        echo "=" * 50
                        echo report.take(500) + "..."
                        
                    } catch (Exception e) {
                        error("AI coordination failed: ${e.message}")
                    }
                }
            }
        }
        
        stage('Fallback: Manual Analysis') {
            when {
                expression { params.USE_AI_COORDINATION == false }
            }
            steps {
                echo "📝 Running manual (hardcoded) analysis..."
                
                script {
                    def manualReport = """# Manual Feature Analysis Report

**Feature Request**: ${params.FEATURE_REQUEST}
**Generated**: ${env.TIMESTAMP}
**Mode**: Manual (AI coordination disabled)

## Note
This is a fallback manual analysis. For dynamic AI-driven analysis that automatically 
coordinates between agents, enable USE_AI_COORDINATION parameter.

## Agent A - Frontend Analysis
- Mobile app changes needed
- Web app updates required
- API integration required

## Next Steps
1. Enable AI coordination for detailed analysis
2. Ensure Ollama is running
3. Re-run pipeline with USE_AI_COORDINATION=true
"""
                    
                    writeFile file: "${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}", text: manualReport
                    echo "✅ Manual report generated"
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                echo "📦 Archiving analysis results..."
                
                script {
                    // Archive the report and code examples
                    archiveArtifacts artifacts: "analysis-reports/**/*.md, analysis-reports/**/*.txt, analysis-reports/**/code-examples/**/*", 
                                     allowEmptyArchive: true
                    
                    // List generated files
                    sh '''
                        echo ""
                        echo "📋 Generated Files:"
                        echo "=================="
                        if [ -d "${ANALYSIS_DIR}/code-examples" ]; then
                            echo "💻 Code Examples:"
                            ls -lh ${ANALYSIS_DIR}/code-examples/
                        fi
                    '''
                    
                    echo "✅ Results archived"
                    echo ""
                    echo "📄 Report saved to: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
                    echo "💻 Code examples: ${env.ANALYSIS_DIR}/code-examples/"
                }
            }
        }
    }
    
    post {
        success {
            echo "✅ Feature analysis completed successfully!"
            echo ""
            echo "📊 Results:"
            echo "  - Report: ${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}"
            echo "  - Code examples: ${env.ANALYSIS_DIR}/code-examples/"
            echo "    • frontend-component.jsx"
            echo "    • backend-api.js"
            echo "    • sensor-integration.py"
            echo "    • ui-design-spec.md"
            echo "  - Log: ${env.ANALYSIS_DIR}/coordination-log.txt"
            echo ""
            echo "💡 Agents were dynamically coordinated based on AI analysis"
            echo "💻 Code examples generated automatically"
        }
        failure {
            echo "❌ Feature analysis failed"
            echo "Check the logs for details"
        }
        always {
            echo ""
            echo "Pipeline completed at: " + new Date().toString()
        }
    }
}
