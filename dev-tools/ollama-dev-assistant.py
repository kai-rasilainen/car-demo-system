#!/usr/bin/env python3
"""
Ollama Development Assistant for Car Demo Project

This tool uses Ollama to help with:
1. Code analysis and review
2. Documentation generation
3. Test generation
4. Bug detection and suggestions

Usage:
    python ollama-dev-assistant.py analyze <file>
    python ollama-dev-assistant.py document <file>
    python ollama-dev-assistant.py generate-tests <file>
    python ollama-dev-assistant.py review <file>
"""

import argparse
import json
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error


class OllamaDevAssistant:
    def __init__(self, model="llama3:8b"):
        self.model = model
        # Get Ollama host from environment or use default
        self.ollama_host = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
        if not self.ollama_host.startswith('http'):
            self.ollama_host = f'http://{self.ollama_host}'
        
    def _call_ollama(self, prompt, system_prompt=None):
        """Call Ollama API with the given prompt"""
        # Build the API request
        api_url = f"{self.ollama_host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            print(f"🤖 Sending request to Ollama at {self.ollama_host}...", file=sys.stderr)
            print(f"📝 Using model: {self.model}", file=sys.stderr)
            print(f"⏳ Please wait (this may take 1-2 minutes)...\n", file=sys.stderr)
            
            # Make the HTTP request
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', 'No response from Ollama')
                
        except urllib.error.URLError as e:
            return f"Error: Cannot connect to Ollama at {self.ollama_host}. Make sure Ollama is running and OLLAMA_HOST is set correctly. ({str(e)})"
        except TimeoutError:
            return "Error: Ollama request timed out (300s limit)"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def analyze_code(self, file_path):
        """Analyze code for potential issues and improvements"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return f"Error: File {file_path} not found"
        
        code = file_path.read_text()
        language = file_path.suffix[1:]  # Remove the dot
        
        system_prompt = """You are an expert code reviewer. Analyze the code for:
- Potential bugs or issues
- Performance improvements
- Security vulnerabilities
- Code quality and best practices
- Maintainability concerns

Provide specific, actionable feedback."""

        prompt = f"""Analyze this {language} code:

File: {file_path.name}

```{language}
{code}
```

Provide a detailed analysis with specific line references where possible."""

        return self._call_ollama(prompt, system_prompt)
    
    def generate_documentation(self, file_path):
        """Generate documentation for the code"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return f"Error: File {file_path} not found"
        
        code = file_path.read_text()
        language = file_path.suffix[1:]
        
        system_prompt = """You are a technical documentation expert. Generate clear, 
comprehensive documentation including:
- Overview of what the code does
- Function/method descriptions
- Parameters and return values
- Usage examples
- Edge cases and error handling

Use proper markdown formatting."""

        prompt = f"""Generate detailed documentation for this {language} code:

File: {file_path.name}

```{language}
{code}
```

Create documentation that would help other developers understand and use this code."""

        return self._call_ollama(prompt, system_prompt)
    
    def generate_tests(self, file_path):
        """Generate test cases for the code"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return f"Error: File {file_path} not found"
        
        code = file_path.read_text()
        language = file_path.suffix[1:]
        
        # Determine test framework based on language
        test_framework = {
            'py': 'pytest',
            'js': 'Jest',
            'ts': 'Jest'
        }.get(language, 'standard testing framework')
        
        system_prompt = f"""You are an expert test engineer. Generate comprehensive test cases using {test_framework}.
Include:
- Unit tests for all functions/methods
- Edge case testing
- Error handling tests
- Integration tests where appropriate
- Mock/stub examples where needed

Write actual, runnable test code."""

        prompt = f"""Generate comprehensive test cases for this {language} code:

File: {file_path.name}

```{language}
{code}
```

Create test file with complete test coverage."""

        return self._call_ollama(prompt, system_prompt)
    
    def review_changes(self, file_path):
        """Review code changes and suggest improvements"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return f"Error: File {file_path} not found"
        
        code = file_path.read_text()
        language = file_path.suffix[1:]
        
        system_prompt = """You are a senior developer doing code review. Focus on:
- Architecture and design patterns
- Code organization and structure
- Naming conventions
- Error handling
- Potential refactoring opportunities
- Testing considerations

Be constructive and specific."""

        prompt = f"""Review this {language} code and provide feedback:

File: {file_path.name}

```{language}
{code}
```

Provide a code review with specific suggestions for improvement."""

        return self._call_ollama(prompt, system_prompt)
    
    def explain_code(self, file_path):
        """Explain what the code does in simple terms"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return f"Error: File {file_path} not found"
        
        code = file_path.read_text()
        language = file_path.suffix[1:]
        
        system_prompt = """You are a patient teacher explaining code to someone learning programming.
Explain clearly and simply:
- What the code does (high level)
- How it works (step by step)
- Why certain approaches are used
- What could be confusing

Use analogies where helpful."""

        prompt = f"""Explain this {language} code in clear, simple terms:

File: {file_path.name}

```{language}
{code}
```

Help someone understand what this code does and how it works."""

        return self._call_ollama(prompt, system_prompt)


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Development Assistant for Car Demo Project"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "document", "generate-tests", "review", "explain"],
        help="Command to execute"
    )
    parser.add_argument(
        "file",
        help="File to process"
    )
    parser.add_argument(
        "--model",
        default="llama3:8b",
        help="Ollama model to use (default: llama3:8b)"
    )
    parser.add_argument(
        "--output",
        help="Output file (default: print to stdout)"
    )
    
    args = parser.parse_args()
    
    assistant = OllamaDevAssistant(model=args.model)
    
    # Execute the requested command
    if args.command == "analyze":
        result = assistant.analyze_code(args.file)
    elif args.command == "document":
        result = assistant.generate_documentation(args.file)
    elif args.command == "generate-tests":
        result = assistant.generate_tests(args.file)
    elif args.command == "review":
        result = assistant.review_changes(args.file)
    elif args.command == "explain":
        result = assistant.explain_code(args.file)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
    
    # Output result
    if args.output:
        Path(args.output).write_text(result)
        print(f"Output written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
