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
                "stream": False
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

Analyze the feature request and provide:
1. Impact on your components
2. Required changes
3. Dependencies on other agents (Agent B: Backend, Agent C: In-Car Systems)
4. Estimated effort
5. Risks and challenges

Respond in JSON format with these keys:
- impact: string describing impact
- components: list of affected components
- changes: list of required changes
- needs_agent_b: boolean (true if backend changes needed)
- needs_agent_c: boolean (true if in-car system changes needed)
- effort_hours: number
- risks: list of risks
"""
        
        context_str = ""
        if context:
            context_str = f"\n\nContext from other agents:\n{json.dumps(context, indent=2)}"
        
        prompt = f"""Feature Request: {feature_request}{context_str}

Analyze this request from your perspective and determine what's needed.
Provide your analysis in valid JSON format."""
        
        response = self.ollama.generate(prompt, system_prompt)
        
        # Try to parse JSON from response
        try:
            # Find JSON in response (might have extra text)
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                analysis = json.loads(json_str)
                self.analysis_result = analysis
                return analysis
            else:
                # Fallback if no JSON found
                return self._create_default_analysis(feature_request)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON from {self.name}", file=sys.stderr)
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
    
    # Create coordinator and run analysis
    coordinator = AgentCoordinator(ollama_host, model)
    results = coordinator.coordinate(feature_request)
    
    # Generate report
    coordinator.generate_report(results, output_file)
    
    # Output JSON for Jenkins to parse
    print("\n" + "="*50)
    print("JSON Results:")
    print(json.dumps(results, indent=2))
    
    print(f"\n✅ Analysis complete. Report saved to: {output_file}")

if __name__ == "__main__":
    main()
