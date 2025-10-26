# 🚀 Running Pipeline Locally

## ⚠️ Python Version Requirement

**JobSpy requires Python 3.10 or higher**

Your Mac has Python 3.9.6, which doesn't support JobSpy.

---

## ✅ **Option 1: Trigger GitHub Actions** (Recommended - Easiest!)

The pipeline runs perfectly in GitHub Actions (Python 3.10). Trigger it manually:

### **Step 1: Go to Actions**
👉 https://github.com/LoophireTechHub/insurance-leads-dashboard/actions/workflows/daily-leads.yml

### **Step 2: Click "Run workflow"**
- Click the **"Run workflow"** button (right side)
- Select branch: **main**
- Click green **"Run workflow"** button

### **Step 3: Watch It Run**
- Pipeline runs for ~3-5 minutes
- Scrapes Indeed jobs
- Enriches with improved Apollo matching
- Generates dashboard with unique contacts
- Auto-commits to `main`

### **Step 4: View Results**
Dashboard updates automatically at:
👉 https://loophiretechhub.github.io/insurance-leads-dashboard/

---

## ✅ **Option 2: Install Python 3.10+ on Mac**

### **Using Homebrew:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10
brew install python@3.10

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run pipeline
export APOLLO_API_TOKEN=QbMb8hbOIHEpl_TVn1kSLg
python insurance_leads_pipeline_final.py
```

---

## ✅ **Option 3: Use Docker** (Advanced)

```bash
# Build container
docker build -t insurance-leads .

# Run pipeline
docker run -e APOLLO_API_TOKEN=QbMb8hbOIHEpl_TVn1kSLg insurance-leads
```

---

## 🎯 **Recommended: Use GitHub Actions**

**Why GitHub Actions is better:**
- ✅ Already configured and working
- ✅ Python 3.10 pre-installed
- ✅ All dependencies ready
- ✅ Runs in cloud (no local setup needed)
- ✅ Auto-commits results
- ✅ Deploys to GitHub Pages automatically
- ✅ FREE (2,000 minutes/month)
- ✅ Scheduled daily runs (8 AM UTC)

**Just click "Run workflow" and you're done!** 🚀

---

## 📊 **Expected Timeline:**

| Method | Setup Time | Run Time | Total |
|--------|-----------|----------|-------|
| **GitHub Actions** | **0 min** | **3-5 min** | **3-5 min** ⭐ |
| Install Python 3.10 | 10-15 min | 3-5 min | 15-20 min |
| Docker | 5-10 min | 3-5 min | 10-15 min |

---

## 🔗 **Quick Link to Trigger:**

👉 https://github.com/LoophireTechHub/insurance-leads-dashboard/actions/workflows/daily-leads.yml

Click **"Run workflow"** → Select **main** → Click **"Run workflow"** ✅

Then watch your dashboard update with unique contacts in 5 minutes! 🎉
