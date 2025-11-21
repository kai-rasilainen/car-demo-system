#!/usr/bin/env python3
"""
Generate implementation plan from AI agent analysis results.
Reads agent-log.txt JSON output and creates a structured implementation plan.
"""

import json
import os
import sys

def extract_json_from_log(log_file):
    """Extract JSON data from agent log file."""
    if not os.path.exists(log_file):
        return None
    
    with open(log_file, 'r') as f:
        content = f.read()
        
    # Find JSON block in the log
    if '"feature_request"' not in content:
        return None
    
    start = content.find('{', content.find('JSON Results:'))
    if start == -1:
        return None
    
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
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def generate_implementation_plan(json_data, output_file):
    """Generate implementation plan markdown from analysis data."""
    
    with open(output_file, 'w') as f:
        f.write("# Implementation Plan\n\n")
        f.write(f"**Feature**: {json_data.get('feature_request', 'Unknown')}\n\n")
        f.write(f"**Total Estimated Effort**: {json_data.get('total_effort_hours', 0)} hours\n\n")
        
        f.write("---\n\n")
        f.write("## Implementation Phases\n\n")
        
        # Organize by component layers
        agents = json_data.get('agents_involved', [])
        analyses = json_data.get('analyses', {})
        
        # Phase 1: Backend/Database setup
        backend_agents = [a for a in agents if a.startswith('Agent-B') or a.startswith('Agent-C')]
        if backend_agents:
            f.write("### Phase 1: Backend & Data Layer\n\n")
            f.write("**Objective**: Set up backend APIs, databases, and data infrastructure\n\n")
            
            for agent in backend_agents:
                agent_key = agent.lower().replace('-', '_')
                analysis = analyses.get(agent_key, {})
                
                f.write(f"#### {agent}\n\n")
                f.write(f"**Effort**: {analysis.get('effort_hours', 0)} hours\n\n")
                
                if analysis.get('changes'):
                    f.write("**Tasks**:\n")
                    for change in analysis.get('changes', []):
                        f.write(f"- [ ] {change}\n")
                    f.write("\n")
                
                if analysis.get('risks'):
                    f.write("**Risks to Consider**:\n")
                    for risk in analysis.get('risks', []):
                        f.write(f"- [WARN] {risk}\n")
                    f.write("\n")
            
            f.write("---\n\n")
        
        # Phase 2: Frontend development
        frontend_agents = [a for a in agents if a.startswith('Agent-A')]
        if frontend_agents:
            f.write("### Phase 2: Frontend Development\n\n")
            f.write("**Objective**: Implement user-facing features and UI components\n\n")
            
            for agent in frontend_agents:
                agent_key = agent.lower().replace('-', '_')
                analysis = analyses.get(agent_key, {})
                
                f.write(f"#### {agent}\n\n")
                f.write(f"**Effort**: {analysis.get('effort_hours', 0)} hours\n\n")
                
                if analysis.get('changes'):
                    f.write("**Tasks**:\n")
                    for change in analysis.get('changes', []):
                        f.write(f"- [ ] {change}\n")
                    f.write("\n")
                
                if analysis.get('components'):
                    f.write("**Components to Update**:\n")
                    for comp in analysis.get('components', []):
                        f.write(f"- {comp}\n")
                    f.write("\n")
            
            f.write("---\n\n")
        
        # Testing & QA
        f.write("### Phase 3: Testing & Quality Assurance\n\n")
        f.write("**Objective**: Ensure feature works correctly end-to-end\n\n")
        f.write("**Tasks**:\n")
        f.write("- [ ] Unit tests for backend APIs\n")
        f.write("- [ ] Integration tests for data flow\n")
        f.write("- [ ] Frontend component tests\n")
        f.write("- [ ] End-to-end user flow testing\n")
        f.write("- [ ] Performance testing\n")
        f.write("- [ ] Security review\n\n")
        
        f.write("**Estimated Effort**: 4-8 hours\n\n")
        f.write("---\n\n")
        
        # Deployment
        f.write("### Phase 4: Deployment\n\n")
        f.write("**Objective**: Roll out feature to production\n\n")
        f.write("**Tasks**:\n")
        f.write("- [ ] Deploy backend services\n")
        f.write("- [ ] Update database migrations\n")
        f.write("- [ ] Deploy frontend updates\n")
        f.write("- [ ] Monitor system health\n")
        f.write("- [ ] Document new feature\n")
        f.write("- [ ] Train support team\n\n")
        
        f.write("**Estimated Effort**: 2-4 hours\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        total_with_testing = json_data.get('total_effort_hours', 0) + 6 + 3
        f.write(f"**Total Implementation Time**: {total_with_testing} hours ({total_with_testing/8:.1f} days)\n\n")
        f.write("**Recommended Team**:\n")
        if any('Agent-A' in a for a in agents):
            f.write("- Frontend Developer\n")
        if any('Agent-B' in a for a in agents):
            f.write("- Backend Developer\n")
        if any('Agent-C' in a for a in agents):
            f.write("- IoT/Embedded Systems Engineer\n")
        f.write("- QA Engineer\n")
        f.write("- DevOps Engineer\n\n")
        
        f.write("**Prerequisites**:\n")
        f.write("- Development environment set up\n")
        f.write("- Access to all required services\n")
        f.write("- Test data available\n")
        f.write("- Code review process in place\n\n")
        
        f.write("**Success Metrics**:\n")
        f.write("- All tests passing\n")
        f.write("- Feature meets acceptance criteria\n")
        f.write("- No performance degradation\n")
        f.write("- Documentation complete\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: generate-implementation-plan.py <analysis-dir> <output-file>")
        sys.exit(1)
    
    analysis_dir = sys.argv[1]
    output_file = sys.argv[2]
    
    # Read the analysis results from the JSON output
    log_file = os.path.join(analysis_dir, "agent-log.txt")
    
    json_data = extract_json_from_log(log_file)
    
    if not json_data:
        print("[WARN] Could not extract JSON from analysis")
        sys.exit(0)
    
    # Generate implementation plan
    plan_file = os.path.join(analysis_dir, output_file)
    generate_implementation_plan(json_data, plan_file)
    
    print(f"[OK] Implementation plan generated: {plan_file}")

if __name__ == "__main__":
    main()
