#!/usr/bin/env python3
"""
AI Agent Coordinator - Dynamic Multi-Agent Analysis System
Uses Ollama to dynamically coordinate agents and generate analysis
"""

import json
import requests
import sys
import os
from typing import Dict, List, Optional

class OllamaClient:
    def __init__(self, host: str = "http://10.0.2.2:11434", model: str = "llama3:8b"):
        self.host = host
        self.model = model  # Model name from Ollama
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from Ollama"""
        try:
            url = f"{self.host}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Request JSON format
                "options": {
                    "temperature": 0.7,  # Balance creativity and consistency
                    "top_p": 0.9
                }
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}", file=sys.stderr)
            return ""

class Agent:
    def __init__(self, name: str, role: str, responsibilities: List[str], ollama: OllamaClient):
        self.name = name
        self.role = role
        self.responsibilities = responsibilities
        self.ollama = ollama
        self.analysis_result = None
    
    def analyze(self, feature_request: str, context: Dict = None) -> Dict:
        """Analyze feature request using AI"""
        system_prompt = f"""You are {self.name}, a {self.role} in a car rental system.
Your responsibilities: {', '.join(self.responsibilities)}

You must respond ONLY with valid JSON. Do not include any explanatory text before or after the JSON.

Required JSON structure:
{{
  "impact": "string describing the impact",
  "components": ["component1", "component2"],
  "changes": ["change1", "change2"],
  "needs_agent_b": true or false,
  "needs_agent_c": true or false,
  "effort_hours": number,
  "risks": ["risk1", "risk2"]
}}
"""
        
        context_str = ""
        if context:
            context_str = f"\n\nContext from other agents:\n{json.dumps(context, indent=2)}"
        
        prompt = f"""Feature Request: {feature_request}{context_str}

Analyze this feature request from your perspective as {self.name}.

Determine:
1. Impact on your components
2. What changes are required
3. Whether you need Agent B (Backend) - set needs_agent_b to true/false
4. Whether you need Agent C (In-Car Systems) - set needs_agent_c to true/false
5. Estimated effort in hours
6. Potential risks

Respond with ONLY a JSON object, no other text:"""
        
        response = self.ollama.generate(prompt, system_prompt)
        
        # Debug: print raw response
        print(f"\n--- Raw response from {self.name} ---", file=sys.stderr)
        print(response[:500], file=sys.stderr)  # First 500 chars
        print("--- End raw response ---\n", file=sys.stderr)
        
        # Try to parse JSON from response
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                # Remove markdown code fences
                lines = cleaned.split('\n')
                # Remove first line (```json or ```)
                if lines[0].startswith('```'):
                    lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned = '\n'.join(lines)
            
            # Find JSON in response (might have extra text)
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                analysis = json.loads(json_str)
                
                # Validate required keys
                required_keys = ['impact', 'components', 'changes', 'needs_agent_b', 'needs_agent_c', 'effort_hours', 'risks']
                missing_keys = [key for key in required_keys if key not in analysis]
                
                if missing_keys:
                    print(f"Warning: Missing keys in {self.name} response: {missing_keys}", file=sys.stderr)
                    # Fill in missing keys with defaults
                    for key in missing_keys:
                        if key in ['needs_agent_b', 'needs_agent_c']:
                            analysis[key] = False
                        elif key == 'effort_hours':
                            analysis[key] = 0
                        elif key in ['components', 'changes', 'risks']:
                            analysis[key] = []
                        else:
                            analysis[key] = "Not provided"
                
                self.analysis_result = analysis
                return analysis
            else:
                print(f"Warning: No JSON object found in {self.name} response", file=sys.stderr)
                return self._create_default_analysis(feature_request)
                
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON from {self.name}: {e}", file=sys.stderr)
            print(f"Attempted to parse: {json_str[:200] if 'json_str' in locals() else 'N/A'}", file=sys.stderr)
            return self._create_default_analysis(feature_request)
    
    def _create_default_analysis(self, feature_request: str) -> Dict:
        """Create default analysis structure if AI fails"""
        return {
            "impact": f"Analyzing impact of: {feature_request}",
            "components": ["Unknown"],
            "changes": ["Analysis needed"],
            "needs_agent_b": False,
            "needs_agent_c": False,
            "effort_hours": 0,
            "risks": ["AI analysis unavailable"]
        }

class AgentCoordinator:
    def __init__(self, ollama_host: str = "http://10.0.2.2:11434", model: str = "llama3:8b"):
        self.ollama = OllamaClient(ollama_host, model)
        
        # Define agents
        self.agent_a = Agent(
            name="Agent A",
            role="Frontend Developer & Coordinator",
            responsibilities=[
                "React Native mobile app (A1)",
                "React web staff app (A2)",
                "User interface design",
                "API integration",
                "Coordinate between all agents"
            ],
            ollama=self.ollama
        )
        
        self.agent_b = Agent(
            name="Agent B",
            role="Backend Developer",
            responsibilities=[
                "REST API server (B1)",
                "IoT Gateway (B2)",
                "MongoDB database (B3)",
                "PostgreSQL database (B4)",
                "WebSocket communications"
            ],
            ollama=self.ollama
        )
        
        self.agent_c = Agent(
            name="Agent C",
            role="In-Car Systems Developer",
            responsibilities=[
                "Cloud communication (C1)",
                "Redis message broker (C2)",
                "CAN bus interface (C3)",
                "Vehicle controller (C4)",
                "Data sensors (C5)"
            ],
            ollama=self.ollama
        )
    
    def coordinate(self, feature_request: str) -> Dict:
        """Coordinate agents to analyze feature request"""
        print(f"🤖 Starting AI-driven analysis for: {feature_request}")
        
        results = {
            "feature_request": feature_request,
            "agents_involved": [],
            "analyses": {}
        }
        
        # Step 1: Agent A analyzes and determines needs
        print("📊 Agent A: Analyzing request and determining dependencies...")
        agent_a_result = self.agent_a.analyze(feature_request)
        results["agents_involved"].append("Agent A")
        results["analyses"]["agent_a"] = agent_a_result
        
        # Step 2: If Agent A needs Backend, invoke Agent B
        if agent_a_result.get("needs_agent_b", False):
            print("📊 Agent B: Backend analysis needed...")
            context = {"agent_a_analysis": agent_a_result}
            agent_b_result = self.agent_b.analyze(feature_request, context)
            results["agents_involved"].append("Agent B")
            results["analyses"]["agent_b"] = agent_b_result
            
            # Step 3: If Agent B needs In-Car, invoke Agent C
            if agent_b_result.get("needs_agent_c", False):
                print("📊 Agent C: In-car system analysis needed...")
                context = {
                    "agent_a_analysis": agent_a_result,
                    "agent_b_analysis": agent_b_result
                }
                agent_c_result = self.agent_c.analyze(feature_request, context)
                results["agents_involved"].append("Agent C")
                results["analyses"]["agent_c"] = agent_c_result
        
        # Step 3 (alternative): If Agent A directly needs Agent C
        elif agent_a_result.get("needs_agent_c", False):
            print("📊 Agent C: In-car system analysis needed...")
            context = {"agent_a_analysis": agent_a_result}
            agent_c_result = self.agent_c.analyze(feature_request, context)
            results["agents_involved"].append("Agent C")
            results["analyses"]["agent_c"] = agent_c_result
        
        # Calculate total effort
        total_effort = sum(
            analysis.get("effort_hours", 0) 
            for analysis in results["analyses"].values()
        )
        results["total_effort_hours"] = total_effort
        
        return results
    
    def generate_code_examples(self, results: Dict, output_dir: str):
        """Generate code examples based on analysis"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        feature_request = results['feature_request']
        
        print("💻 Generating code examples...")
        
        # Generate frontend code examples if Agent A was involved
        if "agent_a" in results["analyses"]:
            self._generate_frontend_code(feature_request, output_dir)
        
        # Generate backend code examples if Agent B was involved
        if "agent_b" in results["analyses"]:
            self._generate_backend_code(feature_request, output_dir)
        
        # Generate in-car code examples if Agent C was involved
        if "agent_c" in results["analyses"]:
            self._generate_incar_code(feature_request, output_dir)
        
        print(f"✅ Code examples saved to {output_dir}/")
    
    def _generate_frontend_code(self, feature_request: str, output_dir: str):
        """Generate frontend code examples using AI"""
        system_prompt = """You are a React Native expert. Generate clean, production-ready code with proper formatting.
- Use 2-space indentation
- Add proper imports at the top
- Use functional components with hooks
- Include JSDoc comments for main component
- Format with proper line breaks and spacing
Output ONLY the code itself with no JSON wrapping, no explanations."""
        
        prompt = f"""Generate a well-formatted React Native component for: {feature_request}

Include:
- All necessary imports (React, useState, useEffect, StyleSheet)
- JSDoc comment for the component
- Component with hooks (useState, useEffect)
- API integration with fetch or axios
- Real-time WebSocket updates if needed
- Error handling with try-catch
- StyleSheet for component styling
- PropTypes or TypeScript types
- Export statement

Write complete, properly indented working code:"""
        
        code_response = self.ollama.generate(prompt, system_prompt)
        
        # Clean up code fences if present
        code = code_response.replace('```javascript', '').replace('```jsx', '').replace('```typescript', '').replace('```', '').strip()
        
        # If still wrapped in JSON, try to extract
        if code.startswith('{') and '"component"' in code:
            try:
                import json
                data = json.loads(code)
                code = data.get('component', code)
            except:
                pass
        
        # Ensure proper formatting
        lines = code.split('\n')
        formatted_lines = []
        for line in lines:
            # Remove excessive blank lines (keep max 1)
            if line.strip() or (formatted_lines and formatted_lines[-1].strip()):
                formatted_lines.append(line)
        
        formatted_code = '\n'.join(formatted_lines)
        
        with open(f"{output_dir}/frontend-component.jsx", 'w') as f:
            f.write("/**\n")
            f.write(" * Auto-generated React Native Component\n")
            f.write(f" * Feature: {feature_request}\n")
            f.write(" * Generated by AI Agent Coordinator\n")
            f.write(" */\n\n")
            f.write(formatted_code)
            f.write("\n")  # Ensure file ends with newline
        
        print("  ✅ Frontend component example created")
    
    def _generate_backend_code(self, feature_request: str, output_dir: str):
        """Generate backend code examples using AI"""
        system_prompt = """You are a Node.js/Express expert. Generate clean, production-ready code with proper formatting.
- Use 2-space indentation
- Add proper imports/requires at the top
- Include JSDoc comments for functions
- Format with proper line breaks and spacing
Output ONLY the code itself with no JSON wrapping, no explanations."""
        
        prompt = f"""Generate well-formatted Node.js backend code for: {feature_request}

Include:
- All necessary requires (express, mongoose, socket.io)
- JSDoc comments for main functions
- Express.js routes with proper HTTP methods
- MongoDB schema and CRUD operations
- WebSocket event handlers
- Input validation (express-validator or joi)
- Error handling middleware
- Async/await with try-catch
- Module exports

Write complete, properly indented working code:"""
        
        code_response = self.ollama.generate(prompt, system_prompt)
        
        # Clean up code fences
        code = code_response.replace('```javascript', '').replace('```js', '').replace('```', '').strip()
        
        # Format code
        lines = code.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip() or (formatted_lines and formatted_lines[-1].strip()):
                formatted_lines.append(line)
        
        formatted_code = '\n'.join(formatted_lines)
        
        with open(f"{output_dir}/backend-api.js", 'w') as f:
            f.write("/**\n")
            f.write(" * Auto-generated Node.js Backend API\n")
            f.write(f" * Feature: {feature_request}\n")
            f.write(" * Generated by AI Agent Coordinator\n")
            f.write(" */\n\n")
            f.write(formatted_code)
            f.write("\n")
        
        print("  ✅ Backend API example created")
    
    def _generate_incar_code(self, feature_request: str, output_dir: str):
        """Generate in-car system code examples using AI"""
        system_prompt = """You are a Python IoT expert. Generate clean, production-ready code with proper formatting.
- Use 4-space indentation (PEP 8)
- Add docstrings for functions and classes
- Include proper imports at the top
- Format with proper line breaks and spacing
Output ONLY the code itself with no JSON wrapping, no explanations."""
        
        prompt = f"""Generate well-formatted Python sensor code for: {feature_request}

Include:
- All necessary imports (redis, json, logging, time, etc.)
- Module-level docstring
- Class or functions with docstrings
- Sensor data reading/simulation logic
- Redis pub/sub integration
- JSON data formatting
- Error handling with try-except
- Logging configuration and usage
- Continuous operation loop with proper exit handling
- Type hints if appropriate

Write complete, properly indented PEP 8 compliant code:"""
        
        code_response = self.ollama.generate(prompt, system_prompt)
        
        # Clean up code fences
        code = code_response.replace('```python', '').replace('```py', '').replace('```', '').strip()
        
        # Format code
        lines = code.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip() or (formatted_lines and formatted_lines[-1].strip()):
                formatted_lines.append(line)
        
        formatted_code = '\n'.join(formatted_lines)
        
        with open(f"{output_dir}/sensor-integration.py", 'w') as f:
            f.write('"""\n')
            f.write("Auto-generated Python Sensor Integration\n")
            f.write(f"Feature: {feature_request}\n")
            f.write("Generated by AI Agent Coordinator\n")
            f.write('"""\n\n')
            f.write(formatted_code)
            f.write("\n")
        
        print("  ✅ Sensor integration example created")
    
    def generate_ui_mockup(self, results: Dict, output_dir: str):
        """Generate UI description/mockup"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        feature_request = results['feature_request']
        
        print("🎨 Generating UI design specifications...")
        
        prompt = f"""Create a detailed UI/UX design specification for: {feature_request}

IMPORTANT: Create ASCII art mockups using these box-drawing characters:
- Horizontal lines: ─ (use ─ not -)
- Vertical lines: │ (use │ not |)
- Corners: ┌ ┐ └ ┘
- Intersections: ├ ┤ ┬ ┴ ┼
- Use these consistently for clean box drawings

Include:
1. ASCII art screen layout (use the box-drawing characters above)
2. Component placement with labels
3. Color scheme (#hex codes)
4. User interaction flows
5. Responsive design notes
6. Accessibility considerations

Example format:
┌─────────────────────────────────┐
│  Header / Title                 │
├─────────────────────────────────┤
│  [Button] Content Area          │
│  ┌───────────────────┐          │
│  │  Component Box    │          │
│  └───────────────────┘          │
└─────────────────────────────────┘

Create professional ASCII mockups using these characters."""
        
        ui_spec = self.ollama.generate(prompt)
        
        with open(f"{output_dir}/ui-design-spec.md", 'w') as f:
            f.write(f"# UI Design Specification\n\n")
            f.write(f"**Feature**: {feature_request}\n\n")
            f.write("---\n\n")
            f.write(ui_spec)
            f.write("\n\n---\n\n")
            f.write("*Generated by AI Agent Coordinator*\n")
        
        print(f"  ✅ UI design spec saved")
    
    def generate_report(self, results: Dict, output_file: str):
        """Generate markdown report from analysis results"""
        with open(output_file, 'w') as f:
            f.write(f"# AI-Driven Feature Analysis Report\n\n")
            f.write(f"**Feature Request**: {results['feature_request']}\n\n")
            f.write(f"**Agents Involved**: {', '.join(results['agents_involved'])}\n\n")
            f.write(f"**Total Estimated Effort**: {results['total_effort_hours']} hours\n\n")
            f.write("---\n\n")
            
            # Agent A Analysis
            if "agent_a" in results["analyses"]:
                a = results["analyses"]["agent_a"]
                f.write("## Agent A - Frontend Analysis\n\n")
                f.write(f"**Impact**: {a.get('impact', 'N/A')}\n\n")
                f.write("**Components Affected**:\n")
                for comp in a.get('components', []):
                    f.write(f"- {comp}\n")
                f.write("\n**Required Changes**:\n")
                for change in a.get('changes', []):
                    f.write(f"- {change}\n")
                f.write(f"\n**Estimated Effort**: {a.get('effort_hours', 0)} hours\n\n")
                f.write("**Risks**:\n")
                for risk in a.get('risks', []):
                    f.write(f"- {risk}\n")
                f.write("\n---\n\n")
            
            # Agent B Analysis
            if "agent_b" in results["analyses"]:
                b = results["analyses"]["agent_b"]
                f.write("## Agent B - Backend Analysis\n\n")
                f.write(f"**Impact**: {b.get('impact', 'N/A')}\n\n")
                f.write("**Components Affected**:\n")
                for comp in b.get('components', []):
                    f.write(f"- {comp}\n")
                f.write("\n**Required Changes**:\n")
                for change in b.get('changes', []):
                    f.write(f"- {change}\n")
                f.write(f"\n**Estimated Effort**: {b.get('effort_hours', 0)} hours\n\n")
                f.write("**Risks**:\n")
                for risk in b.get('risks', []):
                    f.write(f"- {risk}\n")
                f.write("\n---\n\n")
            
            # Agent C Analysis
            if "agent_c" in results["analyses"]:
                c = results["analyses"]["agent_c"]
                f.write("## Agent C - In-Car Systems Analysis\n\n")
                f.write(f"**Impact**: {c.get('impact', 'N/A')}\n\n")
                f.write("**Components Affected**:\n")
                for comp in c.get('components', []):
                    f.write(f"- {comp}\n")
                f.write("\n**Required Changes**:\n")
                for change in c.get('changes', []):
                    f.write(f"- {change}\n")
                f.write(f"\n**Estimated Effort**: {c.get('effort_hours', 0)} hours\n\n")
                f.write("**Risks**:\n")
                for risk in c.get('risks', []):
                    f.write(f"- {risk}\n")
                f.write("\n---\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"This analysis was generated dynamically using AI.\n")
            f.write(f"Total effort across all agents: {results['total_effort_hours']} hours\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: ai-agent-coordinator.py '<feature_request>' [output_file] [ollama_host] [model]")
        sys.exit(1)
    
    feature_request = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis-report.md"
    ollama_host = sys.argv[3] if len(sys.argv) > 3 else "http://10.0.2.2:11434"
    model = sys.argv[4] if len(sys.argv) > 4 else "llama3:8b"
    
    # Determine output directory
    import os
    output_dir = os.path.dirname(output_file) if output_file else "."
    code_examples_dir = os.path.join(output_dir, "code-examples")
    
    # Create coordinator and run analysis
    coordinator = AgentCoordinator(ollama_host, model)
    results = coordinator.coordinate(feature_request)
    
    # Generate report
    coordinator.generate_report(results, output_file)
    
    # Generate code examples
    coordinator.generate_code_examples(results, code_examples_dir)
    
    # Generate UI mockup
    coordinator.generate_ui_mockup(results, code_examples_dir)
    
    # Output JSON for Jenkins to parse
    print("\n" + "="*50)
    print("JSON Results:")
    print(json.dumps(results, indent=2))
    
    print(f"\n✅ Analysis complete!")
    print(f"  📄 Report: {output_file}")
    print(f"  💻 Code examples: {code_examples_dir}/")
    print(f"  🎨 UI spec: {code_examples_dir}/ui-design-spec.md")

if __name__ == "__main__":
    main()
