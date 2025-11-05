#!/usr/bin/env python3
import json
import csv
from pathlib import Path
from datetime import datetime
import os

def generate_dashboard():
    output_dir = Path("leads_output")
    csv_files = sorted(output_dir.glob("insurance_leads_*.csv"), reverse=True)

    if not csv_files:
        print("No CSV files found")
        return

    latest_csv = csv_files[0]
    print(f"Processing {latest_csv}")

    leads = []
    with open(latest_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p EST')

    stats = {
        'total_leads': len(leads),
        'high_priority': len([l for l in leads if float(l.get('Urgency Score', 0)) > 75]),
        'with_contacts': sum(1 for l in leads if l.get('Leadership 1 Email')),
        'unique_companies': len(set(l.get('Company Name', '') for l in leads if l.get('Company Name'))),
        'last_updated': current_timestamp,
        'update_date': current_date
    }

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)

    # Load existing history
    history_file = docs_dir / "data_history.json"
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
        'leads': leads[:50]
    }

    # Check if today already exists, if so replace it
    history = [h for h in history if h['date'] != current_date]
    history.insert(0, new_session)

    # Keep only last 10 sessions
    history = history[:10]

    # Save history
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

    # Also save current data for backwards compatibility
    with open(docs_dir / "data.json", 'w') as f:
        json.dump({
            'stats': stats,
            'leads': leads[:50]
        }, f, indent=2)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insurance Leads Dashboard</title>
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
            max-width: 1400px;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
        .session-divider {
            margin: 40px 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            text-align: center;
        }
        .session-divider h3 {
            color: white;
            font-size: 1.3em;
            margin-bottom: 5px;
        }
        .session-divider p {
            color: rgba(255,255,255,0.9);
            font-size: 0.9em;
        }
        .session-stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        .session-stat {
            color: white;
            font-size: 0.85em;
        }
        .session-stat strong {
            font-size: 1.2em;
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
        }
        tr:hover {
            background: #f7fafc;
        }
        .score-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
        }
        .score-high { background: #fed7d7; color: #c53030; }
        .score-medium { background: #feebc8; color: #c05621; }
        .score-low { background: #c6f6d5; color: #276749; }
        .company-name {
            font-weight: 600;
            color: #2d3748;
        }
        .contact-info {
            font-size: 0.9em;
            color: #718096;
        }
        .btn {
            display: inline-block;
            padding: 8px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 500;
            transition: opacity 0.3s ease;
            margin: 2px;
        }
        .btn:hover {
            opacity: 0.9;
        }
        .btn-linkedin {
            background: #0077b5;
        }
        .btn-linkedin:hover {
            background: #005885;
            opacity: 1;
        }
        .loading {
            text-align: center;
            padding: 50px;
            color: white;
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
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: 1fr; }
            table { font-size: 0.9em; }
            .header h1 { font-size: 1.8em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Insurance Leads Dashboard</h1>
            <p>Daily updated pipeline of commercial insurance opportunities</p>
            <p class="last-update">Last updated: <span id="lastUpdate">Loading...</span></p>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">Companies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">--</div>
                <div class="stat-label">With Contacts</div>
            </div>
        </div>

        <div class="filter-section">
            <input type="text" id="searchInput" placeholder="🔍 Search by company, title, or location..." />
        </div>

        <div class="leads-table">
            <h2>Top Insurance Leads</h2>
            <table id="leadsTable">
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Company</th>
                        <th>Job Title</th>
                        <th>Location</th>
                        <th>Days Open</th>
                        <th>Contact</th>
                        <th>LinkedIn</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td colspan="8" class="loading">Loading leads data...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadDashboard() {
            try {
                const response = await fetch('data_history.json?t=' + new Date().getTime());
                const history = await response.json();

                if (history.length === 0) return;

                // Update header with latest stats
                const latest = history[0];
                document.getElementById('lastUpdate').textContent = latest.stats.last_updated;

                const statCards = document.querySelectorAll('.stat-value');
                statCards[0].textContent = latest.stats.total_leads;
                statCards[1].textContent = latest.stats.high_priority;
                statCards[2].textContent = latest.stats.unique_companies;
                statCards[3].textContent = latest.stats.with_contacts;

                const tbody = document.querySelector('#leadsTable tbody');
                tbody.innerHTML = '';

                // Display all sessions with dividers
                history.forEach((session, index) => {
                    // Add session divider
                    if (index > 0) {
                        const dividerRow = tbody.insertRow();
                        dividerRow.innerHTML = `
                            <td colspan="8" style="padding: 0;">
                                <div class="session-divider">
                                    <h3>📅 ${session.timestamp}</h3>
                                    <div class="session-stats">
                                        <div class="session-stat"><strong>${session.stats.total_leads}</strong> Leads</div>
                                        <div class="session-stat"><strong>${session.stats.high_priority}</strong> High Priority</div>
                                        <div class="session-stat"><strong>${session.stats.with_contacts}</strong> With Contacts</div>
                                    </div>
                                </div>
                            </td>
                        `;
                    }

                    // Add leads for this session
                    session.leads.forEach(lead => {
                        const score = parseFloat(lead['Urgency Score'] || 0);
                        const scoreClass = score > 75 ? 'score-high' : score > 50 ? 'score-medium' : 'score-low';

                        // Show leadership contact or company phone
                        const hasLeadership = lead['Leadership 1 Name'] && lead['Leadership 1 Name'] !== '';
                        const hasEmail = lead['Leadership 1 Email'] && !lead['Leadership 1 Email'].includes('email_not_unlocked');
                        const hasLinkedIn = lead['Leadership 1 LinkedIn'] && lead['Leadership 1 LinkedIn'] !== '';

                        const contact = hasLeadership ?
                            `${lead['Leadership 1 Name']}<br><span class="contact-info">${lead['Leadership 1 Title'] || 'Leadership'}</span>` +
                            (hasEmail ? `<br><span class="contact-info">✉️ ${lead['Leadership 1 Email']}</span>` : '') :
                            (lead['Phone Number'] ?
                                `<span class="contact-info">📞 ${lead['Phone Number']}</span>` :
                                '<span class="contact-info">Apply via job posting</span>');

                        const linkedInButton = hasLinkedIn ?
                            `<a href="${lead['Leadership 1 LinkedIn']}" target="_blank" class="btn btn-linkedin">LinkedIn</a>` :
                            '<span style="color: #cbd5e0; font-size: 0.85em;">N/A</span>';

                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td><span class="score-badge ${scoreClass}">${score.toFixed(1)}</span></td>
                            <td class="company-name">${lead['Company Name'] || 'N/A'}</td>
                            <td>${lead['Job Title'] || 'N/A'}</td>
                            <td>${lead['Location'] || 'N/A'}</td>
                            <td>${lead['Days Open'] || 'N/A'}</td>
                            <td>${contact}</td>
                            <td>${linkedInButton}</td>
                            <td>
                                ${lead['Job URL'] ? `<a href="${lead['Job URL']}" target="_blank" class="btn">View Job</a>` : 'N/A'}
                            </td>
                        `;
                    });
                });

                document.getElementById('searchInput').addEventListener('input', filterTable);

            } catch (error) {
                console.error('Error loading data:', error);
                document.querySelector('#leadsTable tbody').innerHTML =
                    '<tr><td colspan="8" style="text-align:center; color:red;">Error loading data. Please refresh.</td></tr>';
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
        setInterval(loadDashboard, 300000);
    </script>
</body>
</html>"""
    
    with open(docs_dir / "index.html", 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated in docs/index.html")
    print(f"📊 Processed {len(leads)} leads")

if __name__ == "__main__":
    generate_dashboard()
