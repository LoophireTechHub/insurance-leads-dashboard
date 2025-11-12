#!/usr/bin/env python3
"""
Generate dashboard for enhanced multi-signal leads
"""
import json
import csv
from pathlib import Path
from datetime import datetime

def generate_enhanced_dashboard():
    output_dir = Path("leads_output")
    csv_files = sorted(output_dir.glob("enhanced_leads_*.csv"), reverse=True)

    if not csv_files:
        print("No enhanced CSV files found")
        return

    latest_csv = csv_files[0]
    print(f"Processing {latest_csv}")

    leads = []
    with open(latest_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    # Sort by composite score
    leads.sort(key=lambda x: float(x.get('Composite Score', 0)), reverse=True)

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p EST')

    # Calculate stats
    stats = {
        'total_leads': len(leads),
        'high_score': len([l for l in leads if float(l.get('Composite Score', 0)) >= 50]),
        'growing': len([l for l in leads if float(l.get('Growth Rate %', 0)) >= 10]),
        'hiring': len([l for l in leads if int(l.get('Active Jobs', 0)) > 0]),
        'with_contacts': sum(1 for l in leads if l.get('Contact 1 Email') and 'email_not_unlocked' not in l.get('Contact 1 Email', '')),
        'last_updated': current_timestamp,
        'update_date': current_date
    }

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    # Load existing history
    history_file = docs_dir / "enhanced_data_history.json"
    history = []
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []

    # Add current session to history
    new_session = {
        'date': current_date,
        'timestamp': current_timestamp,
        'stats': stats,
        'leads': leads[:100]  # Top 100
    }

    # Check if today already exists, if so replace it
    history = [h for h in history if h['date'] != current_date]
    history.insert(0, new_session)

    # Keep only last 10 sessions
    history = history[:10]

    # Save history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

    # Generate HTML dashboard
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insurance Leads Dashboard - Multi-Signal Detection</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #2d3748;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #718096;
            font-size: 1.1em;
        }
        .last-update {
            color: #667eea;
            font-weight: 600;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            color: #718096;
            margin-top: 8px;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .leads-table {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow-x: auto;
        }
        .leads-table h2 {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .filter-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .filter-section input {
            width: 100%;
            padding: 10px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1em;
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        th {
            background: #f7fafc;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #e2e8f0;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #2d3748;
            font-size: 0.9em;
        }
        tr:hover {
            background: #f7fafc;
        }
        .score-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
        }
        .score-high { background: #fed7d7; color: #c53030; }
        .score-medium { background: #feebc8; color: #c05621; }
        .score-low { background: #c6f6d5; color: #276749; }
        .company-name {
            font-weight: 600;
            color: #2d3748;
        }
        .growth-indicator {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            background: #c6f6d5;
            color: #276749;
            margin-left: 8px;
        }
        .jobs-indicator {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 600;
            background: #bee3f8;
            color: #2c5282;
            margin-left: 8px;
        }
        .contact-info {
            font-size: 0.85em;
            color: #718096;
        }
        .btn-linkedin {
            display: inline-block;
            padding: 6px 12px;
            background: #0077b5;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: 500;
            transition: background 0.3s ease;
        }
        .btn-linkedin:hover {
            background: #005885;
        }
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr 1fr; }
            table { font-size: 0.85em; }
            .header h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Insurance Leads Dashboard - Multi-Signal Detection</h1>
            <p>Apollo-powered lead generation with composite scoring</p>
            <p class="last-update">Last updated: <span id="lastUpdate">Loading...</span></p>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">High Score (50+)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">Growing</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">Actively Hiring</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">With Contacts</div>
            </div>
        </div>

        <div class="filter-section">
            <input type="text" id="searchInput" placeholder="🔍 Search by company, location, or industry..." />
        </div>

        <div class="leads-table">
            <h2>Top Insurance Leads by Composite Score</h2>
            <table id="leadsTable">
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Company</th>
                        <th>Location</th>
                        <th>Headcount</th>
                        <th>Growth</th>
                        <th>Jobs</th>
                        <th>Industry</th>
                        <th>Contact</th>
                        <th>Phone</th>
                        <th>LinkedIn</th>
                        <th>Website</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td colspan="11" style="text-align:center; padding:50px;">Loading leads data...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('enhanced_data_history.json?t=' + new Date().getTime());
                const history = await response.json();

                if (history.length === 0) return;

                const latest = history[0];
                document.getElementById('lastUpdate').textContent = latest.stats.last_updated;

                const statCards = document.querySelectorAll('.stat-value');
                statCards[0].textContent = latest.stats.total_leads;
                statCards[1].textContent = latest.stats.high_score;
                statCards[2].textContent = latest.stats.growing;
                statCards[3].textContent = latest.stats.hiring;
                statCards[4].textContent = latest.stats.with_contacts;

                const tbody = document.querySelector('#leadsTable tbody');
                tbody.innerHTML = '';

                latest.leads.forEach(lead => {
                    const score = parseFloat(lead['Composite Score'] || 0);
                    const scoreClass = score >= 50 ? 'score-high' : score >= 25 ? 'score-medium' : 'score-low';

                    const growthRate = parseFloat(lead['Growth Rate %'] || 0);
                    const activeJobs = parseInt(lead['Active Jobs'] || 0);

                    const growthBadge = growthRate >= 10 ?
                        `<span class="growth-indicator">↑ ${growthRate}%</span>` : '';

                    const jobsBadge = activeJobs > 0 ?
                        `<span class="jobs-indicator">${activeJobs} jobs</span>` : '';

                    const contact1Name = lead['Contact 1 Name'] || '';
                    const contact1Title = lead['Contact 1 Title'] || '';
                    const contact1LinkedIn = lead['Contact 1 LinkedIn'] || '';

                    const contactDisplay = contact1Name ?
                        `${contact1Name}<br><span class="contact-info">${contact1Title}</span>` :
                        '<span class="contact-info">No contact</span>';

                    const linkedInButton = contact1LinkedIn ?
                        `<a href="${contact1LinkedIn}" target="_blank" class="btn-linkedin">LinkedIn</a>` :
                        '<span class="contact-info">N/A</span>';

                    const websiteLink = lead['Website'] ?
                        `<a href="${lead['Website']}" target="_blank" style="color: #667eea; text-decoration: none;">Visit</a>` :
                        'N/A';

                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td><span class="score-badge ${scoreClass}">${score.toFixed(0)}</span></td>
                        <td class="company-name">${lead['Company Name'] || 'N/A'}${growthBadge}${jobsBadge}</td>
                        <td>${lead['Location'] || 'N/A'}</td>
                        <td>${lead['Current Headcount'] || '0'}</td>
                        <td>${growthRate > 0 ? '+' + growthRate + '%' : (growthRate < 0 ? growthRate + '%' : '--')}</td>
                        <td>${activeJobs || 0}</td>
                        <td><span class="contact-info">${lead['Industry'] || 'N/A'}</span></td>
                        <td>${contactDisplay}</td>
                        <td>${lead['Phone'] || 'N/A'}</td>
                        <td>${linkedInButton}</td>
                        <td>${websiteLink}</td>
                    `;
                });

                document.getElementById('searchInput').addEventListener('input', filterTable);

            } catch (error) {
                console.error('Error loading data:', error);
                document.querySelector('#leadsTable tbody').innerHTML =
                    '<tr><td colspan="11" style="text-align:center; color:red;">Error loading data. Please refresh.</td></tr>';
            }
        }

        function filterTable() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#leadsTable tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }

        loadDashboard();
        setInterval(loadDashboard, 300000); // Refresh every 5 minutes
    </script>
</body>
</html>"""

    with open(docs_dir / "enhanced.html", 'w') as f:
        f.write(html)

    print(f"✅ Enhanced dashboard generated in docs/enhanced.html")
    print(f"📊 Processed {len(leads)} leads")
    print(f"   - High score (50+): {stats['high_score']}")
    print(f"   - Growing companies: {stats['growing']}")
    print(f"   - Actively hiring: {stats['hiring']}")

if __name__ == "__main__":
    generate_enhanced_dashboard()
