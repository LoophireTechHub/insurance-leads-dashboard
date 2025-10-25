#!/usr/bin/env python3
"""
Background Worker for Daily Lead Scraping
Run this in the background to automatically scrape leads daily
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Execute the insurance leads pipeline"""
    logger.info("🚀 Starting scheduled pipeline run...")

    try:
        result = subprocess.run(
            ["python3", "insurance_leads_pipeline_final.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode == 0:
            logger.info("✅ Pipeline completed successfully")
            logger.info(f"Output preview: {result.stdout[-200:]}")
        else:
            logger.error("❌ Pipeline failed")
            logger.error(f"Error: {result.stderr[-200:]}")

    except subprocess.TimeoutExpired:
        logger.error("⏱️ Pipeline timed out after 10 minutes")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


def main():
    """Main worker loop"""
    logger.info("🤖 Insurance Leads Worker Started")
    logger.info("📅 Scheduled to run daily at 8:00 AM")

    # Schedule daily run at 8 AM
    schedule.every().day.at("08:00").do(run_pipeline)

    # Optional: Run immediately on startup
    logger.info("Running initial pipeline...")
    run_pipeline()

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
