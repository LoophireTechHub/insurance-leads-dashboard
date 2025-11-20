#!/usr/bin/env python3
"""
Activity Tracking API Server - Production Version
Provides REST API endpoints for the team dashboard to sync activities across users
Stores data in memory and syncs back to GitHub via GitHub API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory activities database
activities_db = {
    'last_updated': datetime.utcnow().isoformat() + 'Z',
    'activities': {}
}

# Lock for thread-safe access
db_lock = threading.Lock()

# GitHub configuration (from environment variables)
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'LoophireTechHub/loophireteam-chrisinsuranceleads')
ACTIVITIES_FILE_PATH = 'docs/team_leads/activities_database.json'

def load_from_github():
    """Load activities from GitHub"""
    global activities_db

    if not GITHUB_TOKEN:
        print("⚠️ No GITHUB_TOKEN set - using in-memory storage only")
        return

    try:
        url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{ACTIVITIES_FILE_PATH}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            with db_lock:
                activities_db = json.loads(content)
            print(f"✅ Loaded {len(activities_db.get('activities', {}))} activities from GitHub")
        else:
            print(f"⚠️ Could not load from GitHub: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error loading from GitHub: {e}")

def save_to_github():
    """Save activities back to GitHub"""
    if not GITHUB_TOKEN:
        return

    try:
        # Get current file SHA
        url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{ACTIVITIES_FILE_PATH}'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }

        response = requests.get(url, headers=headers)
        sha = response.json().get('sha', '') if response.status_code == 200 else None

        # Prepare content
        import base64
        content = json.dumps(activities_db, indent=2)
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        # Update file
        data = {
            'message': f'Update activities - {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC',
            'content': encoded_content,
            'branch': 'main'
        }

        if sha:
            data['sha'] = sha

        response = requests.put(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            print(f"✅ Saved {len(activities_db.get('activities', {}))} activities to GitHub")
        else:
            print(f"⚠️ Could not save to GitHub: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Error saving to GitHub: {e}")

@app.route('/api/activities', methods=['GET'])
def get_all_activities():
    """Get all tracked activities"""
    try:
        with db_lock:
            return jsonify({
                'success': True,
                'last_updated': activities_db['last_updated'],
                'activities': activities_db['activities']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/activities/<path:job_id>', methods=['GET'])
def get_activity(job_id):
    """Get activities for a specific job"""
    try:
        with db_lock:
            activities = activities_db['activities'].get(job_id, {})
        return jsonify({
            'success': True,
            'job_id': job_id,
            'activities': activities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/activities/<path:job_id>', methods=['POST', 'PUT'])
def update_activity(job_id):
    """Update activities for a specific job"""
    try:
        data = request.get_json()

        if not data or 'activities' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing activities in request body'
            }), 400

        with db_lock:
            # Initialize if not exists
            if job_id not in activities_db['activities']:
                activities_db['activities'][job_id] = {}

            # Merge activities
            activities_db['activities'][job_id].update(data['activities'])

            # Remove empty activities
            if not activities_db['activities'][job_id]:
                del activities_db['activities'][job_id]

            # Update timestamp
            activities_db['last_updated'] = datetime.utcnow().isoformat() + 'Z'

            result_activities = activities_db['activities'].get(job_id, {})

        # Save to GitHub in background
        threading.Thread(target=save_to_github, daemon=True).start()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'activities': result_activities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/activities/<path:job_id>', methods=['DELETE'])
def delete_activity(job_id):
    """Delete activities for a specific job"""
    try:
        with db_lock:
            if job_id in activities_db['activities']:
                del activities_db['activities'][job_id]
                activities_db['last_updated'] = datetime.utcnow().isoformat() + 'Z'
                found = True
            else:
                found = False

        if found:
            # Save to GitHub in background
            threading.Thread(target=save_to_github, daemon=True).start()

            return jsonify({
                'success': True,
                'message': f'Activities deleted for job: {job_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'No activities found for job: {job_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sync', methods=['POST'])
def manual_sync():
    """Manually trigger sync from GitHub"""
    load_from_github()
    return jsonify({
        'success': True,
        'message': 'Synced from GitHub',
        'activities_count': len(activities_db.get('activities', {}))
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Activity Tracking API',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'activities_count': len(activities_db.get('activities', {})),
        'github_enabled': bool(GITHUB_TOKEN)
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'Insurance Leads Activity Tracking API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/health': 'Health check',
            'GET /api/activities': 'Get all activities',
            'GET /api/activities/<job_id>': 'Get activity for specific job',
            'POST /api/activities/<job_id>': 'Update activity for specific job',
            'DELETE /api/activities/<job_id>': 'Delete activity for specific job',
            'POST /api/sync': 'Manually sync from GitHub'
        }
    })

# Load initial data from GitHub on startup
load_from_github()

# Auto-sync from GitHub every 5 minutes
def auto_sync():
    import time
    while True:
        time.sleep(300)  # 5 minutes
        load_from_github()

threading.Thread(target=auto_sync, daemon=True).start()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Activity Tracking API Server (Production)")
    print("=" * 60)
    print(f"GitHub Repo: {GITHUB_REPO}")
    print(f"GitHub Token: {'✅ Set' if GITHUB_TOKEN else '❌ Not set'}")
    print(f"Activities: {len(activities_db.get('activities', {}))} loaded")
    print("=" * 60)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
