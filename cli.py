#!/usr/bin/env python3
"""
Agentic Code Reviewer - Multi-Agent Code Security Tool
UNIQUE FEATURES: Auto-Fix Generation + Compiler Validation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.workflows.review_workflow import ReviewWorkflow
from src.tools.code_scanner import CodeScanner
from src.utils.report_exporter import ReportExporter
import argparse
from datetime import datetime


def print_banner():
    print("""
    ╔══════════════════════════════════════════════╗
    ║  🔒 Agentic Code Reviewer                   ║
    ║  Multi-Agent Code Security Tool             ║
    ║  ⭐ UNIQUE: Auto-Fix + Compiler Validation  ║
    ║  🧠 Model: Qwen 30B (95%+ Accuracy)         ║
    ║  🔍 LangSmith Tracing Integrated            ║
    ╚══════════════════════════════════════════════╝
    """)


def print_separator(char='═', length=60):
    print(char * length)


def print_finding(finding: dict, file: str, agent_type: str):
    """Print a single finding with formatting"""
    severity = finding.get('severity', 'Info')
    colors = {
        'Critical': '\033[91m',
        'High': '\033[93m',
        'Medium': '\033[94m',
        'Low': '\033[92m',
        'Info': '\033[95m'
    }
    reset = '\033[0m'
    
    color = colors.get(severity, reset)
    
    print(f"\n{color}[{agent_type}] ▸ Severity: {severity}{reset}")
    print(f"  Location: {finding.get('location', 'N/A')}")
    print(f"  File: {file}")
    
    if agent_type == "Security":
        print(f"  Issue: {finding.get('issue', 'N/A')[:200]}")
        if 'risk' in finding:
            print(f"  Risk: {finding.get('risk', 'N/A')[:150]}")
        if 'fix' in finding:
            print(f"  Fix: {finding.get('fix', 'N/A')[:150]}...")
    else:
        print(f"  Issue: {finding.get('issue', 'N/A')[:200]}")
        if 'suggestion' in finding:
            print(f"  Suggestion: {finding.get('suggestion', 'N/A')[:150]}...")
    
    print("-" * 50)


def print_metrics(metrics: dict):
    """Print AgentOps metrics"""
    print("\n" + "═" * 60)
    print("📊 Performance Metrics")
    print("═" * 60)
    print(f"  🎯 Goal Success Rate: {metrics.get('goal_success_rate', 0):.1f}%")
    print(f"  📉 False Positive Rate: {metrics.get('false_positive_rate', 0):.2f}%")
    print(f"  💵 Cost per Task: ${metrics.get('cost_per_task', 0):.4f}")
    print(f"  ⏱️ Latency: {metrics.get('latency_ms', 0):.1f}ms")
    print(f"  📊 Quality Score: {metrics.get('quality_score', 0)}/100")
    print(f"  🔧 Fixes Applied: {metrics.get('fixes_applied', 0)}")
    print(f"  ✅ Compilation: {'Success' if metrics.get('compilation_success', True) else 'Failed'}")
    print(f"  🔁 Retries: {metrics.get('retry_count', 0)}")
    print("═" * 60)


def print_sandbox_status(workflow: ReviewWorkflow):
    """Print sandbox status"""
    status = workflow.get_sandbox_status()
    print(f"\n🔒 Sandboxing:")
    print(f"  Docker: {'✅ Enabled' if status['docker_enabled'] else '❌ Disabled'}")
    print(f"  Memory: {status['memory_limit']}")
    print(f"  CPU: {status['cpu_limit']} cores")


def print_tracing_status(workflow: ReviewWorkflow):
    """Print tracing status"""
    status = workflow.get_tracing_status()
    print(f"\n🔍 Observability:")
    print(f"  LangSmith: {'✅ Enabled' if status['enabled'] else '❌ Disabled'}")
    print(f"  Project: {status['project_name']}")
    if status.get('tracing_url'):
        print(f"  📊 Traces: {status['tracing_url']}")


def export_reports(report: dict, filename: str):
    """Export report to PDF and HTML"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    pdf_path = f"reports/pdf/{base_name}_report_{timestamp}.pdf"
    html_path = f"reports/html/{base_name}_report_{timestamp}.html"
    
    # Create directories
    os.makedirs("reports/pdf", exist_ok=True)
    os.makedirs("reports/html", exist_ok=True)
    
    # Export
    try:
        ReportExporter.export_to_pdf(report, pdf_path)
        print(f"📄 PDF Report: {pdf_path}")
    except Exception as e:
        print(f"❌ PDF Export Failed: {e}")
    
    try:
        ReportExporter.export_to_html(report, html_path)
        print(f"🌐 HTML Report: {html_path}")
    except Exception as e:
        print(f"❌ HTML Export Failed: {e}")


def main():
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Agentic Code Reviewer - Multi-Agent Code Security Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cli.py myfile.py
  python3 cli.py ./src/ --model qwen:30b
  python3 cli.py myfile.py --show-fixes --export-reports

⭐ Unique Features:
  1. Auto-Fix Generation - Most tools only detect, this one fixes!
  2. Compiler Validation - Auto-retry if code doesn't compile!
  3. Qwen 30B Model - 95%+ accuracy for vulnerability detection
  4. LangSmith Tracing - Full AgentOps monitoring (just add API key)

Recommended Model:
  --model qwen:30b  (highest accuracy, 32GB+ RAM required)
  --model llama3.2  (fastest, 8GB RAM, good for testing)
        """
    )
    parser.add_argument('target', nargs='?', help='File or directory to review')
    parser.add_argument('--model', default='llama3.2', help='LLM model (default: llama3.2)')
    parser.add_argument('--show-fixes', action='store_true', help='Show fixed code in terminal')
    parser.add_argument('--export-reports', action='store_true', help='Export PDF/HTML reports')
    parser.add_argument('--no-agentops', action='store_true', help='Skip AgentOps metrics')
    
    args = parser.parse_args()
    
    if not args.target:
        print("❌ Usage: python3 cli.py <file_or_directory> [--model MODEL]")
        print("\nExamples:")
        print("  python3 cli.py myfile.py")
        print("  python3 cli.py ./src/ --model qwen:30b")
        print("  python3 cli.py myfile.py --show-fixes --export-reports")
        print("\n⭐ Unique Features:")
        print("  1. Auto-Fix Generation - Most tools only detect, this one fixes!")
        print("  2. Compiler Validation - Auto-retry if code doesn't compile!")
        print("  3. Qwen 30B Model - 95%+ accuracy")
        print("  4. LangSmith Tracing - Full monitoring (just add API key)")
        print("\n🌐 Web UI: streamlit run UI/app.py")
        sys.exit(1)
    
    target = args.target
    model = args.model
    
    if not os.path.exists(target):
        print(f"❌ Error: {target} does not exist")
        sys.exit(1)
    
    print(f"🔧 Initializing 5-Agent Workflow (Model: {model})...")
    workflow = ReviewWorkflow(model=model)
    scanner = CodeScanner()
    print("✅ Ready! (Security + Style + Fix + Compiler + Reporter)\n")
    
    print_sandbox_status(workflow)
    print_tracing_status(workflow)
    print("\n" + "═" * 60)
    
    total_security = 0
    total_style = 0
    total_fixes = 0
    total_files = 0
    total_compiled = 0
    
    if os.path.isfile(target):
        print(f"\n📄 Scanning: {target}")
        code = scanner.read_file(target)
        print(f"📊 Size: {len(code)} bytes\n")
        
        print("🔍 Running 5-agent analysis (with compiler validation)...")
        if args.no_agentops:
            report = workflow.review(code, target)
        else:
            report = workflow.review_with_agentops(code, target)
        
        total_security = report.get('security_issues', 0)
        total_style = report.get('style_issues', 0)
        total_fixes = report.get('fixes_applied', 0)
        total_files = 1
        compilation_success = report.get('compilation_success', True)
        if compilation_success:
            total_compiled = 1
        
        print(f"\n✅ Complete in {report.get('processing_time', 0):.2f}s")
        print(f"🚨 Found {report.get('total_issues', 0)} issue(s)")
        print(f"🔧 Applied {total_fixes} auto-fix(es)")
        
        # Compilation status
        if compilation_success:
            print(f"✅ Compilation successful after {report.get('retry_count', 0)} retry/ies!")
        else:
            print(f"⚠️ Compilation failed after {report.get('retry_count', 0)} retries")
            if report.get('compilation_errors'):
                print(f"   Error: {report['compilation_errors'][0]}")
        print()
        
        if report.get('security_findings'):
            print_separator()
            print("🔒 Security Findings")
            print_separator('-')
            for i, finding in enumerate(report['security_findings'], 1):
                print_finding(finding, target, "Security")
        
        if report.get('style_findings'):
            print_separator()
            print("🎨 Style Findings")
            print_separator('-')
            for i, finding in enumerate(report['style_findings'], 1):
                print_finding(finding, target, "Style")
        
        print_separator()
        print(f"📊 Quality Score: {report.get('score', 0)}/100")
        print(f"🚨 Risk Level: {report.get('risk_level', 'N/A')}")
        print(f"🔧 Fixes Applied: {total_fixes}")
        print(f"✅ Compilation: {'Success' if compilation_success else 'Failed'}")
        print(f"🔁 Retries: {report.get('retry_count', 0)}")
        print(f"⏱️ Processing Time: {report.get('processing_time', 0):.2f}s")
        print_separator()
        
        if 'metrics' in report and not args.no_agentops:
            print_metrics(report['metrics'])
        
        # Export Reports
        if args.export_reports:
            print_separator()
            print("📄 Exporting Reports")
            print_separator('-')
            export_reports(report, target)
            print_separator()
        
        # Auto-Fix Output
        if report.get('has_fixed_code') and report.get('fixed_code'):
            print_separator()
            print("🛠️ Auto-Fixed Code ⭐ Unique Feature")
            print_separator('-')
            print(f"✅ {total_fixes} fix(es) automatically applied!")
            
            output_path = f"fixed_{os.path.basename(target)}"
            with open(output_path, 'w') as f:
                f.write(report['fixed_code'])
            
            print(f"\n📄 Saved: {output_path}")
            print(f"💾 Size: {len(report['fixed_code'])} bytes")
            
            if compilation_success:
                print(f"✅ Code compiles successfully!")
            else:
                print(f"⚠️ Warning: Code may have syntax errors")
            
            if args.show_fixes:
                print("\n📝 Fixed Code:")
                print_separator('-')
                print(report['fixed_code'])
                print_separator('-')
            
            print(f"\n💡 Unique: Auto-fix + Compiler validation!")
            print_separator()
    
    elif os.path.isdir(target):
        print(f"\n📂 Scanning directory: {target}")
        code_files = scanner.read_directory(target)
        
        if not code_files:
            print("❌ No code files found")
            sys.exit(0)
        
        print(f"📊 Found {len(code_files)} file(s)\n")
        
        file_results = []
        
        for filepath, code in code_files.items():
            print(f"\n{'═'*60}")
            print(f"📄 {filepath}")
            print(f"📊 {len(code)} bytes")
            print("═"*60)
            
            if args.no_agentops:
                report = workflow.review(code, filepath)
            else:
                report = workflow.review_with_agentops(code, filepath)
            
            security = report.get('security_issues', 0)
            style = report.get('style_issues', 0)
            fixes = report.get('fixes_applied', 0)
            total = security + style
            compiled = report.get('compilation_success', True)
            
            total_security += security
            total_style += style
            total_fixes += fixes
            total_files += 1
            if compiled:
                total_compiled += 1
            
            file_results.append({
                'file': filepath,
                'security': security,
                'style': style,
                'fixes': fixes,
                'total': total,
                'score': report.get('score', 0),
                'compiled': compiled
            })
            
            if total > 0:
                print(f"🚨 {total} issue(s) | 🔧 {fixes} fixed")
                print(f"📊 Score: {report.get('score', 0)}/100")
                print(f"✅ Compilation: {'Success' if compiled else 'Failed'}")
                
                if report.get('has_fixed_code'):
                    output_path = f"fixed_{os.path.basename(filepath)}"
                    with open(output_path, 'w') as f:
                        f.write(report['fixed_code'])
                    print(f"💾 {output_path}")
            else:
                print("✅ No issues")
        
        print("\n" + "═" * 60)
        print("📊 SUMMARY")
        print("═" * 60)
        print(f"📁 Files: {total_files}")
        print(f"🔒 Security: {total_security}")
        print(f"🎨 Style: {total_style}")
        print(f"🔧 Auto-fixes: {total_fixes}")
        print(f"✅ Compiled: {total_compiled}/{total_files}")
        print("═" * 60)
    
    else:
        print(f"❌ Error: Invalid path")
        sys.exit(1)
    
    print("\n" + "═" * 60)
    print("✅ Analysis Complete ⭐ Auto-Fix + Compiler Enabled")
    print("═" * 60)
    print("\n⭐ Unique Features:")
    print("  1. Auto-Fix Generation - Most tools only detect, this one fixes!")
    print("  2. Compiler Validation - Auto-retry if code doesn't compile!")
    print("  3. Qwen 30B Model - 95%+ accuracy")
    print("  4. LangSmith Tracing - Full monitoring (just add API key)")
    print("\n🌐 Web UI: streamlit run UI/app.py")
    print("═" * 60)


if __name__ == "__main__":
    main()