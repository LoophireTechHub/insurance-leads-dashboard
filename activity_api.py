#!/usr/bin/env python3
"""
Activity Tracking API Server
Provides REST API endpoints for the team dashboard to sync activities across users
Run with: python3 activity_api.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the activities database
DB_PATH = 'docs/team_leads/activities_database.json'

# Lock for thread-safe file access
db_lock = threading.Lock()

def load_database():
    """Load the current activities database"""
    with db_lock:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r') as f:
                return json.load(f)
        return {
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'activities': {}
        }

def save_database(data):
    """Save the activities database"""
    with db_lock:
        data['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        with open(DB_PATH, 'w') as f:
            json.dump(data, f, indent=2)

        # Auto-sync to GitHub in background (non-blocking)
        try:
            subprocess.Popen(
                ['./auto_sync_activities.sh'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Warning: Auto-sync failed: {e}")

@app.route('/api/activities', methods=['GET'])
def get_all_activities():
    """Get all tracked activities"""
    try:
        db = load_database()
        return jsonify({
            'success': True,
            'last_updated': db['last_updated'],
            'activities': db['activities']
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
        db = load_database()
        activities = db['activities'].get(job_id, {})
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

        db = load_database()

        # Initialize if not exists
        if job_id not in db['activities']:
            db['activities'][job_id] = {}

        # Merge activities
        db['activities'][job_id].update(data['activities'])

        # Remove empty activities
        if not db['activities'][job_id]:
            del db['activities'][job_id]

        save_database(db)

        return jsonify({
            'success': True,
            'job_id': job_id,
            'activities': db['activities'].get(job_id, {})
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
        db = load_database()

        if job_id in db['activities']:
            del db['activities'][job_id]
            save_database(db)
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Activity Tracking API',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Activity Tracking API Server")
    print("=" * 60)
    print(f"Database: {os.path.abspath(DB_PATH)}")
    print("Endpoints:")
    print("  GET    /api/activities          - Get all activities")
    print("  GET    /api/activities/<job_id> - Get activity for job")
    print("  POST   /api/activities/<job_id> - Update activity for job")
    print("  DELETE /api/activities/<job_id> - Delete activity for job")
    print("  GET    /api/health              - Health check")
    print("=" * 60)
    print("\n⚡ Server running on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    # Run with threading enabled for better performance
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
