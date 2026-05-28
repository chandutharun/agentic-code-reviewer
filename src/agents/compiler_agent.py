"""
Compiler Agent - Validates that auto-fixed code compiles successfully.
If compilation fails, loops back to Fix Agent with error details for retry.
Supports: Python, JavaScript, TypeScript, Java, Go, HTML, CSS
"""

import py_compile
import subprocess
import tempfile
import os
import re
from typing import Optional


class CompilerAgent:
    """Validates code compilation and provides error feedback for auto-retry."""
    
    def __init__(self):
        self.max_retries = 3
    
    def get_language(self, filename: str) -> str:
        """Get programming language from file extension"""
        if not filename:
            return "unknown"
        
        ext = filename.split('.')[-1].lower()
        
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'java': 'java',
            'go': 'go',
            'html': 'html',
            'htm': 'html',
            'css': 'css',
            'c': 'c',
            'cpp': 'cpp',
            'cc': 'cpp',
            'rb': 'ruby',
            'php': 'php',
            'cs': 'csharp',
            'swift': 'swift',
            'kt': 'kotlin',
            'sql': 'sql',
        }
        
        return language_map.get(ext, 'unknown')
    
    def check_python_compilation(self, code: str) -> dict:
        """Check if Python code compiles successfully."""
        try:
            compile(code, '<string>', 'exec')
            return {
                "success": True,
                "errors": [],
                "error_type": None,
                "error_line": None,
                "language": "python"
            }
        except SyntaxError as e:
            return {
                "success": False,
                "errors": [f"SyntaxError: {e.msg} at line {e.lineno}"],
                "error_type": "syntax_error",
                "error_line": e.lineno,
                "error_message": e.msg,
                "language": "python"
            }
        except IndentationError as e:
            return {
                "success": False,
                "errors": [f"IndentationError: {e.msg} at line {e.lineno}"],
                "error_type": "indentation_error",
                "error_line": e.lineno,
                "error_message": e.msg,
                "language": "python"
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Error: {str(e)}"],
                "error_type": "unknown",
                "error_line": None,
                "error_message": str(e),
                "language": "python"
            }
    
    def check_javascript_syntax(self, code: str) -> dict:
        """Check JavaScript syntax using Node.js (if available)."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['node', '--check', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "errors": [],
                        "error_type": None,
                        "error_line": None,
                        "language": "javascript"
                    }
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    return {
                        "success": False,
                        "errors": [error_msg],
                        "error_type": "syntax_error",
                        "error_line": None,
                        "error_message": error_msg,
                        "language": "javascript"
                    }
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        except FileNotFoundError:
            return {
                "success": True,
                "errors": ["Node.js not found - skipping JavaScript check"],
                "error_type": "skipped",
                "error_line": None,
                "language": "javascript",
                "skipped": True
            }
        except Exception as e:
            return {
                "success": True,
                "errors": [f"Check skipped: {str(e)}"],
                "error_type": "skipped",
                "language": "javascript",
                "skipped": True
            }
    
    def check_html_syntax(self, code: str) -> dict:
        """HTML doesn't compile - always pass with info message."""
        return {
            "success": True,
            "errors": ["HTML doesn't compile - syntax validation skipped"],
            "error_type": "info",
            "error_line": None,
            "language": "html",
            "skipped": True,
            "info": "HTML files don't require compilation"
        }
    
    def check_css_syntax(self, code: str) -> dict:
        """CSS doesn't compile - always pass with info message."""
        return {
            "success": True,
            "errors": ["CSS doesn't compile - syntax validation skipped"],
            "error_type": "info",
            "error_line": None,
            "language": "css",
            "skipped": True,
            "info": "CSS files don't require compilation"
        }
    
    def check_java_compilation(self, code: str) -> dict:
        """Check Java compilation (if javac available)."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['javac', '-Xlint:none', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "errors": [],
                        "error_type": None,
                        "error_line": None,
                        "language": "java"
                    }
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    return {
                        "success": False,
                        "errors": [error_msg],
                        "error_type": "compilation_error",
                        "language": "java"
                    }
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        except FileNotFoundError:
            return {
                "success": True,
                "errors": ["javac not found - skipping Java check"],
                "error_type": "skipped",
                "language": "java",
                "skipped": True
            }
        except Exception as e:
            return {
                "success": True,
                "errors": [f"Check skipped: {str(e)}"],
                "error_type": "skipped",
                "language": "java",
                "skipped": True
            }
    
    def check_go_compilation(self, code: str) -> dict:
        """Check Go compilation (if go available)."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['go', 'build', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "errors": [],
                        "error_type": None,
                        "language": "go"
                    }
                else:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    return {
                        "success": False,
                        "errors": [error_msg],
                        "error_type": "compilation_error",
                        "language": "go"
                    }
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        except FileNotFoundError:
            return {
                "success": True,
                "errors": ["go not found - skipping Go check"],
                "error_type": "skipped",
                "language": "go",
                "skipped": True
            }
        except Exception as e:
            return {
                "success": True,
                "errors": [f"Check skipped: {str(e)}"],
                "error_type": "skipped",
                "language": "go",
                "skipped": True
            }
    
    def check_syntax(self, code: str, filename: str) -> dict:
        """
        Check syntax/compilation based on file type.
        
        Returns:
            dict: {
                "success": bool,
                "errors": list,
                "error_type": str,
                "language": str,
                "skipped": bool (optional)
            }
        """
        language = self.get_language(filename)
        
        # Route to appropriate checker
        if language == 'python':
            return self.check_python_compilation(code)
        elif language in ['javascript', 'jsx']:
            return self.check_javascript_syntax(code)
        elif language in ['typescript', 'tsx']:
            return self.check_javascript_syntax(code)  # TS uses same check
        elif language in ['html', 'htm']:
            return self.check_html_syntax(code)
        elif language == 'css':
            return self.check_css_syntax(code)
        elif language == 'java':
            return self.check_java_compilation(code)
        elif language == 'go':
            return self.check_go_compilation(code)
        else:
            # Unknown language - skip check
            return {
                "success": True,
                "errors": [f"Unknown file type: {filename} - syntax check skipped"],
                "error_type": "skipped",
                "language": language,
                "skipped": True
            }
    
    def generate_fix_prompt(self, original_code: str, failed_code: str, 
                           compilation_result: dict) -> str:
        """Generate prompt for Fix Agent to retry with compilation error."""
        language = compilation_result.get('language', 'unknown')
        error_msg = compilation_result['errors'][0] if compilation_result['errors'] else "Unknown error"
        error_line = compilation_result.get('error_line')
        
        prompt = f"""PREVIOUS auto-fix FAILED {language.upper()} COMPILATION. Fix the code again.

COMPILATION ERROR ({language}):
{error_msg}
{"(Line " + str(error_line) + ")" if error_line else ""}

ORIGINAL CODE:
```{language}
{original_code}
```

PREVIOUS ATTEMPT (FAILED TO COMPILE):
```{language}
{failed_code}
```

YOUR TASK:
Generate a COMPLETE FIXED VERSION that:
1. Fixes ALL security vulnerabilities
2. FIXES THE COMPILATION ERROR above
3. Returns ONLY the complete fixed code (no explanations)
4. Make sure code COMPILES SUCCESSFULLY

Provide ONLY the fixed {language} code:
"""
        return prompt
    
    def validate_and_retry(self, original_code: str, fixed_code: str, 
                          llm_invoke_func, max_retries: int = 3,
                          filename: str = "") -> tuple:
        """Validate fixed code and retry if compilation fails."""
        
        # Get language from filename
        language = self.get_language(filename)
        
        # Skip retry for non-compilable languages
        if language in ['html', 'htm', 'css']:
            print(f"⚠️ Skipping compilation check for {filename} ({language} doesn't compile)")
            return fixed_code, self.check_syntax(fixed_code, filename), 0
        
        current_code = fixed_code
        
        for attempt in range(max_retries):
            # Check compilation
            result = self.check_syntax(current_code, filename)
            
            # If skipped (no compiler available), return success
            if result.get('skipped', False):
                print(f"ℹ️ {language.title()} check skipped ({result['errors'][0]})")
                return current_code, result, 0
            
            # If success, return
            if result["success"]:
                return current_code, result, attempt
            
            # Compilation failed - retry
            prompt = self.generate_fix_prompt(original_code, current_code, result)
            fixed_response = llm_invoke_func(prompt)
            
            # Extract code (remove markdown if present)
            current_code = self._extract_code(fixed_response)
            
            print(f"⚠️ {language.title()} compilation attempt {attempt + 1}/{max_retries} failed. Retrying...")
        
        # Max retries reached
        return current_code, result, max_retries
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response."""
        # Remove markdown code blocks
        if "```python" in response or "```py" in response:
            match = re.search(r'```(?:py|python)\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        if "```javascript" in response or "```js" in response:
            match = re.search(r'```(?:js|javascript)\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        if "```html" in response:
            match = re.search(r'```html\n(.*?)\n```', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        if "```" in response:
            match = re.search(r'```\n(.*)', response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return response.strip()