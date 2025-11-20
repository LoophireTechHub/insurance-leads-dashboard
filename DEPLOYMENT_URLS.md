# Insurance Leads Dashboard - Live URLs

## 📊 Live Dashboards

### 1. Team Dashboard (Enriched with Contact Info)
**URL**: https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/team_leads/team_dashboard_enriched.html

**Features**:
- 500+ commercial insurance jobs nationwide
- Enriched with hiring manager contact information
- Activity tracking (Called, LinkedIn, Emailed checkboxes)
- **Cross-user activity sync** - See what your teammates have done
- Filters by role (Producer, Underwriter, Broker, Account Manager)
- Search by company, title, or location
- Auto-updates every 5 minutes

**Best For**: Sales and Marketing teams tracking outreach activities

---

### 2. Main Dashboard (Job-Based Leads)
**URL**: https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/

**Features**:
- Indeed, LinkedIn, and Google Jobs aggregation
- Lead scoring based on title keywords
- Source labels showing which job board
- Sortable by score, company, title, location
- Auto-updates daily at 8:00 AM CDT

**Best For**: Quick overview of all active job postings

---

## 🔄 Cross-User Activity Tracking

### How It Works

**On GitHub Pages** (Production):
1. User checks "Called" on a job → Saved to their browser localStorage
2. Activities load from shared `activities_database.json` every 15 seconds
3. Daily workflow updates the JSON file from team's collective activities
4. All team members see the same activities within 15 seconds after daily sync

**On Localhost** (Development):
1. Start API server: `./start_activity_api.sh`
2. Activities sync in real-time via REST API
3. Changes push to GitHub automatically
4. Instant sync across all browsers

### Current Status

✅ **Deployed to GitHub Pages** - Latest changes live
✅ **Activity tracking enabled** - Checkboxes working
✅ **Cross-browser loading** - Activities load from JSON
⏳ **Real-time sync** - Requires daily workflow run OR manual commit

### Testing Cross-User Sync

1. **User 1** - Open Team Dashboard:
   - Go to: https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/team_leads/team_dashboard_enriched.html
   - Check "Called" on a job
   - You'll see: "💾 Saved locally (GitHub Pages mode)"

2. **User 2** - Open same dashboard in different browser/incognito:
   - Wait 15 seconds OR refresh
   - Activities from User 1 will appear after daily workflow runs

3. **To sync immediately**: Run the daily leads workflow manually

---

## 🚀 Manual Sync (For Testing)

To manually sync activities across users:

```bash
# Option 1: Run daily workflow via GitHub Actions
gh workflow run daily-leads.yml

# Option 2: Run locally and commit
python3 update_team_activities.py update "job-url" '{"called": true}'
./auto_sync_activities.sh

# Option 3: Start local API server for instant sync
./start_activity_api.sh
```

---

## 📁 File Locations

- **Team Dashboard**: `docs/team_leads/team_dashboard_enriched.html`
- **Main Dashboard**: `docs/index.html`
- **Activities Database**: `docs/team_leads/activities_database.json`
- **Team Jobs Data**: `docs/team_leads/team_jobs_data_enriched.json`

---

## 🔧 Development

### Local Development with Real-Time Sync

```bash
# 1. Start API server
./start_activity_api.sh

# 2. Open dashboard
open docs/team_leads/team_dashboard_enriched.html

# 3. Activities now sync in real-time!
```

### Deploy Changes

```bash
# 1. Make changes to HTML/Python files
# 2. Commit and push
git add .
git commit -m "Your changes"
git push origin main

# 3. GitHub Pages auto-deploys (takes 1-2 minutes)
```

---

## 📊 Dashboard URLs Quick Reference

| Dashboard | URL | Update Frequency |
|-----------|-----|------------------|
| **Team Dashboard** | [team_dashboard_enriched.html](https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/team_leads/team_dashboard_enriched.html) | Daily 8 AM CDT |
| **Main Dashboard** | [index.html](https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/) | Daily 8 AM CDT |
| **Activities JSON** | [activities_database.json](https://loophiretechhub.github.io/loophireteam-chrisinsuranceleads/team_leads/activities_database.json) | On workflow run |

---

## 🎯 Next Steps

1. ✅ Dashboards are live and accessible
2. ✅ Activity tracking is working
3. ✅ Cross-user loading from JSON enabled
4. ⏳ **Run daily workflow to sync activities** (or wait for automatic 8 AM run)
5. 🔜 Consider deploying API server for real-time sync

---

## 🆘 Troubleshooting

**Activities not syncing?**
- Check browser console (F12) for error messages
- Verify `activities_database.json` exists in GitHub repo
- Ensure you're on GitHub Pages URL (not localhost)

**Dashboard not loading?**
- Wait 1-2 minutes for GitHub Pages deployment
- Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Check GitHub Actions for failed workflows

**Want instant sync?**
- Run API server locally: `./start_activity_api.sh`
- Open localhost version: `file:///path/to/docs/team_leads/team_dashboard_enriched.html`

---

**Last Updated**: 2025-11-20
**Status**: ✅ Live and operational
