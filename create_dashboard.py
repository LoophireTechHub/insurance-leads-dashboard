#!/usr/bin/env python3
"""
Creates an HTML dashboard that auto-updates with latest leads data
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def create_html_dashboard():
    """Generate HTML dashboard from latest CSV"""
    
    # Find the most recent CSV
    output_dir = Path("leads_output")
    csv_files = sorted(output_dir.glob("insurance_leads_*.csv"), reverse=True)
    
    if not csv_files:
        return "No data yet"
    
    latest_csv = csv_files[0]
    
    # Read CSV data
    leads = []
    with open(latest_csv, 'r') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Insurance Leads Dashboard</title>
        <meta http-equiv="refresh" content="3600">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 10px; 
                         box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            table {{ width: 100%; background: white; border-radius: 10px; overflow: hidden; 
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            tr:hover {{ background: #f8f9ff; }}
            .urgent {{ background: #fff3cd; }}
            .high-score {{ color: #d73502; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Insurance Leads Dashboard</h1>
            <p>Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Auto-refreshes every hour</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(leads)}</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len([l for l in leads if float(l.get('Urgency Score', 0)) > 75])}</div>
                <div class="stat-label">High Priority (75+ score)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(set(l.get('Company Name', '') for l in leads if l.get('Company Name')))}</div>
                <div class="stat-label">Unique Companies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for l in leads if l.get('Leadership 1 Email'))}</div>
                <div class="stat-label">With Contacts</div>
            </div>
        </div>
        
        <h2>Top Insurance Leads</h2>
        <table>
            <thead>
                <tr>
                    <th>Score</th>
                    <th>Job Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Days Open</th>
                    <th>Website</th>
                    <th>Primary Contact</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for lead in leads[:20]:  # Top 20
        urgency = float(lead.get('Urgency Score', 0))
        urgency_class = 'high-score' if urgency > 75 else ''
        row_class = 'urgent' if urgency > 80 else ''
        
        contact = ""
        if lead.get('Leadership 1 Name'):
            contact = f"{lead.get('Leadership 1 Name')} ({lead.get('Leadership 1 Title', '')})"
        
        website = lead.get('Company Website', '')
        website_link = f'<a href="{website}" target="_blank">View</a>' if website else 'N/A'
        
        job_url = lead.get('Job URL', '#')
        
        html += f"""
                <tr class="{row_class}">
                    <td class="{urgency_class}">{lead.get('Urgency Score', '0')}</td>
                    <td>{lead.get('Job Title', 'N/A')}</td>
                    <td><strong>{lead.get('Company Name', 'N/A')}</strong></td>
                    <td>{lead.get('Location', 'N/A')}</td>
                    <td>{lead.get('Days Open', 'N/A')}</td>
                    <td>{website_link}</td>
                    <td>{contact}</td>
                    <td><a href="{job_url}" target="_blank">View Job</a></td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
        
        <script>
            // Auto-refresh every hour
            setTimeout(() => location.reload(), 3600000);
        </script>
    </body>
    </html>
    """
    
    # Save dashboard
    with open('leads_dashboard.html', 'w') as f:
        f.write(html)
    
    return 'leads_dashboard.html'

# Run after pipeline completes
if __name__ == "__main__":
    dashboard_file = create_html_dashboard()
    print(f"Dashboard created: {dashboard_file}")
    print(f"Open in browser: file://{Path(dashboard_file).absolute()}")
