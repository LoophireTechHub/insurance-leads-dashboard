# Cross-User Activity Tracking Setup

This guide explains how to set up the Activity Tracking API server to enable **cross-user activity syncing** on the Team Dashboard.

## Problem Solved

Previously, activity tracking (Called, LinkedIn, Emailed checkboxes) was saved only in each user's browser localStorage. This meant:
- ❌ Sales team couldn't see Marketing's activities
- ❌ Marketing couldn't see Sales' activities
- ❌ Activities were lost when switching browsers

Now with the Activity API:
- ✅ All team members see the same activities in real-time
- ✅ Activities persist across browsers and devices
- ✅ Changes sync automatically within 15 seconds
- ✅ Works for Sales, Marketing, and all other departments

## How It Works

```
User Browser 1 (Sales)          User Browser 2 (Marketing)
      |                                  |
      |  Checks "Called" box             |  Opens dashboard
      |  ↓                                |  ↓
      |  Saves to API Server ←-----------+  Loads from API Server
      |  ↓                                |  ↓
      |  Syncs to GitHub                 |  Sees "Called" is checked!
```

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/loophire/insurance-leads-dashboard
pip3 install flask flask-cors
```

### 2. Start the API Server

```bash
./start_activity_api.sh
```

Or manually:
```bash
python3 activity_api.py
```

You should see:
```
============================================================
🚀 Activity Tracking API Server
============================================================
Database: /path/to/docs/team_leads/activities_database.json
Endpoints:
  GET    /api/activities          - Get all activities
  GET    /api/activities/<job_id> - Get activity for job
  POST   /api/activities/<job_id> - Update activity for job
  DELETE /api/activities/<job_id> - Delete activity for job
  GET    /api/health              - Health check
============================================================

⚡ Server running on http://localhost:5000
Press Ctrl+C to stop
```

### 3. Open the Dashboard

Open the team dashboard in your browser:
```bash
open docs/team_leads/team_dashboard_enriched.html
```

Or navigate to: `http://localhost:8000/docs/team_leads/team_dashboard_enriched.html`

### 4. Test Cross-User Sync

1. **Open in Browser 1** (e.g., Chrome):
   - Check "Called" on a job
   - See green "✓ Synced to server" message

2. **Open in Browser 2** (e.g., Safari or Incognito):
   - Wait 15 seconds OR refresh the page
   - See that "Called" is already checked!

3. **Check in Browser 2**:
   - Check "Emailed" on the same job
   - Switch to Browser 1
   - Wait 15 seconds OR refresh
   - Both "Called" and "Emailed" are checked!

## Features

### Real-Time Sync
- Activities update every 15 seconds automatically
- Manual refresh also pulls latest activities
- Visual sync indicator in top-right corner

### Fallback Mode
- If API server is offline, activities save to localStorage
- When API comes back online, activities sync automatically
- Yellow "⚠ API offline - saved locally" warning shown

### Auto-Git Sync
- All activity changes automatically commit to GitHub
- Uses `auto_sync_activities.sh` in background
- Marketing can see Sales activities via GitHub Pages

## API Endpoints

### Get All Activities
```bash
curl http://localhost:5000/api/activities
```

Response:
```json
{
  "success": true,
  "last_updated": "2025-11-20T14:25:33.898679Z",
  "activities": {
    "https://job-url.com": {
      "called": true,
      "linkedin": true,
      "emailed": false
    }
  }
}
```

### Update Activity for a Job
```bash
curl -X POST http://localhost:5000/api/activities/https://job-url.com \
  -H "Content-Type: application/json" \
  -d '{"activities": {"called": true, "linkedin": true}}'
```

### Delete Activity for a Job
```bash
curl -X DELETE http://localhost:5000/api/activities/https://job-url.com
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

## Production Deployment

### Option 1: Run on Server (Recommended)

Deploy the API server on a VPS or cloud instance:

```bash
# Install gunicorn for production
pip3 install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 activity_api:app
```

Update `team_dashboard_enriched.html` line 317:
```javascript
const API_BASE_URL = 'https://your-domain.com/api';
```

### Option 2: Serverless Function

Deploy as AWS Lambda, Google Cloud Function, or Vercel Function:

1. Export the Flask app
2. Use a serverless adapter (e.g., `serverless-wsgi`)
3. Update API_BASE_URL to your function URL

### Option 3: GitHub Pages + Webhook

For GitHub Pages hosting:

1. Keep API server running on a machine
2. Set up ngrok tunnel: `ngrok http 5000`
3. Update API_BASE_URL to ngrok URL
4. Or use GitHub Actions to sync via commits

## Troubleshooting

### "API offline" message
- Check if API server is running: `curl http://localhost:5000/api/health`
- Check firewall isn't blocking port 5000
- Check browser console for CORS errors

### Activities not syncing
- Check browser console for errors
- Verify API_BASE_URL in `team_dashboard_enriched.html:317`
- Test API endpoints manually with curl
- Check `activities_database.json` has write permissions

### Sync is slow
- Reduce polling interval in `team_dashboard_enriched.html:527` (default 15 seconds)
- Check network latency to API server

## File Structure

```
insurance-leads-dashboard/
├── activity_api.py                          # Flask API server
├── start_activity_api.sh                     # Startup script
├── auto_sync_activities.sh                   # Auto-commit to GitHub
├── update_team_activities.py                 # Manual activity updater
├── docs/team_leads/
│   ├── team_dashboard_enriched.html         # Dashboard with sync
│   └── activities_database.json             # Shared activities DB
└── requirements.txt                          # Python dependencies
```

## Support

If you encounter issues:
1. Check the API logs: `tail -f activity_api.log`
2. Check browser console for errors (F12)
3. Test API endpoints with curl
4. Verify `activities_database.json` exists and is writable

## Next Steps

- [ ] Deploy API to production server
- [ ] Add authentication for API endpoints
- [ ] Add activity history/audit log
- [ ] Add activity filtering (by user, date, etc.)
- [ ] Add activity export to CSV
