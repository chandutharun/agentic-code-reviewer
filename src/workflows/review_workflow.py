"""
LangGraph Workflow for Multi-Agent Code Review
COMPLETE VERSION WITH AUTO-FIX GENERATION + COMPILER VALIDATION
Unique Features:
1. Auto-Fix Agent (generates corrected code automatically)
2. Compiler Agent (validates code compiles, loops back if fails)
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from src.agents.security_agent import SecurityAgent
from src.agents.style_agent import StyleAgent
from src.agents.fix_agent import FixAgent
from src.agents.compiler_agent import CompilerAgent  # NEW
from src.utils.evaluations import AgentEvaluations
from src.tools.sandbox import SandboxedExecutor
from src.utils.langsmith_tracing import LangSmithTracing
import time

class ReviewState(TypedDict):
    """State shared between agents"""
    code: str
    filename: str
    security_findings: List[Dict]
    style_findings: List[Dict]
    final_report: Dict
    completed: bool
    processing_time: float
    fixed_code: str
    fixes_applied: int
    fix_details: List[Dict]
    compilation_success: bool  # NEW
    compilation_errors: List[str]  # NEW
    retry_count: int  # NEW

class ReviewWorkflow:
    """
    Multi-Agent Code Review Workflow with Auto-Fix Generation + Compiler Validation
    UNIQUE FEATURES:
    1. Automatically generates fixed code for vulnerabilities
    2. Validates code compiles successfully
    3. Auto-retry if compilation fails
    """
    
    def __init__(self, model: str = "llama3.2"):  # ✅ Default: llama3.2
        self.security_agent = SecurityAgent(model=model)
        self.style_agent = StyleAgent(model=model)
        self.fix_agent = FixAgent(model=model)
        self.compiler_agent = CompilerAgent()  # NEW
        self.model = model
        
        # AgentOps components
        self.evaluator = AgentEvaluations()
        self.sandbox = SandboxedExecutor()
        self.tracer = LangSmithTracing()
        
        # Create workflow graph
        self.workflow = StateGraph(ReviewState)
        
        # Add nodes
        self.workflow.add_node("security_agent", self.run_security_agent)
        self.workflow.add_node("style_agent", self.run_style_agent)
        self.workflow.add_node("fix_agent", self.run_fix_agent)
        self.workflow.add_node("compiler_agent", self.run_compiler_agent)  # NEW
        self.workflow.add_node("reporter_agent", self.run_reporter_agent)
        
        # Define edges
        self.workflow.set_entry_point("security_agent")
        self.workflow.add_edge("security_agent", "style_agent")
        self.workflow.add_edge("style_agent", "fix_agent")
        self.workflow.add_edge("fix_agent", "compiler_agent")  # NEW
        self.workflow.add_edge("compiler_agent", "reporter_agent")
        self.workflow.add_edge("reporter_agent", END)
        
        # Compile
        self.app = self.workflow.compile()
    
    def run_security_agent(self, state: ReviewState) -> ReviewState:
        """Run security analysis"""
        findings = self.security_agent.review(state['code'], state['filename'])
        state['security_findings'] = findings
        return state
    
    def run_style_agent(self, state: ReviewState) -> ReviewState:
        """Run style analysis"""
        findings = self.style_agent.review(state['code'], state['filename'])
        state['style_findings'] = findings
        return state
    
    def run_fix_agent(self, state: ReviewState) -> ReviewState:
        """
        Run fix agent - UNIQUE FEATURE: Auto-generate fixed code
        """
        print("🔧 [Agent 3/5] Fix Agent generating fixes...")
        
        # Combine all findings
        all_findings = state['security_findings'] + state['style_findings']
        
        # Generate fixes
        fix_result = self.fix_agent.generate_fixes_for_all(
            state['code'],
            all_findings,
            state['filename']
        )
        
        state['fixed_code'] = fix_result['fixed_code']
        state['fixes_applied'] = fix_result['fixes_applied']
        state['fix_details'] = fix_result.get('fix_details', [])
        
        return state
    
    def run_compiler_agent(self, state: ReviewState) -> ReviewState:
        """
        Run compiler agent - VALIDATES CODE COMPILES
        If compilation fails, loops back to Fix Agent for retry
        """
        print("🔍 [Agent 4/5] Compiler Agent validating code...")
        
        original_code = state['code']
        fixed_code = state['fixed_code']
        filename = state['filename']  # Get filename
        
        # Validate and retry if needed
        final_code, compilation_result, retry_count = self.compiler_agent.validate_and_retry(
            original_code=original_code,
            fixed_code=fixed_code,
            llm_invoke_func=lambda prompt: self.fix_agent.llm.invoke(prompt).content,
            max_retries=3,
            filename=filename  # Pass filename
        )
        
        # Update state
        state['fixed_code'] = final_code
        state['compilation_success'] = compilation_result['success']
        state['compilation_errors'] = compilation_result.get('errors', [])
        state['retry_count'] = retry_count
        
        # Show appropriate message based on result
        if compilation_result.get('skipped', False):
            print(f"ℹ️ Compilation check skipped for {filename}")
            print(f"   Reason: {compilation_result['errors']}")
        elif compilation_result['success']:
            print(f"✅ Compilation successful after {retry_count} retry/ies!")
        else:
            print(f"⚠️ Compilation failed after {retry_count} retries")
            for error in compilation_result.get('errors', []):
                print(f"   ❌ {error}")
        
        return state
    
    def run_reporter_agent(self, state: ReviewState) -> ReviewState:
        """Generate final report"""
        report = {
            'filename': state['filename'],
            'security_issues': len(state['security_findings']),
            'style_issues': len(state['style_findings']),
            'total_issues': len(state['security_findings']) + len(state['style_findings']),
            'security_findings': state['security_findings'],
            'style_findings': state['style_findings'],
            'risk_level': self._calculate_risk_level(state['security_findings']),
            'score': self._calculate_score(state),
            'model_used': self.model,
            'completed': True,
            # Auto-fix results
            'has_fixed_code': state.get('fixes_applied', 0) > 0,
            'fixes_applied': state.get('fixes_applied', 0),
            'fixed_code': state.get('fixed_code', ''),
            'original_code': state['code'],
            'fix_comparison': self.fix_agent.compare_codes(
                state['code'],
                state.get('fixed_code', state['code'])
            ) if state.get('fixed_code') else None,
            # Compiler results (NEW)
            'compilation_success': state.get('compilation_success', True),
            'compilation_errors': state.get('compilation_errors', []),
            'retry_count': state.get('retry_count', 0)
        }
        state['final_report'] = report
        state['completed'] = True
        return state
    
    def _calculate_risk_level(self, security_findings: List[Dict]) -> str:
        """Calculate overall risk level"""
        for finding in security_findings:
            severity = finding.get('severity', 'Info')
            if severity == 'Critical':
                return '🔴 Critical'
            elif severity == 'High':
                return '🟠 High'
            elif severity == 'Medium':
                return '🟡 Medium'
        return '🟢 Low'
    
    def _calculate_score(self, state: ReviewState) -> int:
        """Calculate code quality score (0-100)"""
        score = 100
        
        # Deduct for security issues
        for finding in state['security_findings']:
            severity = finding.get('severity', 'Info')
            if severity == 'Critical':
                score -= 25
            elif severity == 'High':
                score -= 15
            elif severity == 'Medium':
                score -= 8
            elif severity == 'Low':
                score -= 3
        
        # Deduct for style issues
        score -= len(state['style_findings']) * 2
        
        # Bonus for auto-fixes applied
        if state.get('fixes_applied', 0) > 0:
            score = min(100, score + 5)
        
        # Bonus for successful compilation
        if state.get('compilation_success', True):
            score = min(100, score + 2)
        
        return max(0, min(100, score))
    
    def review(self, code: str, filename: str) -> Dict:
        """Run complete review with auto-fix + compiler validation"""
        start_time = time.time()
        
        initial_state = {
            'code': code,
            'filename': filename,
            'security_findings': [],
            'style_findings': [],
            'final_report': {},
            'completed': False,
            'processing_time': 0,
            'fixed_code': '',
            'fixes_applied': 0,
            'fix_details': [],
            'compilation_success': True,
            'compilation_errors': [],
            'retry_count': 0
        }
        
        result = self.app.invoke(initial_state)
        
        # ✅ FIX: Add processing_time to final_report (not just result)
        processing_time = time.time() - start_time
        result['final_report']['processing_time'] = processing_time
        
        return result['final_report']
    
    def review_with_agentops(self, code: str, filename: str) -> Dict:
        """Run review with full AgentOps + Auto-Fix + Compiler"""
        self.tracer.setup_tracing()
        
        report = self.review(code, filename)
        
        metrics = self.evaluator.calculate_metrics(report, report.get('processing_time', 0))
        self.evaluator.save_review(report, metrics, filename)
        
        report['metrics'] = {
            'total_issues': metrics.total_issues,
            'security_issues': metrics.security_issues,
            'style_issues': metrics.style_issues,
            'quality_score': metrics.quality_score,
            'false_positive_rate': metrics.false_positive_rate,
            'processing_time': metrics.processing_time,
            'cost_per_task': metrics.cost_per_task,
            'latency_ms': metrics.latency_ms,
            'goal_success_rate': metrics.goal_success_rate,
            'fixes_applied': report.get('fixes_applied', 0),
            'compilation_success': report.get('compilation_success', True),
            'retry_count': report.get('retry_count', 0)
        }
        
        self.tracer.trace_agent_execution(
            agent_name="Multi-Agent Review with Auto-Fix + Compiler",
            input_data={'filename': filename, 'code_length': len(code)},
            output_data=report
        )
        
        return report
    
    def save_fixed_code(self, report: Dict, output_path: str):
        """Save fixed code to file"""
        if report.get('fixed_code'):
            with open(output_path, 'w') as f:
                f.write(report['fixed_code'])
            return True
        return False
    
    def get_benchmark_report(self) -> Dict:
        """Get benchmark report"""
        return self.evaluator.generate_benchmark_report()
    
    def get_performance_summary(self) -> str:
        """Get performance summary"""
        return self.evaluator.get_performance_summary()
    
    def verify_code_safety(self, code: str) -> Dict:
        """Verify code safety"""
        return self.sandbox.verify_safe_code(code)
    
    def get_sandbox_status(self) -> Dict:
        """Get sandbox status"""
        return {
            'docker_enabled': self.sandbox.docker_enabled,
            'memory_limit': self.sandbox.memory_limit,
            'cpu_limit': self.sandbox.cpu_limit
        }
    
    def get_tracing_status(self) -> Dict:
        """Get tracing status"""
        return {
            'enabled': self.tracer.enabled,
            'project_name': self.tracer.project_name,
            'tracing_url': self.tracer.get_tracing_url() if self.tracer.enabled else None
        }
