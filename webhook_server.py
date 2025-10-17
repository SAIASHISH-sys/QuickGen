#!/usr/bin/env python3
"""
Standalone Webhook Server for HeyGen Video Callbacks

This server listens for webhook callbacks from HeyGen and processes
video generation completion/failure events.

Usage:
    python3 webhook_server.py

Then expose via ngrok:
    ngrok http 5000

Or deploy to a cloud service for production use.
"""

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Flask not installed. Install with: pip install flask")
    exit(1)

import json
import os
from datetime import datetime

app = Flask(__name__)

# Directory to store webhook logs
LOG_DIR = "webhook_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# File to track completed videos
COMPLETED_VIDEOS_FILE = "completed_videos.json"


def log_webhook(data):
    """Log webhook data to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_type = data.get('event_type', 'unknown').replace('.', '_')
    log_file = f"{LOG_DIR}/webhook_{timestamp}_{event_type}.json"
    
    with open(log_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"📝 Logged to: {log_file}")


def save_completed_video(video_id, video_url, callback_id):
    """Save completed video information."""
    # Load existing data
    if os.path.exists(COMPLETED_VIDEOS_FILE):
        with open(COMPLETED_VIDEOS_FILE, 'r') as f:
            videos = json.load(f)
    else:
        videos = []
    
    # Add new video
    videos.append({
        "video_id": video_id,
        "video_url": video_url,
        "callback_id": callback_id,
        "completed_at": datetime.now().isoformat()
    })
    
    # Save
    with open(COMPLETED_VIDEOS_FILE, 'w') as f:
        json.dump(videos, f, indent=2)
    
    print(f"💾 Saved to: {COMPLETED_VIDEOS_FILE}")


@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "message": "HeyGen Webhook Server",
        "webhook_endpoint": "/webhook"
    }), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook from HeyGen."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        print("\n" + "="*80)
        print("🔔 WEBHOOK RECEIVED")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(json.dumps(data, indent=2))
        print("="*80 + "\n")
        
        # Log the webhook
        log_webhook(data)
        
        # Process the webhook
        event_type = data.get('event_type', '')
        callback_id = data.get('callback_id', 'unknown')
        event_data = data.get('data', {})
        
        if event_type == 'video.complete':
            video_id = event_data.get('video_id')
            video_url = event_data.get('video_url')
            duration = event_data.get('duration', 'unknown')
            thumbnail_url = event_data.get('thumbnail_url', '')
            
            print(f"✅ VIDEO COMPLETED")
            print(f"   Video ID: {video_id}")
            print(f"   Callback ID: {callback_id}")
            print(f"   Duration: {duration}s")
            print(f"   Video URL: {video_url}")
            if thumbnail_url:
                print(f"   Thumbnail: {thumbnail_url}")
            
            # Save to file
            save_completed_video(video_id, video_url, callback_id)
            
            # You can add custom processing here
            # For example: download the video, send notification, etc.
            
        elif event_type == 'video.failed':
            video_id = event_data.get('video_id')
            error = event_data.get('error', 'Unknown error')
            
            print(f"❌ VIDEO FAILED")
            print(f"   Video ID: {video_id}")
            print(f"   Callback ID: {callback_id}")
            print(f"   Error: {error}")
            
        else:
            print(f"⚠️  UNKNOWN EVENT TYPE: {event_type}")
        
        # Return success response
        return jsonify({
            "status": "received",
            "event_type": event_type,
            "callback_id": callback_id
        }), 200
    
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/videos', methods=['GET'])
def list_videos():
    """List all completed videos."""
    if not os.path.exists(COMPLETED_VIDEOS_FILE):
        return jsonify({"videos": []}), 200
    
    with open(COMPLETED_VIDEOS_FILE, 'r') as f:
        videos = json.load(f)
    
    return jsonify({
        "count": len(videos),
        "videos": videos
    }), 200


if __name__ == '__main__':
    import sys
    
    port = int(os.getenv('PORT', 5000))
    
    print("\n" + "="*80)
    print("🔔 HEYGEN WEBHOOK SERVER")
    print("="*80)
    print(f"\nStarting server on port {port}...")
    print(f"\nEndpoints:")
    print(f"  - Health Check: http://localhost:{port}/")
    print(f"  - Webhook:      http://localhost:{port}/webhook")
    print(f"  - List Videos:  http://localhost:{port}/videos")
    print(f"\nTo expose publicly with ngrok:")
    print(f"  ngrok http {port}")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)
