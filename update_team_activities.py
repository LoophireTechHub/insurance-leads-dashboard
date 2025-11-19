#!/usr/bin/env python3
"""
Update Team Activities Database
Run this script manually or via cron to update the shared activities database
"""

import json
import os
from datetime import datetime

# Path to the activities database
DB_PATH = 'docs/team_leads/activities_database.json'

def load_database():
    """Load the current activities database"""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    return {
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'activities': {}
    }

def save_database(data):
    """Save the activities database"""
    data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Updated activities database: {len(data['activities'])} jobs tracked")

def merge_activities(job_id, new_activities):
    """Merge new activities for a specific job"""
    db = load_database()

    if job_id not in db['activities']:
        db['activities'][job_id] = {}

    # Merge the activities
    db['activities'][job_id].update(new_activities)

    save_database(db)
    return db

def get_all_activities():
    """Get all tracked activities"""
    db = load_database()
    return db['activities']

def clear_job_activity(job_id):
    """Clear activities for a specific job"""
    db = load_database()
    if job_id in db['activities']:
        del db['activities'][job_id]
        save_database(db)
        print(f"✓ Cleared activities for job: {job_id}")
    else:
        print(f"✗ No activities found for job: {job_id}")

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python update_team_activities.py list")
        print("  python update_team_activities.py update <job_id> '<json>'")
        print("  python update_team_activities.py clear <job_id>")
        print("\nExample:")
        print('  python update_team_activities.py update "https://job-url" \'{"called": true, "linkedin": true}\'')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        activities = get_all_activities()
        print(json.dumps(activities, indent=2))

    elif command == 'update' and len(sys.argv) >= 4:
        job_id = sys.argv[2]
        new_activities = json.loads(sys.argv[3])
        merge_activities(job_id, new_activities)

    elif command == 'clear' and len(sys.argv) >= 3:
        job_id = sys.argv[2]
        clear_job_activity(job_id)

    else:
        print("Invalid command or arguments")
        sys.exit(1)
