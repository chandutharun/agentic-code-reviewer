"""
Sandboxed Code Execution
Execute agent-generated code in isolated Docker environments
"""
import docker
import tempfile
import os
import subprocess
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class SandboxResult:
    """Result from sandboxed execution"""
    success: bool
    output: str
    error: str
    sandboxed: bool
    execution_time: float
    safety_violations: list

class SandboxedExecutor:
    """
    Execute code in isolated Docker container
    Prevents system exploits from agent-generated code
    """
    
    def __init__(self, memory_limit: str = "256m", cpu_limit: float = 0.5):
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.client = None
        self.docker_enabled = self._check_docker()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            return True
        except:
            return False
    
    def execute_in_sandbox(self, code: str, timeout: int = 10) -> SandboxResult:
        """
        Execute code in isolated Docker container
        
        Features:
        - Isolated environment (no network access)
        - Memory limits (prevent DoS)
        - CPU limits (prevent resource exhaustion)
        - No filesystem access (except temp)
        """
        import time
        start_time = time.time()
        
        if not self.docker_enabled:
            # Fallback: validate but don't execute
            return self._validate_only(code, start_time)
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run in sandboxed container
            container = self.client.containers.run(
                "python:3.11-slim",
                command=f"python /app/script.py",
                volumes={tempfile.gettempdir(): {'bind': '/app', 'mode': 'rw'}},
                network_disabled=True,  # No network access
                memory=self.memory_limit,  # Limit memory
                nano_cpus=int(self.cpu_limit * 1_000_000_000),  # Limit CPU
                detach=False,
                remove=True,
                timeout=timeout,
                security_opt=["no-new-privileges:true"]  # Additional security
            )
            
            execution_time = time.time() - start_time
            os.unlink(temp_file)
            
            return SandboxResult(
                success=True,
                output=container.decode('utf-8'),
                error="",
                sandboxed=True,
                execution_time=execution_time,
                safety_violations=[]
            )
        
        except docker.errors.ContainerError as e:
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                sandboxed=True,
                execution_time=time.time() - start_time,
                safety_violations=['container_error']
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                sandboxed=False,
                execution_time=time.time() - start_time,
                safety_violations=['execution_error']
            )
    
    def _validate_only(self, code: str, start_time: float) -> SandboxResult:
        """Validate code without executing (fallback when Docker unavailable)"""
        dangerous_patterns = [
            ('os.system', 'System command execution'),
            ('subprocess', 'Subprocess execution'),
            ('eval(', 'Eval function (code injection)'),
            ('exec(', 'Exec function (code injection)'),
            ('__import__', 'Dynamic import'),
            ('import os', 'OS module import'),
            ('import subprocess', 'Subprocess module import'),
            ('socket', 'Network access'),
            ('requests', 'HTTP requests'),
        ]
        
        violations = []
        for pattern, description in dangerous_patterns:
            if pattern in code:
                violations.append(description)
        
        return SandboxResult(
            success=len(violations) == 0,
            output="" if violations else "Code validated (Docker not available)",
            error="Dangerous patterns detected" if violations else "",
            sandboxed=False,
            execution_time=time.time() - start_time,
            safety_violations=violations
        )
    
    def verify_safe_code(self, code: str) -> Dict:
        """
        Pre-flight check: Is this code safe to execute?
        Safety checks before execution
        """
        dangerous_patterns = [
            ('os.system', 'System command'),
            ('subprocess', 'Subprocess'),
            ('eval(', 'Eval'),
            ('exec(', 'Exec'),
            ('__import__', 'Dynamic import'),
            ('import os', 'OS module'),
            ('import subprocess', 'Subprocess module'),
            ('socket', 'Network'),
            ('open(', 'File access'),
            ('os.remove', 'File deletion'),
            ('os.mkdir', 'Directory creation'),
        ]
        
        findings = []
        for pattern, description in dangerous_patterns:
            if pattern in code:
                findings.append({
                    'pattern': pattern,
                    'description': description,
                    'severity': 'High' if pattern in ['eval(', 'exec(', 'os.system'] else 'Medium'
                })
        
        return {
            'safe': len(findings) == 0,
            'dangerous_patterns': findings,
            'recommendation': 'Block execution' if findings else 'Safe to execute',
            'risk_level': 'High' if any(f['severity'] == 'High' for f in findings) else 'Medium' if findings else 'Low'
        }
    
    def run_agent_code_safely(self, agent_generated_code: str) -> Dict:
        """
        Full safety pipeline for agent-generated code
        Complete safety workflow
        """
        # Step 1: Pre-flight safety check
        safety_check = self.verify_safe_code(agent_generated_code)
        
        if not safety_check['safe']:
            return {
                'success': False,
                'blocked': True,
                'reason': 'Dangerous patterns detected',
                'violations': safety_check['dangerous_patterns'],
                'recommendation': safety_check['recommendation']
            }
        
        # Step 2: Execute in sandbox
        result = self.execute_in_sandbox(agent_generated_code)
        
        return {
            'success': result.success,
            'blocked': False,
            'output': result.output,
            'error': result.error,
            'sandboxed': result.sandboxed,
            'execution_time': result.execution_time,
            'safety_violations': result.safety_violations
        }
