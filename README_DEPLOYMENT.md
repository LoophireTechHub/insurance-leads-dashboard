# Insurance Leads Dashboard - Riff Deployment Guide

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone or upload to Riff
cd insurance-leads-dashboard

# Deploy everything
python deploy.py deploy
```

### 2. Configure Environment
Update `.env` with your API credentials:
```env
APIFY_API_TOKEN=your_apify_token_here
APOLLO_API_TOKEN=your_apollo_token_here
```

### 3. Start the Dashboard
```bash
# Start the web server
python deploy.py start
```

Visit: **http://localhost:8000** (or your Riff domain)

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `python deploy.py deploy` | Full deployment setup |
| `python deploy.py start` | Start the web server |
| `python deploy.py worker` | Start background scraper worker |
| `python deploy.py pipeline` | Run pipeline manually |
| `python deploy.py setup` | Setup environment only |
| `python deploy.py migrate` | Run database migrations |

---

## 🏗️ Architecture

### Components

**1. FastAPI Application** (`app/main.py`)
- Serves the dashboard at `/`
- REST API endpoints at `/api/*`
- Health checks and monitoring

**2. Background Worker** (`app/scraper_worker.py`)
- Runs pipeline daily at 14:00 UTC
- Automatic lead collection and enrichment
- Dashboard regeneration

**3. Pipeline Scripts**
- `insurance_leads_pipeline_final.py` - Main scraping logic
- `generate_dashboard.py` - Dashboard HTML generator

---

## 🔌 API Endpoints

### Dashboard
- **GET** `/` - Main dashboard HTML
- **GET** `/api/health` - Health check
- **GET** `/api/stats` - Dashboard statistics
- **GET** `/api/leads` - All leads data
- **GET** `/api/leads/{index}` - Specific lead
- **GET** `/api/data.json` - Raw JSON data
- **POST** `/api/pipeline/trigger` - Trigger pipeline manually

### Example API Usage
```bash
# Get stats
curl http://localhost:8000/api/stats

# Get all leads
curl http://localhost:8000/api/leads

# Trigger pipeline
curl -X POST http://localhost:8000/api/pipeline/trigger
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```env
# Required
APIFY_API_TOKEN=<your_token>
APOLLO_API_TOKEN=<your_token>

# Optional
PORT=8000
HOST=0.0.0.0
DEBUG=false
PIPELINE_SCHEDULE=0 14 * * *
```

### Pipeline Settings
Edit `insurance_leads_pipeline_final.py`:
- **Search terms**: Lines 37-44
- **Max results per search**: Line 218 (`max_items=50`)
- **Insurance keywords**: Lines 207-211

---

## 🔄 Daily Automation

### Option 1: Background Worker
```bash
# Runs pipeline daily at 14:00 UTC
python deploy.py worker
```

### Option 2: Cron Job
```bash
# Add to crontab
0 14 * * * cd /path/to/dashboard && python3 insurance_leads_pipeline_final.py && python3 generate_dashboard.py
```

### Option 3: GitHub Actions
Already configured in `.github/workflows/daily-leads.yml`

---

## 📊 Data Flow

```
Indeed Jobs (Apify)
    ↓
DataBro Scraper
    ↓
Insurance Keyword Filter ← Removes web dev jobs
    ↓
Apollo.io Enrichment ← Adds contacts
    ↓
Urgency Scoring ← Based on days open
    ↓
Top 20 Leads
    ↓
Dashboard (docs/index.html)
    ↓
FastAPI Server → Browser
```

---

## 🐛 Troubleshooting

### No data showing
```bash
# Run pipeline manually
python deploy.py pipeline

# Check logs
tail -f leads_pipeline.log
```

### API not responding
```bash
# Check if server is running
curl http://localhost:8000/api/health

# Restart server
python deploy.py start
```

### Worker not running
```bash
# Check worker logs
tail -f scraper_worker.log

# Manually trigger
python deploy.py pipeline
```

---

## 📁 Project Structure

```
insurance-leads-dashboard/
├── app/
│   ├── main.py              # FastAPI application
│   └── scraper_worker.py    # Background worker
├── docs/
│   ├── index.html           # Generated dashboard
│   └── data.json            # Leads data
├── leads_output/            # CSV exports
├── insurance_leads_pipeline_final.py  # Main pipeline
├── generate_dashboard.py    # Dashboard generator
├── deploy.py                # Deployment script
├── requirements.txt         # Python dependencies
└── .env                     # Environment config
```

---

## 🎯 Monitoring

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Stats Endpoint
```bash
curl http://localhost:8000/api/stats | jq
```

Expected response:
```json
{
  "total_leads": 20,
  "high_priority": 5,
  "with_contacts": 17,
  "unique_companies": 20,
  "last_updated": "October 25, 2025 at 04:31 PM EST"
}
```

---

## 🔒 Security Notes

1. **Never commit `.env`** - Already in `.gitignore`
2. **API tokens** - Store in environment variables only
3. **Rate limiting** - Built into pipeline (2s delay between searches)
4. **CORS** - Currently open, restrict in production

---

## 📝 Customization

### Add New Search Terms
Edit `insurance_leads_pipeline_final.py`:
```python
SEARCH_TERMS = [
    "Commercial Insurance Underwriter",
    "Your New Term Here",  # Add here
]
```

### Adjust Urgency Scoring
Edit `calculate_urgency_score()` method (lines 182-198)

### Change Insurance Keywords
Edit `is_insurance_related()` method (lines 201-213)

---

## 🚢 Production Deployment (Riff)

1. Upload entire project to Riff
2. Set environment variables in Riff dashboard
3. Run: `python deploy.py deploy`
4. Start services:
   - Web: `python deploy.py start`
   - Worker: `python deploy.py worker`
5. Access via Riff-provided URL

---

## 📞 Support

- Check logs: `leads_pipeline.log`, `scraper_worker.log`
- Test pipeline: `python deploy.py pipeline`
- API docs: `http://localhost:8000/docs`
