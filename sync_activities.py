#!/usr/bin/env python3
"""
Activity Sync Script for Team Dashboard
Syncs activity data to GitHub so it's shared across all team members
"""

import json
import os
import sys
from datetime import datetime
import requests
import base64

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'LoophireTechHub'
REPO_NAME = 'loophireteam-chrisinsuranceleads'
FILE_PATH = 'docs/team_leads/activities_database.json'
BRANCH = 'main'

def get_file_sha():
    """Get the current SHA of the activities file"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['sha']
    return None

def update_activities_file(activities_data):
    """Update the activities file on GitHub"""
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN not found in environment variables")
        return False

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Get current file SHA
    sha = get_file_sha()

    # Prepare the data
    file_data = {
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'activities': activities_data
    }

    content = json.dumps(file_data, indent=2)
    content_bytes = content.encode('utf-8')
    content_base64 = base64.b64encode(content_bytes).decode('utf-8')

    # Prepare the update payload
    payload = {
        'message': f'Update activity tracking - {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC',
        'content': content_base64,
        'branch': BRANCH
    }

    if sha:
        payload['sha'] = sha

    # Update the file
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"✓ Successfully updated activities database")
        return True
    else:
        print(f"✗ Failed to update activities: {response.status_code}")
        print(response.json())
        return False

def get_activities():
    """Get current activities from GitHub"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()['content']
        decoded = base64.b64decode(content).decode('utf-8')
        return json.loads(decoded).get('activities', {})
    return {}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Update mode: python sync_activities.py '{"job-url": {"called": true}}'
        try:
            new_activities = json.loads(sys.argv[1])
            # Merge with existing activities
            current = get_activities()
            current.update(new_activities)
            success = update_activities_file(current)
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Read mode: just print current activities
        activities = get_activities()
        print(json.dumps(activities, indent=2))
