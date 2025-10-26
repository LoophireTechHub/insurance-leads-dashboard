# ✅ GitHub Pages Deployment Checklist

## 📋 Complete These Steps

### ✅ Step 1: Enable GitHub Pages
- [ ] Go to: https://github.com/LoophireTechHub/insurance-leads-dashboard/settings/pages
- [ ] Under "Build and deployment" → Source: Select **"GitHub Actions"**
- [ ] Click **Save**

### ✅ Step 2: Grant Workflow Permissions
- [ ] Go to: https://github.com/LoophireTechHub/insurance-leads-dashboard/settings/actions
- [ ] Scroll to "Workflow permissions"
- [ ] Select **"Read and write permissions"**
- [ ] Check **"Allow GitHub Actions to create and approve pull requests"**
- [ ] Click **Save**

### ✅ Step 3: Verify Deployment
- [ ] Go to: https://github.com/LoophireTechHub/insurance-leads-dashboard/actions
- [ ] Check latest "Deploy to GitHub Pages" workflow
- [ ] Should show: ✅ Green checkmark (all jobs passed)

### ✅ Step 4: View Your Live Dashboard
- [ ] Visit: **https://loophiretechhub.github.io/insurance-leads-dashboard/**
- [ ] Should see: Insurance Leads Dashboard with stats and leads
- [ ] Test search: Try filtering by company name

---

## 🔍 Troubleshooting

### Issue: Deploy job is cancelled

**Fix:**
1. Complete Step 2 above (Grant Workflow Permissions)
2. Go to Actions → Click failed workflow → Click "Re-run all jobs"

### Issue: 404 Page Not Found

**Fix:**
1. Ensure Step 1 is complete (GitHub Pages enabled with "GitHub Actions" source)
2. Wait 2-3 minutes for DNS propagation
3. Check Actions tab for green checkmark

### Issue: Dashboard shows old data

**Fix:**
```bash
python3 insurance_leads_pipeline_final.py
git add docs/
git commit -m "Update dashboard data"
git push origin main
```

---

## 🎯 Success Criteria

Your deployment is successful when:

- ✅ GitHub Pages shows: "Your site is live at https://loophiretechhub.github.io/insurance-leads-dashboard/"
- ✅ Actions tab shows: Green checkmark for "Deploy to GitHub Pages"
- ✅ Dashboard URL loads: Beautiful dashboard with 20 insurance leads
- ✅ Search works: Can filter leads by company/title/location
- ✅ Stats display: Shows total leads, high priority, contacts, companies

---

## 📊 What Happens Next

Once deployed:

1. **Daily Updates (8 AM UTC)**
   - GitHub Actions runs pipeline automatically
   - Scrapes fresh insurance jobs from Indeed
   - Updates `docs/data.json` with new leads
   - Dashboard refreshes with latest data

2. **Automatic Deployment**
   - Every push to `main` branch
   - Any changes to `docs/` folder
   - Manual workflow trigger (if needed)

3. **Zero Maintenance**
   - Everything runs automatically
   - No manual intervention required
   - Logs available in Actions tab

---

## 🔗 Quick Links

| Task | URL |
|------|-----|
| **Enable Pages** | https://github.com/LoophireTechHub/insurance-leads-dashboard/settings/pages |
| **Grant Permissions** | https://github.com/LoophireTechHub/insurance-leads-dashboard/settings/actions |
| **View Actions** | https://github.com/LoophireTechHub/insurance-leads-dashboard/actions |
| **Live Dashboard** | https://loophiretechhub.github.io/insurance-leads-dashboard/ |

---

## 🆘 Still Having Issues?

1. Check the workflow logs:
   - Go to Actions → Click failed workflow → Click "deploy" job
   - Look for error messages in red

2. Common errors and fixes:
   - **"pages build and deployment: Error 403"** → Complete Step 2 (permissions)
   - **"deploy job cancelled"** → Complete Step 2 (permissions)
   - **"404 Not Found"** → Complete Step 1 (enable Pages)

3. Manual deployment:
   ```bash
   # Force a new deployment
   git commit --allow-empty -m "Trigger deployment"
   git push origin main
   ```

---

## 🎉 You're Almost There!

**Current Status:**
- ✅ Code pushed to GitHub
- ✅ Dashboard files ready (`docs/`)
- ✅ Workflow updated (build + deploy jobs)
- ⏳ Waiting for: Steps 1 & 2 above

**Time Required:** 2 minutes
**Result:** Free, auto-updating insurance leads dashboard!

Start here: https://github.com/LoophireTechHub/insurance-leads-dashboard/settings/pages
