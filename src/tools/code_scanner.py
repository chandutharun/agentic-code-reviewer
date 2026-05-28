"""
Code Scanner Tool - Reads and analyzes code files
Supports recursive directory scanning with relative paths
"""
import ast
import os
from typing import List, Dict

class CodeScanner:
    def __init__(self):
        self.supported_extensions = ('.py', '.js', '.java', '.go', '.cpp', '.c', '.ts', '.jsx', '.tsx', '.html', '.css', '.sql', '.rb', '.php', '.cs', '.swift', '.kt')
    
    def read_file(self, filepath: str) -> str:
        """Read code file content"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return ""
    
    def read_directory(self, dirpath: str) -> Dict[str, str]:
        """Read all code files in directory recursively"""
        code_files = {}
        
        if not os.path.exists(dirpath):
            print(f"❌ Directory not found: {dirpath}")
            return code_files
        
        for root, dirs, files in os.walk(dirpath):
            # Skip vendor/cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules', 'env', '.venv', 'dist', 'build', '.idea', '.vscode']]
            
            for file in files:
                # Check extension
                if file.endswith(self.supported_extensions):
                    filepath = os.path.join(root, file)
                    
                    # Skip very large files (>1MB)
                    try:
                        if os.path.getsize(filepath) > 1_000_000:
                            print(f"⚠️ Skipping large file: {filepath}")
                            continue
                    except:
                        continue
                    
                    try:
                        code = self.read_file(filepath)
                        if code.strip():  # Only add non-empty files
                            # Use relative path for cleaner display
                            relative_path = os.path.relpath(filepath, dirpath)
                            code_files[relative_path] = code
                    except Exception as e:
                        print(f"⚠️ Warning: Could not read {filepath}: {e}")
        
        print(f"✅ Found {len(code_files)} code file(s) in {dirpath}")
        return code_files
    
    def get_ast(self, code: str) -> ast.AST:
        """Parse code into AST for analysis (Python only)"""
        try:
            return ast.parse(code)
        except:
            return None
    
    def find_functions(self, code: str) -> List[str]:
        """Find all function definitions (Python only)"""
        try:
            tree = self.get_ast(code)
            if not tree:
                return []
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
            return functions
        except:
            return []
    
    def find_imports(self, code: str) -> List[str]:
        """Find all import statements (Python only)"""
        try:
            tree = self.get_ast(code)
            if not tree:
                return []
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module)
            return imports
        except:
            return []
    
    def get_file_info(self, filepath: str) -> Dict:
        """Get basic file information"""
        try:
            stat = os.stat(filepath)
            code = self.read_file(filepath)
            return {
                'name': os.path.basename(filepath),
                'size': stat.st_size,
                'lines': len(code.split('\n')),
                'modified': stat.st_mtime
            }
        except Exception as e:
            return {'error': str(e)}
