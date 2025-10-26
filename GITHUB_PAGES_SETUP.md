# 🚀 GitHub Pages Deployment Instructions

Your insurance leads dashboard is ready to deploy to GitHub Pages for **FREE**!

---

## 📋 One-Time Setup (2 Minutes)

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub:
   ```
   https://github.com/LoophireTechHub/insurance-leads-dashboard
   ```

2. Click **Settings** (top right)

3. In the left sidebar, click **Pages**

4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"

5. Click **Save**

That's it! Your dashboard will be live at:
```
https://loophiretechhub.github.io/insurance-leads-dashboard/
```

---

## ✅ What Happens Next

### Automatic Deployment

Every time the dashboard updates:
1. GitHub Actions runs the pipeline (daily at 8 AM UTC)
2. Pipeline generates fresh `docs/index.html` and `docs/data.json`
3. Changes are auto-committed to `main` branch
4. GitHub Pages automatically deploys the updated dashboard
5. Your live site updates within 1-2 minutes

**Zero manual work required!**

---

## 🔗 Your Dashboard URL

Once enabled, your dashboard will be available at:

```
https://loophiretechhub.github.io/insurance-leads-dashboard/
```

**Bookmark this URL** and share it with your team!

---

## 📊 Current Dashboard Status

✅ Dashboard generated: `docs/index.html`
✅ Data file created: `docs/data.json`
✅ GitHub Actions workflow: Running daily
✅ Auto-commit enabled: Updates pushed automatically
✅ Ready to deploy: Just enable Pages in Settings!

---

## 🎯 Quick Verification

After enabling Pages:

1. **Check deployment status:**
   - Go to repo → Actions tab
   - Look for "pages build and deployment" workflow
   - Should show green checkmark ✅

2. **Visit your dashboard:**
   - Open: `https://loophiretechhub.github.io/insurance-leads-dashboard/`
   - Should see: Insurance Leads Dashboard with stats and leads

3. **Test auto-updates:**
   - Wait for next daily run (8 AM UTC), or
   - Manually trigger: Actions → "Daily Insurance Leads Pipeline" → Run workflow
   - Dashboard should update within 2 minutes

---

## 🛠️ Troubleshooting

### "404 - Page not found"

**Solution:**
- Go to Settings → Pages
- Ensure Source is set to "GitHub Actions"
- Wait 1-2 minutes for first deployment

### Dashboard shows old data

**Solution:**
```bash
# Manually run pipeline to update
python3 insurance_leads_pipeline_final.py
git add docs/
git commit -m "Update dashboard data"
git push origin main
```

### Deployment failed

**Solution:**
- Go to Settings → Actions → General
- Scroll to "Workflow permissions"
- Select "Read and write permissions"
- Click Save

---

## 🎨 Customization

### Update Dashboard Title

Edit `generate_dashboard.py` line 207:
```python
<h1>🎯 Your Custom Title</h1>
```

### Change Color Scheme

Edit `generate_dashboard.py` lines 53-55:
```python
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Add Custom Domain (Optional)

1. Buy a domain (e.g., `insuranceleads.com`)
2. Go to Settings → Pages → Custom domain
3. Enter your domain
4. Add CNAME record in your DNS provider

---

## 📈 Analytics (Optional)

### Add Google Analytics

Edit `generate_dashboard.py`, add before `</head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

---

## 🔐 Security

### Make Dashboard Private (Optional)

GitHub Pages is public by default. To make it private:

**Option 1: GitHub Pro**
- Upgrade to GitHub Pro ($4/month)
- Settings → Pages → Visibility → Private

**Option 2: Password Protection**
- Add Cloudflare in front (free)
- Enable Cloudflare Access for password protection

**Option 3: Keep Public**
- Dashboard doesn't expose sensitive data
- Leadership emails show as "email_not_unlocked@domain.com" (Apollo free tier)
- Job postings are already public on Indeed

---

## ✅ Summary

**What you have:**
- ✅ Static HTML dashboard in `docs/`
- ✅ Auto-updated daily via GitHub Actions
- ✅ Ready to deploy to GitHub Pages
- ✅ FREE hosting (no costs)
- ✅ Professional URL: `loophiretechhub.github.io/insurance-leads-dashboard`

**Next step:**
1. Go to Settings → Pages
2. Set Source to "GitHub Actions"
3. Visit your live dashboard!

**Time to deploy:** 30 seconds
**Monthly cost:** $0
**Maintenance:** Zero - fully automated

---

## 🎉 You're All Set!

Your insurance leads dashboard will be live at:
```
https://loophiretechhub.github.io/insurance-leads-dashboard/
```

Bookmark it, share it, and enjoy automated daily insurance lead updates! 🚀
