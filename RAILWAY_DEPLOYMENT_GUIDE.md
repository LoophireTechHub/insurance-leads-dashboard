# Railway Deployment Guide - Activity Tracking API

## 🚂 Deploy to Railway (Free Tier)

### Step 1: Sign up for Railway (2 minutes)

1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub (easiest option)
4. Verify your email

---

### Step 2: Create New Project (1 minute)

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository: `LoophireTechHub/loophireteam-chrisinsuranceleads`
4. Railway will automatically detect it's a Python app

---

### Step 3: Configure Environment Variables (3 minutes)

In Railway dashboard, go to your project → Variables tab → Add these:

| Variable Name | Value | Description |
|--------------|-------|-------------|
| `GITHUB_TOKEN` | `ghp_YOUR_TOKEN_HERE` | Your GitHub Personal Access Token |
| `GITHUB_REPO` | `LoophireTechHub/loophireteam-chrisinsuranceleads` | Your repo |
| `PORT` | `5000` | Port (Railway auto-sets this, but include it) |

#### How to get GITHUB_TOKEN:

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "Railway Activity API"
4. Select scopes:
   - ✅ `repo` (all repo permissions)
5. Click "Generate token"
6. **COPY THE TOKEN** (you'll only see it once!)
7. Paste it into Railway's `GITHUB_TOKEN` variable

---

### Step 4: Deploy (Automatic!)

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run the app using `Procfile` command
3. Assign you a public URL like: `your-project.up.railway.app`

Wait 2-3 minutes for deployment to complete.

---

### Step 5: Get Your API URL

1. In Railway dashboard, click on your project
2. Go to "Settings" tab
3. Find "Domains" section
4. Copy your Railway URL (e.g., `https://activity-api-production.up.railway.app`)

---

### Step 6: Test Your API

Open your browser or use curl:

```bash
# Health check
curl https://YOUR-RAILWAY-URL.railway.app/api/health

# Should return:
{
  "status": "healthy",
  "service": "Activity Tracking API",
  "timestamp": "2025-11-20T...",
  "activities_count": 0,
  "github_enabled": true
}
```

---

### Step 7: Update Dashboard Configuration

Now you need to update the team dashboard to use your deployed API URL.

I'll do this in the next step by modifying `docs/team_leads/team_dashboard_enriched.html`.

You'll replace:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

With:
```javascript
const API_BASE_URL = 'https://YOUR-RAILWAY-URL.railway.app/api';
```

---

## 🎯 Expected Results

After deployment:
- ✅ API is accessible from anywhere (not just localhost)
- ✅ Activities sync across all team members in real-time
- ✅ Data persists to GitHub repo automatically
- ✅ Free tier handles 500+ requests/hour easily

---

## 🔒 Security Notes

**Your GitHub token is secure:**
- Stored as environment variable in Railway (not in code)
- Not visible in browser or dashboard HTML
- Only the API server uses it to commit changes

**API is public but safe:**
- Anyone can call it, but it just tracks checkbox states
- No sensitive data stored
- Rate limits prevent abuse

---

## 💰 Cost

Railway Free Tier:
- ✅ 500 hours/month of runtime (enough for always-on)
- ✅ $5/month free credit
- ✅ Shared CPU/RAM (plenty for this API)
- ✅ No credit card required initially

This API uses minimal resources, so free tier is sufficient.

---

##  📊 Monitoring

**Railway Dashboard:**
- View logs in real-time
- See request metrics
- Monitor uptime

**API Endpoints for monitoring:**
```bash
# Check health
GET https://your-api.railway.app/api/health

# Check activities count
GET https://your-api.railway.app/api/activities

# Manually sync from GitHub
POST https://your-api.railway.app/api/sync
```

---

## 🆘 Troubleshooting

**Deployment failed:**
- Check Railway logs for errors
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` points to correct file

**API returns 500 errors:**
- Check GITHUB_TOKEN is set correctly
- Verify GITHUB_REPO matches your repository
- Check Railway logs for Python errors

**Activities not syncing to GitHub:**
- Verify GitHub token has `repo` permissions
- Check GitHub repo name is correct
- Look for error messages in Railway logs

**Dashboard can't connect to API:**
- Verify Railway URL is correct in dashboard
- Check CORS is enabled (it is by default)
- Make sure Railway app is running (not paused)

---

## 🔄 Updates

To update the API after deployment:

1. Make changes to `activity_api_production.py` locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update API"
   git push origin main
   ```
3. Railway auto-detects the push and redeploys
4. Wait 1-2 minutes for new version to be live

---

## Next Steps

After Railway is deployed:
1. ✅ Copy your Railway URL
2. ⏭️ Update dashboard HTML with new API URL
3. ⏭️ Test cross-user activity sync
4. ⏭️ Deploy updated dashboard to GitHub Pages

---

**Ready to proceed?**

Once Railway is deployed and you have your URL, let me know and I'll update the dashboard to use it!
