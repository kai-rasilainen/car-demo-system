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
        
        stage('AI Agent Coordination') {
            when {
                expression { params.USE_AI_COORDINATION == true }
            }
            steps {
                echo "[AI] Running AI-driven agent coordination..."
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
                                echo "[ERROR] AI coordination failed with exit code \$EXIT_CODE"
                                exit \$EXIT_CODE
                            fi
                            
                            echo "[OK] AI coordination completed successfully"
                        """
                        
                        // Read and display the results
                        def report = readFile("${env.ANALYSIS_DIR}/${params.OUTPUT_FILE}")
                        echo "\n[REPORT] Generated Report Preview:"
                        echo "=" * 50
                        echo report.take(500) + "..."
                        
                    } catch (Exception e) {
                        error("AI coordination failed: ${e.message}")
                    }
                }
            }
        }
        
        stage('Generate Implementation Plan') {
            when {
                expression { params.USE_AI_COORDINATION == true }
            }
            steps {
                echo "[PLAN] Generating suggested implementation plan..."
                
                script {
                    try {
                        sh """#!/bin/bash
                            cd ${WORKSPACE}
                            
                            # Create implementation plan based on analysis
                            python3 - << 'PYTHON_SCRIPT'
import json
import os
import sys

# Read the analysis results from the JSON output
analysis_dir = "${ANALYSIS_DIR}"
output_file = "${params.OUTPUT_FILE}"
plan_file = os.path.join(analysis_dir, "implementation-plan.md")

# Parse the coordination log to extract JSON results
log_file = os.path.join(analysis_dir, "coordination-log.txt")
json_data = None

if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        content = f.read()
        # Find JSON block in the log
        if '"feature_request"' in content:
            start = content.find('{', content.find('JSON Results:'))
            if start != -1:
                # Find matching closing brace
                brace_count = 0
                end = start
                for i in range(start, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                json_str = content[start:end]
                try:
                    json_data = json.loads(json_str)
                except:
                    pass

if not json_data:
    print("[WARN] Could not extract JSON from analysis")
    sys.exit(0)

# Generate implementation plan
with open(plan_file, 'w') as f:
    f.write("# Implementation Plan\\n\\n")
    f.write(f"**Feature**: {json_data.get('feature_request', 'Unknown')}\\n\\n")
    f.write(f"**Total Estimated Effort**: {json_data.get('total_effort_hours', 0)} hours\\n\\n")
    
    f.write("---\\n\\n")
    f.write("## Implementation Phases\\n\\n")
    
    # Organize by component layers
    agents = json_data.get('agents_involved', [])
    analyses = json_data.get('analyses', {})
    
    # Phase 1: Backend/Database setup
    backend_agents = [a for a in agents if a.startswith('Agent-B') or a.startswith('Agent-C')]
    if backend_agents:
        f.write("### Phase 1: Backend & Data Layer\\n\\n")
        f.write("**Objective**: Set up backend APIs, databases, and data infrastructure\\n\\n")
        
        for agent in backend_agents:
            agent_key = agent.lower().replace('-', '_')
            analysis = analyses.get(agent_key, {})
            
            f.write(f"#### {agent}\\n\\n")
            f.write(f"**Effort**: {analysis.get('effort_hours', 0)} hours\\n\\n")
            
            if analysis.get('changes'):
                f.write("**Tasks**:\\n")
                for change in analysis.get('changes', []):
                    f.write(f"- [ ] {change}\\n")
                f.write("\\n")
            
            if analysis.get('risks'):
                f.write("**Risks to Consider**:\\n")
                for risk in analysis.get('risks', []):
                    f.write(f"- [WARN] {risk}\\n")
                f.write("\\n")
        
        f.write("---\\n\\n")
    
    # Phase 2: Frontend development
    frontend_agents = [a for a in agents if a.startswith('Agent-A')]
    if frontend_agents:
        f.write("### Phase 2: Frontend Development\\n\\n")
        f.write("**Objective**: Implement user-facing features and UI components\\n\\n")
        
        for agent in frontend_agents:
            agent_key = agent.lower().replace('-', '_')
            analysis = analyses.get(agent_key, {})
            
            f.write(f"#### {agent}\\n\\n")
            f.write(f"**Effort**: {analysis.get('effort_hours', 0)} hours\\n\\n")
            
            if analysis.get('changes'):
                f.write("**Tasks**:\\n")
                for change in analysis.get('changes', []):
                    f.write(f"- [ ] {change}\\n")
                f.write("\\n")
            
            if analysis.get('components'):
                f.write("**Components to Update**:\\n")
                for comp in analysis.get('components', []):
                    f.write(f"- {comp}\\n")
                f.write("\\n")
        
        f.write("---\\n\\n")
    
    # Testing & QA
    f.write("### Phase 3: Testing & Quality Assurance\\n\\n")
    f.write("**Objective**: Ensure feature works correctly end-to-end\\n\\n")
    f.write("**Tasks**:\\n")
    f.write("- [ ] Unit tests for backend APIs\\n")
    f.write("- [ ] Integration tests for data flow\\n")
    f.write("- [ ] Frontend component tests\\n")
    f.write("- [ ] End-to-end user flow testing\\n")
    f.write("- [ ] Performance testing\\n")
    f.write("- [ ] Security review\\n\\n")
    
    f.write("**Estimated Effort**: 4-8 hours\\n\\n")
    f.write("---\\n\\n")
    
    # Deployment
    f.write("### Phase 4: Deployment\\n\\n")
    f.write("**Objective**: Roll out feature to production\\n\\n")
    f.write("**Tasks**:\\n")
    f.write("- [ ] Deploy backend services\\n")
    f.write("- [ ] Update database migrations\\n")
    f.write("- [ ] Deploy frontend updates\\n")
    f.write("- [ ] Monitor system health\\n")
    f.write("- [ ] Document new feature\\n")
    f.write("- [ ] Train support team\\n\\n")
    
    f.write("**Estimated Effort**: 2-4 hours\\n\\n")
    f.write("---\\n\\n")
    
    # Summary
    f.write("## Summary\\n\\n")
    total_with_testing = json_data.get('total_effort_hours', 0) + 6 + 3
    f.write(f"**Total Implementation Time**: {total_with_testing} hours ({total_with_testing/8:.1f} days)\\n\\n")
    f.write("**Recommended Team**:\\n")
    if any('Agent-A' in a for a in agents):
        f.write("- Frontend Developer\\n")
    if any('Agent-B' in a for a in agents):
        f.write("- Backend Developer\\n")
    if any('Agent-C' in a for a in agents):
        f.write("- IoT/Embedded Systems Engineer\\n")
    f.write("- QA Engineer\\n")
    f.write("- DevOps Engineer\\n\\n")
    
    f.write("**Prerequisites**:\\n")
    f.write("- Development environment set up\\n")
    f.write("- Access to all required services\\n")
    f.write("- Test data available\\n")
    f.write("- Code review process in place\\n\\n")
    
    f.write("**Success Metrics**:\\n")
    f.write("- All tests passing\\n")
    f.write("- Feature meets acceptance criteria\\n")
    f.write("- No performance degradation\\n")
    f.write("- Documentation complete\\n")

print(f"[OK] Implementation plan generated: {plan_file}")

PYTHON_SCRIPT
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
                expression { params.USE_AI_COORDINATION == false }
            }
            steps {
                echo "[DOC] Running manual (hardcoded) analysis..."
                
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
            echo "  - Coordination Log: ${env.ANALYSIS_DIR}/coordination-log.txt"
            echo ""
            echo "[AI] Agents were dynamically coordinated based on AI analysis"
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
