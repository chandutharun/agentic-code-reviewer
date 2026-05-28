"""
Evaluation Metrics for Agentic Code Reviewer
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EvaluationMetrics:
    """Data class for evaluation metrics"""
    total_issues: int
    security_issues: int
    style_issues: int
    quality_score: int
    risk_level: str
    false_positive_rate: float
    processing_time: float
    cost_per_task: float
    latency_ms: float
    goal_success_rate: float

class AgentEvaluations:
    """Evaluation and benchmarking for agents"""
    
    def __init__(self):
        self.reviews_history = []
    
    def calculate_metrics(self, report: Dict, processing_time: float = 0) -> EvaluationMetrics:
        """Calculate comprehensive evaluation metrics"""
        total_issues = report.get('total_issues', 0)
        security_issues = report.get('security_issues', 0)
        style_issues = report.get('style_issues', 0)
        quality_score = report.get('score', 0)
        
        # Estimate false positive rate (simplified - in production, use human feedback)
        false_positive_rate = self._estimate_false_positive_rate(report)
        
        # Calculate cost (estimate based on tokens)
        cost_per_task = self._estimate_cost(report)
        
        # Latency
        latency_ms = processing_time * 1000
        
        # Goal success rate (did we find issues?)
        goal_success_rate = 100.0 if total_issues > 0 else 0.0
        
        return EvaluationMetrics(
            total_issues=total_issues,
            security_issues=security_issues,
            style_issues=style_issues,
            quality_score=quality_score,
            risk_level=report.get('risk_level', 'N/A'),
            false_positive_rate=false_positive_rate,
            processing_time=processing_time,
            cost_per_task=cost_per_task,
            latency_ms=latency_ms,
            goal_success_rate=goal_success_rate
        )
    
    def _estimate_false_positive_rate(self, report: Dict) -> float:
        """Estimate false positive rate based on finding quality"""
        security_findings = report.get('security_findings', [])
        
        if not security_findings:
            return 0.0
        
        # Score based on finding completeness
        complete_findings = 0
        for finding in security_findings:
            if finding.get('issue') and finding.get('fix'):
                complete_findings += 1
        
        # Higher completeness = lower false positive rate
        completeness_rate = complete_findings / len(security_findings)
        estimated_fp_rate = (1 - completeness_rate) * 0.3  # Max 30% FP rate
        
        return round(estimated_fp_rate * 100, 2)
    
    def _estimate_cost(self, report: Dict) -> float:
        """Estimate cost per task (simplified)"""
        total_issues = report.get('total_issues', 0)
        # Estimate: $0.001 per finding (very rough estimate)
        return round(total_issues * 0.001 + 0.005, 4)
    
    def save_review(self, report: Dict, metrics: EvaluationMetrics, filename: str = ""):
        """Save review for benchmarking"""
        review_record = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'report': report,
            'metrics': {
                'total_issues': metrics.total_issues,
                'security_issues': metrics.security_issues,
                'style_issues': metrics.style_issues,
                'quality_score': metrics.quality_score,
                'risk_level': metrics.risk_level,
                'false_positive_rate': metrics.false_positive_rate,
                'processing_time': metrics.processing_time,
                'cost_per_task': metrics.cost_per_task,
                'latency_ms': metrics.latency_ms,
                'goal_success_rate': metrics.goal_success_rate
            }
        }
        self.reviews_history.append(review_record)
    
    def generate_benchmark_report(self) -> Dict:
        """Generate benchmark report across all reviews"""
        if not self.reviews_history:
            return {
                'total_reviews': 0,
                'message': 'No reviews yet'
            }
        
        total_reviews = len(self.reviews_history)
        total_issues = sum(r['metrics']['total_issues'] for r in self.reviews_history)
        avg_score = sum(r['metrics']['quality_score'] for r in self.reviews_history) / total_reviews
        avg_processing_time = sum(r['metrics']['processing_time'] for r in self.reviews_history) / total_reviews
        avg_cost = sum(r['metrics']['cost_per_task'] for r in self.reviews_history) / total_reviews
        avg_latency = sum(r['metrics']['latency_ms'] for r in self.reviews_history) / total_reviews
        avg_success_rate = sum(r['metrics']['goal_success_rate'] for r in self.reviews_history) / total_reviews
        
        # Goal success rate: % of reviews that found at least one issue
        reviews_with_issues = sum(1 for r in self.reviews_history if r['metrics']['total_issues'] > 0)
        goal_success_rate = (reviews_with_issues / total_reviews) * 100
        
        return {
            'total_reviews': total_reviews,
            'total_issues_found': total_issues,
            'avg_quality_score': round(avg_score, 2),
            'avg_processing_time': round(avg_processing_time, 2),
            'avg_cost_per_task': round(avg_cost, 4),
            'avg_latency_ms': round(avg_latency, 2),
            'goal_success_rate': round(goal_success_rate, 2),
            'reviews': self.reviews_history
        }
    
    def get_performance_summary(self) -> str:
        """Get human-readable performance summary"""
        benchmark = self.generate_benchmark_report()
        
        if benchmark['total_reviews'] == 0:
            return "No reviews completed yet."
        
        summary = f"""
📊 Agent Performance Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Reviews: {benchmark['total_reviews']}
Total Issues Found: {benchmark['total_issues_found']}
Average Quality Score: {benchmark['avg_quality_score']}/100
Average Processing Time: {benchmark['avg_processing_time']:.2f}s
Average Cost per Task: ${benchmark['avg_cost_per_task']:.4f}
Average Latency: {benchmark['avg_latency_ms']:.2f}ms
Goal Success Rate: {benchmark['goal_success_rate']:.2f}%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary
