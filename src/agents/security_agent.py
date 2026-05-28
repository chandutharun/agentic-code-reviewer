"""
Security Agent - Finds security vulnerabilities in code
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
import re
import json


class SecurityAgent:
    def __init__(self, model: str = "llama3.2"):
        self.llm = ChatOllama(model=model, base_url="http://localhost:11434")
        self.system_prompt = """You are a security expert code reviewer. Your job is to:
1. Find security vulnerabilities in the code
2. Identify: SQL injection, XSS, hardcoded secrets, insecure crypto, path traversal, eval() usage
3. Provide severity (Critical/High/Medium/Low)
4. Suggest fixes with code examples

IMPORTANT: Return your response as a JSON array of findings.
Each finding must have these fields:
- severity: "Critical" | "High" | "Medium" | "Low"
- location: "Line X" or "Line X-Y"
- issue: Brief description of vulnerability
- risk: Why this is dangerous (1-2 sentences)
- fix: Suggested code fix (with code example)

Example response format:
[
    {{
        "severity": "High",
        "location": "Line 5",
        "issue": "SQL Injection - User input directly concatenated into SQL query",
        "risk": "Attacker can inject malicious SQL to access/modify/delete database data",
        "fix": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
    }},
    {{
        "severity": "Critical",
        "location": "Line 10",
        "issue": "Hardcoded API Key - Secret credential in source code",
        "risk": "If code is leaked, attacker gains access to API and can abuse service",
        "fix": "Use environment variable: API_KEY = os.getenv('API_KEY')"
    }}
]

If no vulnerabilities found, return empty array: []

Be thorough and specific. Only include actual vulnerabilities, not warnings."""
    
    def review(self, code: str, filename: str) -> List[Dict]:
        """
        Review code for security issues
        Returns: List of findings with severity, description, fix
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "Review this {language} code for security vulnerabilities:\n\nFile: {filename}\n\nCode:\n```\n{code}\n```")
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
            # Try direct JSON parsing
            data = json.loads(response)
            if isinstance(data, list):
                for finding in data:
                    # Ensure all required fields exist
                    parsed_finding = {
                        'severity': finding.get('severity', 'Medium'),
                        'location': finding.get('location', 'N/A'),
                        'issue': finding.get('issue', 'No description'),
                        'risk': finding.get('risk', 'Potential security risk'),
                        'fix': finding.get('fix', 'Manual review required')
                    }
                    findings.append(parsed_finding)
            return findings
        except json.JSONDecodeError:
            pass
        
        # Fallback: Try old [FINDING] format
        finding_blocks = response.split('[FINDING]')
        
        for block in finding_blocks[1:]:  # Skip first empty split
            finding = {}
            
            # Extract severity
            severity_match = re.search(r'Severity:\s*(\w+)', block)
            finding['severity'] = severity_match.group(1) if severity_match else 'Medium'
            
            # Extract location
            location_match = re.search(r'Location:\s*(.+?)\n', block)
            finding['location'] = location_match.group(1).strip() if location_match else 'Unknown'
            
            # Extract issue
            issue_match = re.search(r'Issue:\s*(.+?)\n', block)
            finding['issue'] = issue_match.group(1).strip() if issue_match else block[:200]
            
            # Extract risk
            risk_match = re.search(r'Risk:\s*(.+?)\n', block)
            finding['risk'] = risk_match.group(1).strip() if risk_match else 'Potential security risk'
            
            # Extract fix
            fix_match = re.search(r'Fix:\s*(.+?)(?:\[END FINDING\]|$)', block, re.DOTALL)
            finding['fix'] = fix_match.group(1).strip() if fix_match else 'Review and fix manually'
            
            findings.append(finding)
        
        # If still no findings, return empty list (no vulnerabilities)
        if not findings:
            return []
        
        return findings