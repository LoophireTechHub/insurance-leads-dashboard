# 🎯 Simple HTML Dashboard Deployment (No Riff Required!)

This is a **100% FREE** solution that generates a static HTML dashboard you can host anywhere.

---

## 📋 What You Get

- **FREE job scraping** with JobSpy (no Apify costs)
- **Static HTML dashboard** (`docs/index.html`) - works anywhere
- **Daily automation** via GitHub Actions
- **No expensive hosting** - use GitHub Pages, Netlify, Vercel, or any static host

---

## 🚀 Quick Start (3 Steps)

### Step 1: Set Environment Variable

```bash
export APOLLO_API_TOKEN=QbMb8hbOIHEpl_TVn1kSLg
```

Or create `.env` file:
```
APOLLO_API_TOKEN=QbMb8hbOIHEpl_TVn1kSLg
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run Pipeline

```bash
python3 insurance_leads_pipeline_final.py
```

This will:
1. Scrape Indeed for insurance jobs (FREE via JobSpy)
2. Filter out web developer jobs (ultra-strict)
3. Enrich with Apollo.io contact data
4. Score by urgency (0-100)
5. Save to CSV (`leads_output/`)
6. **Auto-generate HTML dashboard** (`docs/index.html`)

---

## 🌐 View Your Dashboard

### Option 1: Local Viewing
```bash
# Open the dashboard in your browser
open docs/index.html

# Or serve it locally
cd docs && python3 -m http.server 8000
# Then visit: http://localhost:8000
```

### Option 2: GitHub Pages (FREE Hosting)

1. **Commit the dashboard:**
   ```bash
   git add docs/
   git commit -m "Add insurance leads dashboard"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repo: Settings → Pages
   - Source: `main` branch
   - Folder: `/docs`
   - Click Save

3. **Your dashboard will be live at:**
   ```
   https://yourusername.github.io/your-repo-name/
   ```

### Option 3: Netlify (FREE Hosting)

1. Drag and drop the `docs/` folder to [Netlify Drop](https://app.netlify.com/drop)
2. Get instant live URL

### Option 4: Vercel (FREE Hosting)

```bash
cd docs
vercel --prod
```

---

## ⏰ Daily Automation (Already Set Up!)

Your GitHub Actions workflow runs **daily at 8 AM UTC** and:
- Scrapes fresh insurance jobs
- Updates the CSV
- Regenerates the dashboard
- Auto-commits to `docs/`
- Dashboard updates automatically on GitHub Pages

**No manual work required!**

---

## 📁 File Structure

```
your-project/
├── insurance_leads_pipeline_final.py  # Main pipeline
├── generate_dashboard.py              # HTML generator
├── requirements.txt                   # Dependencies
├── .env                                # Your Apollo key
├── leads_output/                      # CSV files
│   └── insurance_leads_20250125.csv
└── docs/                              # 👈 Deploy this folder!
    ├── index.html                     # Beautiful dashboard
    └── data.json                      # Leads data
```

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| JobSpy | **$0** | FREE open-source scraping |
| Apollo.io | **$0** | Free tier (1,000 credits/month) |
| GitHub Pages | **$0** | FREE static hosting |
| GitHub Actions | **$0** | 2,000 free minutes/month |
| **TOTAL** | **$0/month** | 🎉 Completely free! |

vs. Riff at ~$20-50/month

---

## 🎨 Dashboard Features

The HTML dashboard includes:

✅ **Real-time stats** - Total leads, high priority, companies, contacts
✅ **Search & filter** - By company, title, or location
✅ **Urgency scoring** - Color-coded badges (red/orange/green)
✅ **Leadership contacts** - CEO, Directors, VPs with emails
✅ **Direct job links** - Click to apply
✅ **Mobile responsive** - Works on all devices
✅ **Auto-refresh** - Updates every 5 minutes

---

## 🔧 Customization

### Change Dashboard Colors

Edit `generate_dashboard.py` lines 100-101:
```python
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Refresh Frequency

Edit line 315 in `generate_dashboard.py`:
```javascript
setInterval(loadDashboard, 300000);  // 300000 = 5 minutes
```

### Add More Job Titles

Edit `insurance_leads_pipeline_final.py` lines 42-49:
```python
SEARCH_TERMS = [
    '"Commercial Insurance Underwriter" insurance -software -developer -web',
    '"Your New Job Title" insurance -software -developer -web',
]
```

---

## 🐛 Troubleshooting

### Dashboard shows "No data available"
- Run the pipeline first: `python3 insurance_leads_pipeline_final.py`
- Check that `docs/data.json` exists

### Pipeline fails with import errors
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Apollo.io quota exceeded
- Free tier: 1,000 credits/month
- Each company lookup = 1 credit
- Upgrade to paid plan or reduce scraping frequency

### GitHub Pages not updating
- Check Actions tab for errors
- Ensure workflow has write permissions (Settings → Actions → General → Workflow permissions → Read and write)

---

## 📊 Sample Dashboard

Your dashboard will show:

**Stats Cards:**
- 20 Total Leads
- 15 High Priority (>75% urgency)
- 18 With Contacts
- 12 Unique Companies

**Lead Cards:**
- Insurance Risk Manager @ Metropolitan Management
- Urgency: 86.8% (80 days open)
- Salary: $140K-$155K
- Contacts: Mike Braham (Chief Growth Officer)
- Location: Wyomissing, PA

---

## 🎯 Next Steps

1. **Run pipeline daily** - Already automated via GitHub Actions
2. **Share dashboard URL** - Send to your team
3. **Export leads** - CSV files in `leads_output/`
4. **Customize styling** - Edit `generate_dashboard.py` HTML

---

## 💡 Pro Tips

1. **Bookmark your dashboard** - Easy access to latest leads
2. **Set up notifications** - GitHub Actions can email you when workflow completes
3. **Export to CRM** - CSV files ready to import
4. **Monitor logs** - Check `leads_pipeline.log` for details

---

## ✅ Summary

**What you have now:**
- ✅ FREE job scraping (JobSpy)
- ✅ Beautiful HTML dashboard
- ✅ Daily automation (GitHub Actions)
- ✅ FREE hosting (GitHub Pages)
- ✅ No Riff costs ($0 vs $20-50/month)

**Total setup time:** 5 minutes
**Monthly cost:** $0
**Maintenance:** Zero - fully automated

🎉 **Your dashboard is ready to deploy!**
