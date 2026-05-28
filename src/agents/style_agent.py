"""
Style Agent - Checks code style and best practices
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
import json
import re


class StyleAgent:
    def __init__(self, model: str = "llama3.2"):
        self.llm = ChatOllama(model=model, base_url="http://localhost:11434")
        self.system_prompt = """You are a code style expert. Your job is to:
1. Check PEP8 compliance (for Python)
2. Check naming conventions
3. Check function/documentation quality
4. Check code complexity
5. Suggest improvements

IMPORTANT: Return your response as a JSON array of findings.
Each finding must have these fields:
- severity: "Medium" | "Low" | "Info"
- location: "Line X" or "Line X-Y"
- issue: Style problem description
- suggestion: How to fix it

Example response format:
[
    {{
        "severity": "Low",
        "location": "Line 10",
        "issue": "Missing docstring for function",
        "suggestion": "Add docstring: \\"\\"\\"Brief description.\\"\\"\\" "
    }},
    {{
        "severity": "Medium",
        "location": "Line 25",
        "issue": "Variable name 'x' is not descriptive",
        "suggestion": "Rename to 'max_iterations' or similar"
    }}
]

If NO style issues found, return empty array: []

Be thorough. Only include actual style issues, not warnings."""
    
    def review(self, code: str, filename: str) -> List[Dict]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "Review this {language} code for style issues:\n\nFile: {filename}\n\nCode:\n```\n{code}\n```")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "language": self._detect_language(filename),
            "filename": filename,
            "code": code
        })
        
        return self._parse_findings(response.content)
    
    def _detect_language(self, filename: str) -> str:
        if filename.endswith('.py'):
            return 'Python'
        elif filename.endswith('.js'):
            return 'JavaScript'
        elif filename.endswith('.java'):
            return 'Java'
        elif filename.endswith('.go'):
            return 'Go'
        return 'Unknown'
    
    def _parse_findings(self, response: str) -> List[Dict]:
        """Parse LLM response into structured findings"""
        findings = []
        
        # Clean up response - remove markdown code blocks
        response = response.strip()
        if response.startswith('```json'):
            response = response.split('```json')[1]
        elif response.startswith('```'):
            response = response.split('```')[1]
        
        if response.endswith('```'):
            response = response.rsplit('```', 1)[0]
        
        response = response.strip()
        
        # Try to parse as JSON
        try:
            data = json.loads(response)
            if isinstance(data, list):
                for finding in data:
                    # Skip findings that say "no issues"
                    issue_text = finding.get('issue', '').lower()
                    if 'no issue' in issue_text or 'no style issue' in issue_text or 'great job' in issue_text:
                        continue
                    
                    parsed_finding = {
                        'severity': finding.get('severity', 'Low'),
                        'location': finding.get('location', 'N/A'),
                        'issue': finding.get('issue', 'No description'),
                        'suggestion': finding.get('suggestion', 'Manual review required')
                    }
                    findings.append(parsed_finding)
            return findings
        except json.JSONDecodeError:
            pass
        
        # Fallback: Try old [FINDING] format
        finding_blocks = response.split('[FINDING]')
        
        for block in finding_blocks[1:]:
            # Check if this block says "no issues"
            if 'no style issues found' in block.lower() or 'great job' in block.lower():
                continue
            
            finding = {}
            
            # Extract severity
            severity_match = re.search(r'Severity:\s*(\w+)', block)
            finding['severity'] = severity_match.group(1) if severity_match else 'Low'
            
            # Extract location
            location_match = re.search(r'Location:\s*(.+?)\n', block)
            finding['location'] = location_match.group(1).strip() if location_match else 'N/A'
            
            # Extract issue
            issue_match = re.search(r'Issue:\s*(.+?)\n', block)
            finding['issue'] = issue_match.group(1).strip() if issue_match else block[:200]
            
            # Extract suggestion
            suggestion_match = re.search(r'Suggestion:\s*(.+?)(?:\[END FINDING\]|$)', block, re.DOTALL)
            finding['suggestion'] = suggestion_match.group(1).strip() if suggestion_match else 'Manual review required'
            
            findings.append(finding)
        
        # Return empty list if no findings (no style issues)
        return findings