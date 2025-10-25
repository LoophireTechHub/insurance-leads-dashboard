# Riff Deployment - Complete Setup Instructions

## 🚀 Quick Deploy to Riff

### Step 1: Upload Project Structure

Upload these files to your Riff project in this exact structure:

```
your-riff-project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── scraper_worker.py
├── docs/
│   └── data.json (will be auto-generated)
├── leads_output/
│   └── .gitkeep
├── insurance_leads_pipeline_final.py
├── generate_dashboard.py
├── requirements.txt
├── .env
└── riff-component.jsx (for frontend)
```

### Step 2: Environment Variables

Create `.env` file in Riff with:

```
APOLLO_API_TOKEN=your_apollo_token_here
```

Note: We removed the APIFY requirement since we're using free JobSpy now!

### Step 3: Install Dependencies

In Riff terminal:
```bash
pip install -r requirements.txt
```

### Step 4: Run Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Run Pipeline (First Time)

```bash
python insurance_leads_pipeline_final.py
```

This will populate `docs/data.json` with insurance leads.

### Step 6: Deploy Frontend Component

Use the `riff-component.jsx` in your Riff React app.

---

## 📁 All Files Included

I've created a complete `riff-deployment/` folder with all files ready to upload:

1. **app/main.py** - FastAPI backend
2. **app/scraper_worker.py** - Background worker
3. **app/__init__.py** - Python package marker
4. **insurance_leads_pipeline_final.py** - JobSpy scraper
5. **generate_dashboard.py** - HTML dashboard generator
6. **requirements.txt** - All dependencies
7. **riff-component.jsx** - React dashboard component
8. **.env.example** - Environment variables template

---

## 🔧 Configuration

### Update API URL in Frontend

In `riff-component.jsx`, line 12:
```javascript
const API_BASE_URL = 'https://your-riff-domain.com';
```

---

## ✅ Verify Installation

1. Check health: `curl http://localhost:8000/api/health`
2. Check leads: `curl http://localhost:8000/api/leads`
3. View dashboard: Open `http://localhost:8000` in browser

---

## 🆘 Troubleshooting

**Port already in use?**
```bash
lsof -ti:8000 | xargs kill -9
```

**Dependencies missing?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**No data showing?**
```bash
python insurance_leads_pipeline_final.py
```
