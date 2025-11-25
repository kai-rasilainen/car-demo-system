#!/usr/bin/env python3
"""
AI Agent Orchestrator - Dynamic Multi-Agent Analysis System
Uses Ollama to orchestrate independent agents and generate analysis
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
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, format_json: bool = True) -> str:
        """Generate response from Ollama"""
        try:
            url = f"{self.host}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Balance creativity and consistency
                    "top_p": 0.9
                }
            }
            if format_json:
                payload["format"] = "json"  # Request JSON format only when needed
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
    def __init__(self, name: str, component: str, role: str, responsibilities: List[str], 
                 apis: List[str], downstream_agents: List[str], ollama: OllamaClient):
        self.name = name
        self.component = component
        self.role = role
        self.responsibilities = responsibilities
        self.apis = apis  # APIs this agent exposes
        self.downstream_agents = downstream_agents  # Agents this one can call
        self.ollama = ollama
        self.analysis_result = None
    
    def analyze(self, feature_request: str, context: Dict = None) -> Dict:
        """Analyze feature request using AI"""
        
        # Build downstream agents info
        downstream_info = ""
        if self.downstream_agents:
            downstream_info = f"\n\nYou can request help from these downstream agents: {', '.join(self.downstream_agents)}"
            downstream_info += "\nFor each downstream agent, set needs_<agent_name> to true/false (e.g., needs_a1, needs_b2)"
        
        system_prompt = f"""You are {self.name}, a {self.role} responsible for {self.component}.
Your responsibilities: {', '.join(self.responsibilities)}
APIs you provide: {', '.join(self.apis) if self.apis else 'None'}
{downstream_info}

You must respond ONLY with valid JSON. Do not include any explanatory text before or after the JSON.

Required JSON structure:
{{
  "impact": "string describing the impact",
  "components": ["component1", "component2"],
  "changes": ["change1", "change2"],
  "effort_hours": number,
  "risks": ["risk1", "risk2"]"""
        
        # Add needs_* fields for downstream agents
        for agent in self.downstream_agents:
            agent_key = agent.lower().replace(" ", "_").replace("-", "_")
            system_prompt += f',\n  "needs_{agent_key}": true or false'
        
        system_prompt += "\n}"
        
        context_str = ""
        if context:
            context_str = f"\n\nContext from other agents:\n{json.dumps(context, indent=2)}"
        
        prompt = f"""Feature Request: {feature_request}{context_str}

Analyze this feature request from your perspective as {self.name} for {self.component}.

Determine:
1. Impact on your components
2. What changes are required in your area
3. Which downstream agents you need (set needs_<agent> flags)
4. Estimated effort in hours for your component
5. Potential risks

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
                
                # Validate required keys (dynamic based on downstream agents)
                required_keys = ['impact', 'components', 'changes', 'effort_hours', 'risks']
                missing_keys = [key for key in required_keys if key not in analysis]
                
                if missing_keys:
                    print(f"Warning: Missing keys in {self.name} response: {missing_keys}", file=sys.stderr)
                    # Fill in missing keys with defaults
                    for key in missing_keys:
                        if key == 'effort_hours':
                            analysis[key] = 0
                        elif key in ['components', 'changes', 'risks']:
                            analysis[key] = []
                        else:
                            analysis[key] = "Not provided"
                
                # Ensure needs_* fields exist for downstream agents
                for agent in self.downstream_agents:
                    agent_key = f"needs_{agent.lower().replace(' ', '_').replace('-', '_')}"
                    if agent_key not in analysis:
                        analysis[agent_key] = False
                
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
        analysis = {
            "impact": f"Analyzing impact of: {feature_request}",
            "components": ["Unknown"],
            "changes": ["Analysis needed"],
            "effort_hours": 0,
            "risks": ["AI analysis unavailable"]
        }
        # Add needs_* fields for downstream agents
        for agent in self.downstream_agents:
            agent_key = f"needs_{agent.lower().replace(' ', '_').replace('-', '_')}"
            analysis[agent_key] = False
        return analysis

class AgentOrchestrator:
    def __init__(self, ollama_host: str = "http://10.0.2.2:11434", model: str = "llama3:8b"):
        self.ollama = OllamaClient(ollama_host, model)
        
        # Define component-level agents with their downstream dependencies
        # Frontend Agents
        self.agent_a1 = Agent(
            name="Agent-A1",
            component="Car User Mobile App",
            role="React Native Mobile Developer",
            responsibilities=["User authentication", "Car browsing", "Booking management", "Real-time car status"],
            apis=["GET /bookings", "POST /booking", "GET /car-status"],
            downstream_agents=["Agent-B1", "Agent-B2"],
            ollama=self.ollama
        )
        
        self.agent_a2 = Agent(
            name="Agent-A2",
            component="Rental Staff Web App",
            role="React Web Developer",
            responsibilities=["Fleet management UI", "Booking administration", "Staff dashboard", "Reports"],
            apis=["GET /fleet", "PUT /car-status", "GET /reports"],
            downstream_agents=["Agent-B1", "Agent-B3", "Agent-B4"],
            ollama=self.ollama
        )
        
        # Backend Agents
        self.agent_b1 = Agent(
            name="Agent-B1",
            component="Web Server (REST API)",
            role="Node.js Backend Developer",
            responsibilities=["REST API endpoints", "Authentication", "Business logic", "Data validation"],
            apis=["/api/bookings", "/api/cars", "/api/users", "/api/fleet"],
            downstream_agents=["Agent-B3", "Agent-B4", "Agent-B2"],
            ollama=self.ollama
        )
        
        self.agent_b2 = Agent(
            name="Agent-B2",
            component="IoT Gateway",
            role="WebSocket/IoT Developer",
            responsibilities=["WebSocket server", "Real-time updates", "IoT device communication", "Event streaming"],
            apis=["ws://iot-gateway", "/api/iot/status", "/api/iot/command"],
            downstream_agents=["Agent-C1", "Agent-C2"],
            ollama=self.ollama
        )
        
        self.agent_b3 = Agent(
            name="Agent-B3",
            component="Realtime Database (MongoDB)",
            role="MongoDB Database Administrator",
            responsibilities=["Real-time data storage", "Car status", "IoT data", "Session management"],
            apis=["mongodb://realtime-db", "Collections: cars, sessions, iot_data"],
            downstream_agents=[],
            ollama=self.ollama
        )
        
        self.agent_b4 = Agent(
            name="Agent-B4",
            component="Static Database (PostgreSQL)",
            role="PostgreSQL Database Administrator",
            responsibilities=["Transactional data", "Users", "Bookings", "Fleet data", "Reports"],
            apis=["postgresql://static-db", "Tables: users, bookings, fleet, reports"],
            downstream_agents=[],
            ollama=self.ollama
        )
        
        # In-Car System Agents
        self.agent_c1 = Agent(
            name="Agent-C1",
            component="Cloud Communication",
            role="Python Cloud Integration Developer",
            responsibilities=["Cloud connectivity", "Data synchronization", "Remote commands", "Status updates"],
            apis=["HTTP client to IoT Gateway", "Redis pub/sub"],
            downstream_agents=["Agent-C2"],
            ollama=self.ollama
        )
        
        self.agent_c2 = Agent(
            name="Agent-C2",
            component="Central Broker (Redis)",
            role="Redis/Message Queue Administrator",
            responsibilities=["Message routing", "Pub/sub channels", "Data buffering", "Event distribution"],
            apis=["redis://broker", "Channels: car_status, commands, sensor_data"],
            downstream_agents=["Agent-C3", "Agent-C4", "Agent-C5"],
            ollama=self.ollama
        )
        
        self.agent_c3 = Agent(
            name="Agent-C3",
            component="CAN Bus Interface",
            role="CAN Bus Integration Developer",
            responsibilities=["CAN bus communication", "Vehicle network", "Protocol translation"],
            apis=["CAN interface", "Vehicle data access"],
            downstream_agents=[],
            ollama=self.ollama
        )
        
        self.agent_c4 = Agent(
            name="Agent-C4",
            component="Vehicle Controller",
            role="Embedded Systems Developer",
            responsibilities=["Vehicle control logic", "Command execution", "Safety checks", "State management"],
            apis=["Control commands", "Vehicle state"],
            downstream_agents=["Agent-C3"],
            ollama=self.ollama
        )
        
        self.agent_c5 = Agent(
            name="Agent-C5",
            component="Data Sensors",
            role="IoT Sensor Developer",
            responsibilities=["Sensor data collection", "GPS", "Fuel level", "Tire pressure", "Diagnostics"],
            apis=["Sensor readings", "GPS coordinates", "Vehicle telemetry"],
            downstream_agents=["Agent-C3"],
            ollama=self.ollama
        )
        
        # Agent registry for lookup
        self.agents = {
            "Agent-A1": self.agent_a1,
            "Agent-A2": self.agent_a2,
            "Agent-B1": self.agent_b1,
            "Agent-B2": self.agent_b2,
            "Agent-B3": self.agent_b3,
            "Agent-B4": self.agent_b4,
            "Agent-C1": self.agent_c1,
            "Agent-C2": self.agent_c2,
            "Agent-C3": self.agent_c3,
            "Agent-C4": self.agent_c4,
            "Agent-C5": self.agent_c5,
        }
    
    def orchestrate(self, feature_request: str) -> Dict:
        """Orchestrate agents to analyze feature request hierarchically"""
        print(f"[AI] Starting AI-driven hierarchical analysis for: {feature_request}")
        
        results = {
            "feature_request": feature_request,
            "agents_involved": [],
            "analyses": {},
            "call_tree": []
        }
        
        # Determine which frontend agents to start with based on feature keywords
        start_agents = []
        if any(word in feature_request.lower() for word in ['mobile', 'app', 'user', 'customer', 'booking']):
            start_agents.append("Agent-A1")
        if any(word in feature_request.lower() for word in ['staff', 'admin', 'fleet', 'report', 'dashboard']):
            start_agents.append("Agent-A2")
        
        # If no specific match, start with both frontend agents
        if not start_agents:
            start_agents = ["Agent-A1", "Agent-A2"]
        
        print(f"[INFO] Starting with: {', '.join(start_agents)}")
        
        # Analyze recursively starting from frontend agents
        context = {}
        for agent_name in start_agents:
            self._analyze_recursive(agent_name, feature_request, context, results, level=0)
        
        # Calculate total effort
        total_effort = sum(
            analysis.get("effort_hours", 0) 
            for analysis in results["analyses"].values()
        )
        results["total_effort_hours"] = total_effort
        
        return results
    
    def _analyze_recursive(self, agent_name: str, feature_request: str, 
                          context: Dict, results: Dict, level: int):
        """Recursively analyze feature with agent and its downstream dependencies"""
        indent = "  " * level
        agent = self.agents.get(agent_name)
        
        if not agent:
            print(f"{indent}[WARN] Agent {agent_name} not found")
            return
        
        if agent_name in results["agents_involved"]:
            print(f"{indent}[SKIP] {agent_name} already analyzed")
            return
        
        print(f"{indent}[ANALYZE] {agent_name} ({agent.component}): Analyzing...")
        
        # Analyze with current context
        analysis = agent.analyze(feature_request, context)
        results["agents_involved"].append(agent_name)
        results["analyses"][agent_name.lower().replace("-", "_")] = analysis
        results["call_tree"].append({"agent": agent_name, "level": level})
        
        # Update context for downstream agents
        context[agent_name] = analysis
        
        # Check which downstream agents are needed
        for downstream_agent in agent.downstream_agents:
            agent_key = f"needs_{downstream_agent.lower().replace('-', '_')}"
            if analysis.get(agent_key, False):
                print(f"{indent}  -> {agent_name} needs {downstream_agent}")
                self._analyze_recursive(downstream_agent, feature_request, context, results, level + 1)
    
    def generate_code_examples(self, results: Dict, output_dir: str):
        """Generate code examples based on analysis"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        feature_request = results['feature_request']
        
        print("[CODE] Generating code examples...")
        
        # Generate frontend code if any frontend agent (A1 or A2) was involved
        frontend_agents = [agent for agent in results['agents_involved'] if agent.startswith('Agent-A')]
        if frontend_agents:
            self._generate_frontend_code(feature_request, output_dir)
        
        # Generate backend code if any backend agent (B1-B4) was involved
        backend_agents = [agent for agent in results['agents_involved'] if agent.startswith('Agent-B')]
        if backend_agents:
            self._generate_backend_code(feature_request, output_dir)
        
        # Generate in-car code if any in-car agent (C1-C5) was involved
        incar_agents = [agent for agent in results['agents_involved'] if agent.startswith('Agent-C')]
        if incar_agents:
            self._generate_incar_code(feature_request, output_dir)
        
        print(f"[DONE] Code examples saved to {output_dir}/")
    
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
        
        code_response = self.ollama.generate(prompt, system_prompt, format_json=False)
        
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
            f.write(" * Generated by AI Agent Orchestrator\n")
            f.write(" */\n\n")
            f.write(formatted_code)
            f.write("\n")  # Ensure file ends with newline
        
        print("  [OK] Frontend component example created")
    
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
        
        code_response = self.ollama.generate(prompt, system_prompt, format_json=False)
        
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
            f.write(" * Auto-generated Express API Endpoint\n")
            f.write(f" * Feature: {feature_request}\n")
            f.write(" * Generated by AI Agent Orchestrator\n")
            f.write(" */\n\n")
            f.write(formatted_code)
            f.write("\n")
        
        print("  [OK] Backend API example created")
    
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
        
        code_response = self.ollama.generate(prompt, system_prompt, format_json=False)
        
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
            f.write("Generated by AI Agent Orchestrator\n")
            f.write('"""\n\n')
            f.write(formatted_code)
            f.write("\n")
        
        print("  [OK] Sensor integration example created")
    
    def generate_ui_mockup(self, results: Dict, output_dir: str):
        """Generate UI description/mockup with ASCII art"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        feature_request = results['feature_request']
        
        print("[UI] Generating UI design specifications...")
        
        # Get design details from AI
        prompt = f"""Analyze the UI/UX requirements for: {feature_request}

Provide a detailed specification including:
1. Main screen components (list them)
2. Color scheme with hex codes
3. Key user interactions
4. Layout structure (header, content areas, footer, etc.)
5. Responsive design considerations
6. Accessibility features

Be specific and detailed."""
        
        ui_details = self.ollama.generate(prompt, format_json=False)
        
        # Create ASCII art mockup using box-drawing characters
        mockup = self._create_ascii_mockup(feature_request)
        
        with open(f"{output_dir}/ui-design-spec.md", 'w') as f:
            f.write(f"# UI Design Specification\n\n")
            f.write(f"**Feature**: {feature_request}\n\n")
            f.write("## Screen Mockup\n\n")
            f.write("```\n")
            f.write(mockup)
            f.write("\n```\n\n")
            f.write("## Design Details\n\n")
            f.write(ui_details)
            f.write("\n\n---\n\n")
            f.write("*Generated by AI Agent Orchestrator*\n")
        
        print(f"  [OK] UI design spec saved")
    
    def _create_ascii_mockup(self, feature: str) -> str:
        """Create ASCII art mockup using box-drawing characters"""
        width = 70
        
        mockup = []
        
        # Check if feature is tire/pressure related
        is_tire_feature = any(word in feature.lower() for word in ['tire', 'tyre', 'pressure', 'wheel'])
        
        if is_tire_feature:
            # Tire pressure specific mockup
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("|                    TIRE PRESSURE MONITOR                         |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("|                                                                  |")
            mockup.append("|        FRONT LEFT              |             FRONT RIGHT         |")
            mockup.append("|       .-'''''''-.              |            .-'''''''-.          |")
            mockup.append("|      /           \\             |           /           \\         |")
            mockup.append("|     |             |            |          |             |        |")
            mockup.append("|     | [=======   ]|            |          | [========= ]|        |")
            mockup.append("|     |   2.2 bar   |            |          |   2.2 bar   |        |")
            mockup.append("|      \\           /             |           \\           /          |")
            mockup.append("|       '-.......-'              |            '-.......-'           |")
            mockup.append("|         [OK]                   |              [OK]               |")
            mockup.append("|                                |                                 |")
            mockup.append("|--------------------------------+-------------------------------- |")
            mockup.append("|                                                                  |")
            mockup.append("|        REAR LEFT               |             REAR RIGHT          |")
            mockup.append("|       .-'''''''-.              |            .-'''''''-.          |")
            mockup.append("|      /           \\             |           /           \\         |")
            mockup.append("|     |             |            |          |             |        |")
            mockup.append("|     | [======    ]|            |          | [====      ]|        |")
            mockup.append("|     |   2.1 bar   |            |          |   1.9 bar   |        |")
            mockup.append("|      \\           /             |           \\           /          |")
            mockup.append("|       '-.......-'              |            '-.......-'           |")
            mockup.append("|         [OK]                   |             [LOW!]              |")
            mockup.append("|                                                                  |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("| Status: 1 tire low pressure    | Last Update: 2 seconds ago      |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("| [Refresh] [History] [Alerts] [Settings]                          |")
            mockup.append("+------------------------------------------------------------------+")
        else:
            # Generic feature mockup
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("|  " + feature[:62].center(62) + "  |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("|  [Home]  [Dashboard]  [Settings]  [Profile]                      |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("|                                                                  |")
            mockup.append("|  Main Content Area:                                              |")
            mockup.append("|                                                                  |")
            mockup.append("|  +------------------------------------------------------------+  |")
            mockup.append("|  | Data Display / Visualization                              |  |")
            mockup.append("|  |                                                            |  |")
            mockup.append("|  | [=============>            ] 60%                           |  |")
            mockup.append("|  |                                                            |  |")
            mockup.append("|  +------------------------------------------------------------+  |")
            mockup.append("|                                                                  |")
            mockup.append("|  +------------------------------------------------------------+  |")
            mockup.append("|  | Interactive Controls                                       |  |")
            mockup.append("|  |                                                            |  |")
            mockup.append("|  |   [Start]    [Stop]    [Refresh]    [Export]              |  |")
            mockup.append("|  |                                                            |  |")
            mockup.append("|  +------------------------------------------------------------+  |")
            mockup.append("|                                                                  |")
            mockup.append("+------------------------------------------------------------------+")
            mockup.append("| Status: Active         | Updated: Just now    | Users: 142       |")
            mockup.append("+------------------------------------------------------------------+")
        
        return "\n".join(mockup)
    
    def format_analysis_output(self, results: Dict) -> str:
        """Format analysis results with ASCII box-drawing characters"""
        lines = []
        
        # Header
        feature = results.get('feature_request', 'Unknown Feature')
        header_width = max(70, len(feature) + 10)
        
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        # Center "Feature Request"
        title = "Feature Request"
        title_padding = (header_width - len(title) - 2) // 2
        lines.append("|" + " " * title_padding + title + " " * (header_width - len(title) - title_padding - 2) + "|")
        
        # Center the feature name with quotes
        feature_text = f'"{feature}"'
        feature_padding = (header_width - len(feature_text) - 2) // 2
        lines.append("|" + " " * feature_padding + feature_text + " " * (header_width - len(feature_text) - feature_padding - 2) + "|")
        
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        # Summary section
        agents_count = len(results.get('agents_involved', []))
        total_effort = results.get('total_effort_hours', 0)
        
        lines.append("|" + f" Agents Involved: {agents_count}".ljust(header_width - 2) + "|")
        lines.append("|" + f" Total Effort: {total_effort} hours".ljust(header_width - 2) + "|")
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        # Agent orchestration tree
        lines.append("|" + " Agent Orchestration Flow".ljust(header_width - 2) + "|")
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        if results.get('call_tree'):
            for call in results['call_tree']:
                indent_str = "  " * call['level']
                tree_line = f" {indent_str}+-- {call['agent']}"
                lines.append("|" + tree_line.ljust(header_width - 2) + "|")
        
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        # Individual agent analyses
        for agent_name in results.get('agents_involved', []):
            agent_key = agent_name.lower().replace("-", "_")
            if agent_key not in results.get("analyses", {}):
                continue
            
            analysis = results["analyses"][agent_key]
            agent = self.agents.get(agent_name)
            
            # Agent header
            role = agent.role if agent else "Unknown Role"
            component = agent.component if agent else "Unknown Component"
            lines.append("|" + f" [AI] {agent_name} - {role}".ljust(header_width - 2) + "|")
            lines.append("|" + f" Component: {component}".ljust(header_width - 2) + "|")
            
            # Impact and effort
            impact = analysis.get('impact', 'N/A')
            effort = analysis.get('effort_hours', 0)
            lines.append("|" + f" Impact: {impact}"[:header_width - 3].ljust(header_width - 2) + "|")
            lines.append("|" + f" Effort: {effort} hours".ljust(header_width - 2) + "|")
            
            # Changes needed
            if analysis.get('changes'):
                lines.append("|" + " Changes:".ljust(header_width - 2) + "|")
                for change in analysis.get('changes', [])[:3]:  # Limit to 3 changes for display
                    change_line = f"   - {change}"[:header_width - 3]
                    lines.append("|" + change_line.ljust(header_width - 2) + "|")
            
            # Downstream dependencies
            if agent and agent.downstream_agents:
                deps_needed = []
                for downstream in agent.downstream_agents:
                    agent_key_dep = f"needs_{downstream.lower().replace('-', '_')}"
                    if analysis.get(agent_key_dep, False):
                        deps_needed.append(downstream)
                
                if deps_needed:
                    deps_line = f" Needs: {', '.join(deps_needed)}"[:header_width - 3]
                    lines.append("|" + deps_line.ljust(header_width - 2) + "|")
            
            lines.append("+" + "-" * (header_width - 2) + "+")
        
        # Footer
        lines.append("|" + " Analysis generated by AI Agent Orchestrator".ljust(header_width - 2) + "|")
        lines.append("+" + "-" * (header_width - 2) + "+")
        
        return "\n".join(lines)

    def generate_report(self, results: Dict, output_file: str):
        """Generate markdown report from analysis results"""
        with open(output_file, 'w') as f:
            f.write(f"# AI-Driven Feature Analysis Report\n\n")
            f.write(f"**Feature Request**: {results['feature_request']}\n\n")
            f.write(f"**Agents Involved**: {', '.join(results['agents_involved'])}\n\n")
            f.write(f"**Total Estimated Effort**: {results['total_effort_hours']} hours\n\n")
            
            # Show agent call tree
            if results.get('call_tree'):
                f.write("## Agent Orchestration Flow\n\n")
                f.write("```\n")
                for call in results['call_tree']:
                    indent = "  " * call['level']
                    f.write(f"{indent}└─ {call['agent']}\n")
                f.write("```\n\n")
            
            f.write("---\n\n")
            
            # Write analysis for each agent
            for agent_name in results['agents_involved']:
                agent_key = agent_name.lower().replace("-", "_")
                if agent_key not in results["analyses"]:
                    continue
                
                analysis = results["analyses"][agent_key]
                agent = self.agents.get(agent_name)
                
                if agent:
                    f.write(f"## {agent_name} - {agent.component}\n\n")
                    f.write(f"**Role**: {agent.role}\n\n")
                    f.write(f"**APIs Provided**: {', '.join(agent.apis) if agent.apis else 'None'}\n\n")
                else:
                    f.write(f"## {agent_name}\n\n")
                
                f.write(f"**Impact**: {analysis.get('impact', 'N/A')}\n\n")
                
                if analysis.get('components'):
                    f.write("**Components Affected**:\n")
                    for comp in analysis.get('components', []):
                        f.write(f"- {comp}\n")
                    f.write("\n")
                
                if analysis.get('changes'):
                    f.write("**Required Changes**:\n")
                    for change in analysis.get('changes', []):
                        f.write(f"- {change}\n")
                    f.write("\n")
                
                f.write(f"**Estimated Effort**: {analysis.get('effort_hours', 0)} hours\n\n")
                
                if analysis.get('risks'):
                    f.write("**Risks**:\n")
                    for risk in analysis.get('risks', []):
                        f.write(f"- {risk}\n")
                    f.write("\n")
                
                # Show downstream dependencies
                if agent and agent.downstream_agents:
                    f.write("**Downstream Dependencies**:\n")
                    for downstream in agent.downstream_agents:
                        agent_key = f"needs_{downstream.lower().replace('-', '_')}"
                        needed = analysis.get(agent_key, False)
                        status = "[OK] Required" if needed else "[SKIP] Not needed"
                        f.write(f"- {downstream}: {status}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"This hierarchical analysis was generated dynamically using AI.\n\n")
            f.write(f"- **Total agents involved**: {len(results['agents_involved'])}\n")
            f.write(f"- **Total effort**: {results['total_effort_hours']} hours\n")
            f.write(f"- **Analysis approach**: Each agent only sees downstream agent APIs\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: ai-agent-orchestrator.py '<feature_request>' [output_file] [ollama_host] [model]")
        sys.exit(1)
    
    feature_request = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "analysis-report.md"
    ollama_host = sys.argv[3] if len(sys.argv) > 3 else "http://10.0.2.2:11434"
    model = sys.argv[4] if len(sys.argv) > 4 else "llama3:8b"
    
    # Create orchestrator and run analysis
    orchestrator = AgentOrchestrator(ollama_host, model)
    results = orchestrator.orchestrate(feature_request)
    
    # Generate report
    orchestrator.generate_report(results, output_file)
    
    # Display formatted analysis
    print("\n" + orchestrator.format_analysis_output(results))
    
    # Output JSON for Jenkins to parse
    print("\n" + "="*50)
    print("JSON Results:")
    print(json.dumps(results, indent=2))
    
    print(f"\n[OK] Analysis complete!")
    print(f"  [DOC] Report: {output_file}")

if __name__ == "__main__":
    main()
