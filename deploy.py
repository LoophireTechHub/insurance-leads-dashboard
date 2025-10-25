#!/usr/bin/env python3
"""
Insurance Leads Dashboard - Deployment Script for Riff
Handles setup, configuration, and deployment
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def setup_environment():
    """Setup environment and dependencies"""
    print("\n🚀 Setting up Insurance Leads Dashboard Environment")

    # Create necessary directories
    Path("docs").mkdir(exist_ok=True)
    Path("leads_output").mkdir(exist_ok=True)
    Path("app").mkdir(exist_ok=True)

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False

    # Check for .env file
    if not Path(".env").exists():
        print("\n⚠️  No .env file found. Creating template...")
        with open(".env", "w") as f:
            f.write("""# Insurance Leads Dashboard Environment Variables

# Apify Configuration
APIFY_API_TOKEN=your_apify_token_here

# Apollo.io Configuration
APOLLO_API_TOKEN=your_apollo_token_here

# Application Settings
PORT=8000
HOST=0.0.0.0
DEBUG=false

# Pipeline Schedule (cron format)
PIPELINE_SCHEDULE=0 14 * * *
""")
        print("✅ Created .env template. Please update with your actual tokens.")
        return False

    print("✅ Environment setup complete")
    return True


def run_migrations():
    """Run any database migrations (if needed)"""
    print("\n📊 Running migrations...")
    # No database migrations needed for this project currently
    print("✅ Migrations complete (none required)")
    return True


def start_app():
    """Start the FastAPI application"""
    print("\n🌐 Starting Insurance Leads Dashboard...")
    print("Dashboard will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop\n")

    try:
        subprocess.run(["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")


def start_worker():
    """Start the background scraper worker"""
    print("\n⚙️  Starting background scraper worker...")
    print("Worker will run pipeline daily at 14:00 UTC")
    print("\nPress Ctrl+C to stop\n")

    try:
        subprocess.run(["python3", "app/scraper_worker.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Worker stopped")


def deploy():
    """Full deployment process"""
    print("\n" + "="*60)
    print("🎯 INSURANCE LEADS DASHBOARD - DEPLOYMENT")
    print("="*60)

    steps = [
        (setup_environment, "Environment Setup"),
        (run_migrations, "Database Migrations"),
    ]

    for step_func, step_name in steps:
        if not step_func():
            print(f"\n❌ Deployment failed at: {step_name}")
            return False

    print("\n" + "="*60)
    print("✅ DEPLOYMENT SUCCESSFUL")
    print("="*60)
    print("\nNext steps:")
    print("  1. Update .env with your API tokens")
    print("  2. Run: python deploy.py start")
    print("  3. Visit http://localhost:8000")
    print("\nOptional:")
    print("  - Run pipeline manually: python insurance_leads_pipeline_final.py")
    print("  - Start background worker: python deploy.py worker")
    return True


def run_pipeline():
    """Run the pipeline manually"""
    print("\n🔄 Running Insurance Leads Pipeline...")
    if run_command("python3 insurance_leads_pipeline_final.py", "Fetching and processing leads"):
        run_command("python3 generate_dashboard.py", "Generating dashboard")
        print("\n✅ Pipeline complete! Check docs/index.html")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Insurance Leads Dashboard Deployment Tool"
    )
    parser.add_argument(
        "command",
        choices=["deploy", "start", "worker", "setup", "migrate", "pipeline"],
        help="Command to execute"
    )

    args = parser.parse_args()

    if args.command == "deploy":
        deploy()
    elif args.command == "start":
        start_app()
    elif args.command == "worker":
        start_worker()
    elif args.command == "setup":
        setup_environment()
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "pipeline":
        run_pipeline()


if __name__ == "__main__":
    main()
