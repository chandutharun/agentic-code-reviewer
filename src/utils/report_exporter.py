from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os


class ReportExporter:
    @staticmethod
    def export_to_html(report, output_path):
        """Export report to HTML with full details"""
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Review Report - QA Score: {report.get('score', 0)}/100</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1e3d59;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #667eea;
            margin-top: 30px;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: {"#28a745" if report.get('score', 0) >= 80 else "#ffc107" if report.get('score', 0) >= 50 else "#dc3545"};
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            font-size: 14px;
            color: #6c757d;
        }}
        .finding {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .finding-critical {{ border-left-color: #dc3545; background: #f8d7da; }}
        .finding-high {{ border-left-color: #ffc107; background: #fff3cd; }}
        .finding-medium {{ border-left-color: #17a2b8; background: #d1ecf1; }}
        .finding-low {{ border-left-color: #28a745; background: #d4edda; }}
        .code-block {{
            background: #262730;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 10px 0;
            white-space: pre-wrap;
        }}
        .summary {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Code Review Report</h1>
        
        <div class="summary">
            <h2>📊 Quality Score</h2>
            <div class="score">{report.get('score', 0)}/100</div>
            <p><strong>Risk Level:</strong> {report.get('risk_level', 'N/A')}</p>
            <p><strong>File:</strong> {report.get('filename', 'N/A')}</p>
            <p><strong>Model:</strong> {report.get('model_used', 'llama3.2')}</p>
            <p><strong>Processing Time:</strong> {report.get('processing_time', 0):.2f} seconds</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{report.get('security_issues', 0)}</div>
                <div class="metric-label">🔒 Security Issues</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.get('style_issues', 0)}</div>
                <div class="metric-label">🎨 Style Issues</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report.get('fixes_applied', 0)}</div>
                <div class="metric-label">🔧 Fixes Applied</div>
            </div>
            <div class="metric">
                <div class="metric-value">{"✅" if report.get('compilation_success', False) else "❌"}</div>
                <div class="metric-label">Compilation</div>
            </div>
        </div>
"""
        
        # Security Findings
        if report.get('security_findings'):
            html_content += """
        <h2>🔒 Security Findings</h2>
"""
            for i, finding in enumerate(report['security_findings'], 1):
                severity = finding.get('severity', 'Info').lower()
                html_content += f"""
        <div class="finding finding-{severity}">
            <h3>Finding #{i} - {finding.get('severity', 'Info')}</h3>
            <p><strong>Issue:</strong> {finding.get('issue', 'N/A')}</p>
"""
                if finding.get('location'):
                    html_content += f"<p><strong>Location:</strong> {finding.get('location')}</p>"
                if finding.get('risk'):
                    html_content += f"<p><strong>Risk:</strong> {finding.get('risk')}</p>"
                if finding.get('fix'):
                    html_content += f"""
            <p><strong>Suggested Fix:</strong></p>
            <div class="code-block">{finding.get('fix', 'N/A')}</div>
"""
            html_content += """
        <hr>
"""
        
        # Style Findings
        if report.get('style_findings'):
            html_content += """
        <h2>🎨 Style Findings</h2>
"""
            for i, finding in enumerate(report['style_findings'], 1):
                html_content += f"""
        <div class="finding">
            <p><strong>Finding #{i}:</strong> {finding.get('issue', 'N/A')}</p>
"""
                if finding.get('suggestion'):
                    html_content += f"<p><strong>Suggestion:</strong> {finding.get('suggestion')}</p>"
            html_content += """
        <hr>
"""
        
        # Fixed Code
        if report.get('has_fixed_code') and report.get('fixed_code'):
            html_content += f"""
        <h2>🛠️ Auto-Fixed Code</h2>
        <div class="summary">
            <p>✅ <strong>{report.get('fixes_applied', 0)} fix(es) automatically applied!</strong></p>
        </div>
        
        <h3>📄 Original Code</h3>
        <div class="code-block">{report.get('original_code', 'N/A')}</div>
        
        <h3>✅ Fixed Code</h3>
        <div class="code-block">{report.get('fixed_code', 'N/A')}</div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        # Write HTML file
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    @staticmethod
    def export_to_pdf(report, output_path):
        """Export report to PDF with FULL details and proper formatting"""
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3d59'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=20,
            leading=18
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=8,
            alignment=TA_LEFT,
            leading=14,
            wordWrap='CJK'  # ✅ FIX: Enable text wrapping
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Courier',
            textColor=colors.black,
            spaceAfter=10,
            backColor=colors.HexColor('#f4f4f4'),
            borderLeftWidth=4,
            borderLeftColor=colors.HexColor('#667eea'),
            leftIndent=20,
            leading=10,
            wordWrap='Normal'  # ✅ FIX: Enable code wrapping
        )
        
        # Title
        story.append(Paragraph("🔒 Code Review Report", title_style))
        story.append(Spacer(1, 25))
        
        # Summary Table
        summary_data = [
            ['Quality Score', f"{report.get('score', 0)}/100"],
            ['Risk Level', report.get('risk_level', 'N/A')],
            ['File', report.get('filename', 'N/A')],
            ['Model', report.get('model_used', 'llama3.2')],
            ['Processing Time', f"{report.get('processing_time', 0):.2f} seconds"],  # ✅ Shows actual time
            ['Compilation', '✅ Successful' if report.get('compilation_success', False) else '❌ Failed']
        ]
        
        summary_table = Table(summary_data, colWidths=[3.2*inch, 2.3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e7f3ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ('valign', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 25))
        
        # Key Metrics
        story.append(Paragraph("📊 Key Metrics", heading_style))
        
        metrics_data = [
            ['🔒 Security Issues', str(report.get('security_issues', 0))],
            ['🎨 Style Issues', str(report.get('style_issues', 0))],
            ['🔧 Fixes Applied', str(report.get('fixes_applied', 0))],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3.2*inch, 2.3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ('valign', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 25))
        
        # Security Findings with text wrapping
        if report.get('security_findings'):
            story.append(Paragraph("🔒 Security Findings", heading_style))
            
            for i, finding in enumerate(report['security_findings'], 1):
                severity = finding.get('severity', 'Info')
                story.append(Paragraph(f"<b>Finding #{i} - {severity}</b>", normal_style))
                
                # Wrap text at ~150 characters
                issue_text = finding.get('issue', 'N/A')
                if len(issue_text) > 150:
                    words = issue_text.split()
                    chunks = [' '.join(words[j:j+150]) for j in range(0, len(words), 150)]
                    for chunk in chunks:
                        story.append(Paragraph(chunk, normal_style))
                else:
                    story.append(Paragraph(issue_text, normal_style))
                
                if finding.get('location'):
                    story.append(Paragraph(f"<b>Location:</b> {finding.get('location')}", normal_style))
                
                if finding.get('risk'):
                    risk_text = finding.get('risk', '')
                    if len(risk_text) > 150:
                        words = risk_text.split()
                        chunks = [' '.join(words[j:j+150]) for j in range(0, len(words), 150)]
                        for chunk in chunks:
                            story.append(Paragraph(f"<b>Risk:</b> {chunk}", normal_style))
                    else:
                        story.append(Paragraph(f"<b>Risk:</b> {risk_text}", normal_style))
                
                if finding.get('fix'):
                    story.append(Paragraph("<b>Suggested Fix:</b>", normal_style))
                    fix_text = finding.get('fix', 'N/A')[:800]
                    fix_text = fix_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    fix_text = fix_text.replace('\n', '<br/>')
                    story.append(Paragraph(fix_text, code_style))
                
                story.append(Spacer(1, 15))
            
            story.append(PageBreak())
        
        # Style Findings with text wrapping
        if report.get('style_findings'):
            story.append(Paragraph("🎨 Style Findings", heading_style))
            
            for i, finding in enumerate(report['style_findings'], 1):
                story.append(Paragraph(f"<b>Finding #{i}:</b>", normal_style))
                
                issue_text = finding.get('issue', 'N/A')
                if len(issue_text) > 150:
                    words = issue_text.split()
                    chunks = [' '.join(words[j:j+150]) for j in range(0, len(words), 150)]
                    for chunk in chunks:
                        story.append(Paragraph(chunk, normal_style))
                else:
                    story.append(Paragraph(issue_text, normal_style))
                
                if finding.get('suggestion'):
                    suggestion_text = finding.get('suggestion', '')
                    if len(suggestion_text) > 150:
                        words = suggestion_text.split()
                        chunks = [' '.join(words[j:j+150]) for j in range(0, len(words), 150)]
                        for chunk in chunks:
                            story.append(Paragraph(f"<b>Suggestion:</b> {chunk}", normal_style))
                    else:
                        story.append(Paragraph(f"<b>Suggestion:</b> {suggestion_text}", normal_style))
                
                story.append(Spacer(1, 12))
            
            story.append(PageBreak())
        
        # Fixed Code
        if report.get('has_fixed_code') and report.get('fixed_code'):
            story.append(Paragraph("🛠️ Auto-Fixed Code", heading_style))
            story.append(Paragraph(f"✅ {report.get('fixes_applied', 0)} fix(es) automatically applied!", normal_style))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("<b>📄 Original Code:</b>", normal_style))
            original_code = report.get('original_code', 'N/A')[:1500]
            original_code_escaped = original_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            original_code_escaped = original_code_escaped.replace('\n', '<br/>')
            story.append(Paragraph(original_code_escaped, code_style))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("<b>✅ Fixed Code:</b>", normal_style))
            fixed_code = report.get('fixed_code', 'N/A')[:1500]
            fixed_code_escaped = fixed_code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            fixed_code_escaped = fixed_code_escaped.replace('\n', '<br/>')
            story.append(Paragraph(fixed_code_escaped, code_style))
        
        doc.build(story)
        return output_path