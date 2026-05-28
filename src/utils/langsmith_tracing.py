"""
LangSmith Tracing for Observability
Using LangSmith to debug long-running autonomous traces
"""
import os
from typing import Dict, Optional
from datetime import datetime

class LangSmithTracing:
    """
    Setup and manage LangSmith tracing
    """
    
    def __init__(self):
        self.enabled = self._check_enabled()
        self.project_name = os.getenv('LANGCHAIN_PROJECT', 'agentic-code-reviewer')
    
    def _check_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled"""
        api_key = os.getenv('LANGCHAIN_API_KEY', '')
        tracing_v2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower()
        
        return bool(api_key) and tracing_v2 == 'true'
    
    def setup_tracing(self) -> bool:
        """
        Setup LangSmith tracing
        Returns: True if successfully configured
        """
        if not self.enabled:
            print("⚠️ LangSmith tracing is disabled. Set in .env to enable:")
            print("   LANGCHAIN_API_KEY=your_api_key")
            print("   LANGCHAIN_TRACING_V2=true")
            return False
        
        try:
            # Import and setup
            from langsmith import Client
            client = Client()
            
            # Verify project exists
            try:
                project = client.read_project(project_name=self.project_name)
            except:
                # Create project if doesn't exist
                project = client.create_project(project_name=self.project_name)
            
            print(f"✅ LangSmith tracing enabled for project: {self.project_name}")
            return True
        
        except Exception as e:
            print(f"❌ LangSmith setup failed: {e}")
            return False
    
    def trace_agent_execution(self, agent_name: str, input_data: Dict, output_data: Dict):
        """Trace agent execution with LangSmith"""
        if not self.enabled:
            return
        
        try:
            from langsmith import traceable
            
            @traceable(run_type="chain", name=f"{agent_name}_execution")
            def trace_run(input: Dict) -> Dict:
                return output_data
            
            trace_run(input_data)
        
        except Exception as e:
            print(f"⚠️ Tracing error: {e}")
    
    def get_tracing_url(self) -> Optional[str]:
        """Get URL to view traces in LangSmith UI"""
        if not self.enabled:
            return None
        
        return f"https://smith.langchain.com/o/{os.getenv('LANGCHAIN_API_KEY')}/projects/p/{self.project_name}"
    
    def generate_tracing_report(self, reviews: list) -> Dict:
        """Generate observability report"""
        if not reviews:
            return {'message': 'No tracing data available'}
        
        total_traces = len(reviews)
        avg_processing_time = sum(r.get('processing_time', 0) for r in reviews) / total_traces
        
        return {
            'total_traces': total_traces,
            'avg_processing_time': round(avg_processing_time, 2),
            'tracing_enabled': self.enabled,
            'project_name': self.project_name,
            'tracing_url': self.get_tracing_url() if self.enabled else None,
            'recommendation': 'Enable LangSmith for detailed trace visualization' if not self.enabled else 'Tracing active'
        }
