#!/usr/bin/env python3
"""
Weekly Leads Manager
Appends new leads to existing data with week markers
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyLeadsManager:
    def __init__(self, leads_file: str = "docs/team_leads/team_jobs_data_enriched.json"):
        self.leads_file = Path(leads_file)
        self.weekly_data = self.load_weekly_data()

    def load_weekly_data(self) -> Dict:
        """Load existing weekly leads data"""
        if self.leads_file.exists():
            try:
                with open(self.leads_file, 'r') as f:
                    return json.load(f)
            except:
                return self.create_empty_structure()
        return self.create_empty_structure()

    def create_empty_structure(self) -> Dict:
        """Create empty data structure"""
        return {
            "last_updated": datetime.now().isoformat(),
            "weeks": []
        }

    def add_weekly_batch(self, new_jobs: List[Dict], stats: Dict = None):
        """Add a new week's batch of leads"""
        week_start = datetime.now().strftime("%Y-%m-%d")
        week_display = datetime.now().strftime("%B %d, %Y")  # e.g., "November 20, 2025"

        # Create new week entry
        new_week = {
            "week_start": week_start,
            "week_display": week_display,
            "job_count": len(new_jobs),
            "jobs": new_jobs
        }

        # Add stats if provided
        if stats:
            new_week["stats"] = stats

        # Add to beginning of weeks list (most recent first)
        self.weekly_data["weeks"].insert(0, new_week)
        self.weekly_data["last_updated"] = datetime.now().isoformat()

        # Keep only last 4 weeks (1 month of data)
        if len(self.weekly_data["weeks"]) > 4:
            self.weekly_data["weeks"] = self.weekly_data["weeks"][:4]
            logger.info(f"Trimmed to last 4 weeks of data")

        logger.info(f"Added {len(new_jobs)} jobs for week of {week_display}")
        logger.info(f"Total weeks stored: {len(self.weekly_data['weeks'])}")

    def save(self):
        """Save the weekly leads data"""
        self.leads_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.leads_file, 'w') as f:
            json.dump(self.weekly_data, f, indent=2)

        logger.info(f"Saved weekly leads to {self.leads_file}")

    def get_all_jobs_flat(self) -> List[Dict]:
        """Get all jobs across all weeks as flat list (for backward compatibility)"""
        all_jobs = []
        for week in self.weekly_data["weeks"]:
            for job in week["jobs"]:
                # Add week metadata to each job
                job["week_start"] = week["week_start"]
                job["week_display"] = week["week_display"]
                all_jobs.append(job)
        return all_jobs

    def get_stats_summary(self) -> Dict:
        """Get aggregate stats across all weeks"""
        total_jobs = sum(week["job_count"] for week in self.weekly_data["weeks"])

        # Aggregate by role from latest week's stats
        latest_stats = {}
        if self.weekly_data["weeks"] and "stats" in self.weekly_data["weeks"][0]:
            latest_stats = self.weekly_data["weeks"][0]["stats"]

        return {
            "total_jobs": total_jobs,
            "weeks_stored": len(self.weekly_data["weeks"]),
            "last_updated": self.weekly_data["last_updated"],
            **latest_stats
        }

if __name__ == "__main__":
    # Test with sample data
    manager = WeeklyLeadsManager()

    sample_jobs = [
        {"title": "Test Job 1", "company": "Test Company"},
        {"title": "Test Job 2", "company": "Test Company 2"}
    ]

    sample_stats = {
        "producers": 5,
        "underwriters": 3,
        "account_managers": 2
    }

    manager.add_weekly_batch(sample_jobs, sample_stats)
    manager.save()

    print(f"Total jobs across all weeks: {len(manager.get_all_jobs_flat())}")
    print(f"Stats: {manager.get_stats_summary()}")
