"""
Fix Agent - Generates fixed code for security and style issues.
UNIQUE FEATURE: Auto-generates complete fixed code (not just suggestions)
"""

from langchain_ollama import ChatOllama
from typing import List, Dict, Any
import re


class FixAgent:
    """Generates fixed code for all security and style findings."""
    
    def __init__(self, model: str = "llama3.2"):
        # self.llm = ChatOllama(model=model, temperature=0.3)
        self.llm = ChatOllama(model=model, temperature=0.3, base_url="http://localhost:11434")
    
    def generate_fix_prompt(self, code: str, findings: List[Dict], filename: str) -> str:
        """Generate prompt for fix agent."""
        
        finding_descriptions = []
        for i, finding in enumerate(findings, 1):
            finding_descriptions.append(f"{i}. {finding.get('issue', 'Unknown issue')}")
        
        findings_text = "\n".join(finding_descriptions) if finding_descriptions else "No issues"
        
        prompt = f"""CRITICAL INSTRUCTION: You must generate the COMPLETE, FULL CODE from start to finish.
DO NOT use comments like "# unchanged", "# rest of code", "# same as before", or any placeholders.
You must rewrite EVERY SINGLE LINE of the code completely.

Your task: Fix ALL security and style issues in this code.

FILE: {filename}

ISSUES TO FIX:
{findings_text}

ORIGINAL CODE (COMPLETE):
```python
{code}
```

YOUR TASK:
Generate the COMPLETE FIXED CODE that:
1. Fixes ALL issues listed above
2. Returns the FULL code from line 1 to the last line
3. NO placeholders, NO "# unchanged", NO "# rest of code"
4. EVERY function, EVERY import, EVERY line must be written completely
5. Code must be production-ready and compile successfully

IMPORTANT: Write the FULL code. Do not skip any lines.
Do NOT use comments like "# unchanged" or "# rest of code here".
Write EVERYTHING from scratch.

COMPLETE FIXED CODE (write EVERY line, NO placeholders):
```python
"""
        return prompt
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        # Remove markdown code blocks
        if "```python" in response:
            match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        if "```py" in response:
            match = re.search(r'```py\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        if "```" in response:
            match = re.search(r'```\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return response.strip()
    
    def clean_generated_code(self, code: str) -> str:
        """Remove any placeholder comments from generated code."""
        # Remove common placeholder comments
        placeholders = [
            '# unchanged',
            '# rest of code',
            '# same as before',
            '# ... rest of code',
            '# ...',
            '# rest of the code remains the same',
            '# code continues...',
            '# remaining code unchanged',
            '# other code unchanged',
            '# rest unchanged',
        ]
        
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just placeholders
            if any(ph in line.lower() for ph in placeholders):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def generate_fixes_for_all(self, code: str, findings: List[Dict], filename: str) -> Dict:
        """Generate fixes for all findings at once."""
        
        if not findings:
            return {
                'fixed_code': code,
                'fixes_applied': 0,
                'fix_details': []
            }
        
        # Generate prompt
        prompt = self.generate_fix_prompt(code, findings, filename)
        
        # Invoke LLM
        response = self.llm.invoke(prompt)
        fixed_code = response.content
        
        # Clean generated code (remove placeholders like "# unchanged")
        fixed_code = self.clean_generated_code(fixed_code)
        
        # Extract code from markdown if present
        fixed_code = self._extract_code(fixed_code)
        
        fixes_applied = len(findings)
        
        fix_details = []
        for finding in findings:
            fix_details.append({
                'issue': finding.get('issue', 'Unknown'),
                'severity': finding.get('severity', 'Info'),
                'fix_applied': True
            })
        
        return {
            'fixed_code': fixed_code,
            'fixes_applied': fixes_applied,
            'fix_details': fix_details
        }
    
    def compare_codes(self, original: str, fixed: str) -> Dict:
        """Compare original and fixed code."""
        original_lines = len(original.split('\n'))
        fixed_lines = len(fixed.split('\n'))
        
        # Simple diff (could be improved with difflib)
        modified_lines = abs(original_lines - fixed_lines)
        
        return {
            'original_lines': original_lines,
            'fixed_lines': fixed_lines,
            'modified_lines': modified_lines
        }
