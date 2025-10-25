#!/usr/bin/env python3
"""
Insurance Leads Scraper Worker
Background worker that runs the pipeline on schedule
"""

import schedule
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_worker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the insurance leads pipeline"""
    logger.info("="*50)
    logger.info("Starting scheduled pipeline run")
    logger.info("="*50)

    try:
        # Run the main pipeline script
        result = subprocess.run(
            ["python3", "insurance_leads_pipeline_final.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            logger.info("✅ Pipeline completed successfully")
            logger.info(f"Output: {result.stdout[-200:]}")  # Last 200 chars

            # Generate dashboard
            subprocess.run(
                ["python3", "generate_dashboard.py"],
                timeout=60
            )
            logger.info("✅ Dashboard generated")
        else:
            logger.error(f"❌ Pipeline failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("❌ Pipeline timeout after 10 minutes")
    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}")

    logger.info("="*50)


def main():
    """Main worker function with scheduling"""
    logger.info("🚀 Insurance Leads Scraper Worker Started")
    logger.info(f"📅 Scheduled to run daily at 14:00 UTC (2:00 PM)")

    # Schedule daily run at 2 PM UTC (matches GitHub Actions)
    schedule.every().day.at("14:00").do(run_pipeline)

    # Optional: Run immediately on startup (comment out if not needed)
    logger.info("🔄 Running initial pipeline on startup...")
    run_pipeline()

    # Keep the worker running
    logger.info("⏰ Worker is now running. Waiting for scheduled jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
