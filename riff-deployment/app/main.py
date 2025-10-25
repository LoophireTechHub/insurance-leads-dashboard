#!/usr/bin/env python3
"""
Insurance Leads Dashboard - FastAPI Application
Main application for serving the dashboard and API endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Insurance Leads Dashboard",
    description="Automated insurance job leads pipeline with contact enrichment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data paths
DOCS_DIR = Path("docs")
DATA_FILE = DOCS_DIR / "data.json"
INDEX_FILE = DOCS_DIR / "index.html"


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard HTML"""
    try:
        if INDEX_FILE.exists():
            with open(INDEX_FILE, 'r') as f:
                return f.read()
        else:
            return """
            <html>
                <head><title>Insurance Leads Dashboard</title></head>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                    <h1>🎯 Insurance Leads Dashboard</h1>
                    <p>Dashboard initializing... Run the pipeline to generate data.</p>
                    <p><a href="/api/health">Check API Health</a></p>
                </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Error serving dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Insurance Leads Dashboard"
    }


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    try:
        if not DATA_FILE.exists():
            return {"error": "No data available yet. Run the pipeline first."}

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        return data.get('stats', {})
    except Exception as e:
        logger.error(f"Error reading stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads")
async def get_leads():
    """Get all leads data"""
    try:
        if not DATA_FILE.exists():
            return {"leads": [], "message": "No data available yet"}

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        return {
            "leads": data.get('leads', []),
            "stats": data.get('stats', {}),
            "total": len(data.get('leads', []))
        }
    except Exception as e:
        logger.error(f"Error reading leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{lead_index}")
async def get_lead(lead_index: int):
    """Get specific lead by index"""
    try:
        if not DATA_FILE.exists():
            raise HTTPException(status_code=404, detail="No data available")

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        leads = data.get('leads', [])

        if lead_index < 0 or lead_index >= len(leads):
            raise HTTPException(status_code=404, detail="Lead not found")

        return leads[lead_index]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/trigger")
async def trigger_pipeline():
    """Trigger the leads pipeline manually"""
    try:
        import subprocess

        result = subprocess.run(
            ["python3", "insurance_leads_pipeline_final.py"],
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Pipeline completed successfully",
                "output": result.stdout[-500:]
            }
        else:
            return {
                "status": "error",
                "message": "Pipeline failed",
                "error": result.stderr[-500:]
            }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Pipeline timeout")
    except Exception as e:
        logger.error(f"Error triggering pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data.json")
async def get_data_json():
    """Get raw data.json"""
    try:
        if not DATA_FILE.exists():
            raise HTTPException(status_code=404, detail="Data not found")

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)

        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
