import requests
import time
import os
import glob
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from threading import Thread, Event
import json

load_dotenv()
API_KEY = os.getenv("HEYGEN_API_KEY")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", None)  

DEFAULT_AVATAR_ID = "Artur_sitting_sofacasual_front"  # HeyGen's public avatar


VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
USE_TEST_MODE = os.getenv("USE_TEST_MODE", "true").lower() == "true"

# API Endpoints
BASE_URL = "https://api.heygen.com"
GENERATE_ENDPOINT = f"{BASE_URL}/v2/video/generate"
STATUS_ENDPOINT = f"{BASE_URL}/v1/video_status.get"
UPLOAD_ASSET_ENDPOINT = "https://upload.heygen.com/v1/asset"

# --- HELPER FUNCTIONS ---
def upload_audio_file(api_key, audio_file_path):
    """Upload a local audio file to HeyGen and return the asset URL."""
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        return None
    
    headers = {
        "Content-Type": "audio/mpeg",
        "X-Api-Key": api_key}
    
    print(f" Uploading audio file: {audio_file_path}")
    
    try:
        with open(audio_file_path, 'rb') as audio_file:       
            response = requests.post(UPLOAD_ASSET_ENDPOINT, headers=headers, data=audio_file)
            
            # Print response for debugging
            print(f"   Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f" Upload failed with status {response.status_code}")
                print(f" Response: {response.text}")
                return None
            
            data = response.json()
            
            if data.get('data') and data['data'].get('url'):
                asset_url = data['data']['url']
                print(f" Audio uploaded successfully!")
                print(f" Asset URL: {asset_url}")
                return asset_url
            else:
                print(" Error: Could not retrieve asset URL from upload response.")
                print("Full response:", data)
                return None
                
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during audio upload: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def list_commentary_files():
    """List all MP3 files in the commentaries directory."""
    commentary_dir = "commentaries"
    
    if not os.path.exists(commentary_dir):
        print(f"Error: {commentary_dir} directory not found.")
        return []
    
    mp3_files = glob.glob(f"{commentary_dir}/*.mp3")
    
    if not mp3_files:
        print(f"No MP3 files found in {commentary_dir}/")
        return []
    
    return mp3_files


def select_audio_file():
    """Allow user to select an audio file from available options."""
    mp3_files = list_commentary_files()
    
    if not mp3_files:
        return None
    
    print("\n" + "="*80)
    print("AVAILABLE AUDIO COMMENTARIES")
    print("="*80 + "\n")
    
    for idx, file_path in enumerate(mp3_files, 1):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        print(f"{idx}. {file_name} ({file_size:.2f} MB)")
    
    print("\n" + "="*80 + "\n")
    
    while True:
        try:
            choice = input(f"Select audio file (1-{len(mp3_files)}) or enter file path: ").strip()
            # Check if it's a number (selection from list)
            try:
                file_num = int(choice)
                
                if 1 <= file_num <= len(mp3_files):
                    return mp3_files[file_num - 1]
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(mp3_files)}.")
            except ValueError:
                # It's a file path
                if os.path.exists(choice) and choice.endswith('.mp3'):
                    return choice
                else:
                    print("Invalid file path or not an MP3 file. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return None

def generate_video(api_key, avatar_id, audio_url, title="AI Cricket Commentary", webhook_url=None):
    """Starts the video generation process and returns the video ID."""
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id
                },
                "voice": {
                    "type": "audio",
                    "audio_url": audio_url
                }
            }
        ],
        "dimension": {
            "width": VIDEO_WIDTH,
            "height": VIDEO_HEIGHT
        },
        "title": title,
        "test": USE_TEST_MODE
    }
    
    # Add webhook URL if provided
    if webhook_url:
        payload["callback_id"] = f"video_{int(time.time())}"
        payload["webhook"] = {
            "url": webhook_url,
            "events": ["video.complete", "video.failed"]
        }
        print(f"Webhook configured: {webhook_url}")
    
    print(f"Video settings: {VIDEO_WIDTH}x{VIDEO_HEIGHT} {'(test mode)' if USE_TEST_MODE else '(production)'}")
    
    print("Starting video generation...")
    try:
        response = requests.post(GENERATE_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        if not data.get('data') or not data['data'].get('video_id'):
            print("Error: Could not retrieve video ID.")
            print("Full response:", data)
            return None
            
        video_id = data['data']['video_id']
        print(f"Video generation started successfully. Video ID: {video_id}")
        return video_id
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def poll_video_status(api_key, video_id):
    """Checks the video status periodically until it's completed or fails."""
    headers = {"X-Api-Key": api_key}
    params = {"video_id": video_id}
    
    print("\n Polling video status... (checking every 15 seconds)")
    
    while True:
        try:
            response = requests.get(STATUS_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()['data']
            status = data.get('status')
            
            if status == 'completed':
                video_url = data.get('video_url')
                print(f"Video processing completed!")
                print(f"Download URL: {video_url}")
                return video_url
            elif status == 'failed':
                error_message = data.get('error', 'Unknown error')
                print(f"Video processing failed. Reason: {error_message}")
                return None
            else:
                print(f"Current status: {status}...")
                time.sleep(15) # Wait before checking again
                
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while checking status: {e}")
            return None

def download_video(video_url, output_path="output_video.mp4"):
    """Download the generated video to a local file."""
    print(f"\n Downloading video to {output_path}...")
    
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f" Video downloaded successfully to {output_path}")
        return output_path
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        return None


# --- WEBHOOK SUPPORT ---

# Global variables for webhook
webhook_result = {}
webhook_event = Event()
app = None
webhook_server_started = False

def create_webhook_server():
    """Create a Flask webhook server to receive HeyGen callbacks."""
    global app
    
    try:
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming webhook from HeyGen."""
            global webhook_result
            
            data = request.json
            print(f"\n🔔 Webhook received!")
            print(f"   Event: {data.get('event_type', 'unknown')}")
            
            # Store the result
            webhook_result = data
            
            # Signal that webhook was received
            webhook_event.set()
            
            return jsonify({"status": "received"}), 200
        
        return app
    except ImportError:
        print("  Flask not installed. Webhook support disabled.")
        print("   Install with: pip install flask")
        return None


def start_webhook_server(port=5000):
    """Start webhook server in a background thread."""
    global app
    
    if app is None:
        app = create_webhook_server()
    
    if app is None:
        return None
    
    def run_server():
        # Suppress Flask's default logging
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    
    print(f" Webhook server started on port {port}")
    print(f"   Listening at: http://localhost:{port}/webhook")
    
    return thread


def wait_for_webhook(timeout=600):
    """Wait for webhook callback with timeout."""
    global webhook_result, webhook_event
    
    print(f"\n Waiting for webhook callback (timeout: {timeout}s)...")
    print("   Press Ctrl+C to fall back to polling")
    
    try:
        if webhook_event.wait(timeout):
            # Webhook received
            event_type = webhook_result.get('event_type', '')
            
            if event_type == 'video.complete':
                video_url = webhook_result.get('data', {}).get('video_url')
                if video_url:
                    print(f" Video processing completed (via webhook)!")
                    print(f" Download URL: {video_url}")
                    return video_url
            elif event_type == 'video.failed':
                error = webhook_result.get('data', {}).get('error', 'Unknown error')
                print(f" Video processing failed: {error}")
                return None
            
            # Unknown event
            print(f"Received unknown webhook event: {event_type}")
            return None
        else:
            # Timeout
            print("Webhook timeout. Falling back to polling...")
            return None
    
    except KeyboardInterrupt:
        print("\n Webhook wait interrupted. Falling back to polling...")
        return None


def wait_for_video_with_webhook_fallback(api_key, video_id, webhook_url=None, webhook_timeout=600):
    """
    Try webhook first, then fall back to polling if webhook fails or times out.
    
    Args:
        api_key: HeyGen API key
        video_id: Video ID from generate_video()
        webhook_url: Optional webhook URL (if None, will skip webhook and use polling)
        webhook_timeout: Timeout in seconds for webhook (default 600 = 10 minutes)
    
    Returns:
        video_url: URL of completed video, or None if failed
    """
    global webhook_event, webhook_result, webhook_server_started
    
    video_url = None
    
    # Try webhook first if URL is provided
    if webhook_url:
        # Start webhook server if not already started
        if not webhook_server_started:
            try:
                print(f"\n Starting webhook server on port {WEBHOOK_PORT}...")
                start_webhook_server(WEBHOOK_PORT)
                webhook_server_started = True
                print(f"   Webhook server ready!")
            except Exception as e:
                print(f"   Warning: Could not start webhook server: {e}")
                print(f"   Falling back to polling...")
                return poll_video_status(api_key, video_id)
        
        print(f"\n Trying webhook method first...")
        print(f"   Webhook URL: {webhook_url}")
        
        # Reset webhook event
        webhook_event.clear()
        webhook_result = {}
        
        # Wait for webhook
        video_url = wait_for_webhook(timeout=webhook_timeout)
        
        # If webhook succeeded, return the URL
        if video_url:
            return video_url
        
        # Webhook failed or timed out, fall back to polling
        print(f"\n Webhook failed or timed out. Switching to polling method...")
    else:
        print(f"\n No webhook URL provided. Using polling method...")
    
    # Fall back to polling
    video_url = poll_video_status(api_key, video_id)
    
    return video_url


# --- 3. RUN THE PIPELINE ---

def main():
    """Main function to generate AI video from commentary."""
    print("\n" + "="*80)
    print("AI VIDEO GENERATOR - Cricket Commentary")
    print("="*80 + "\n")
    
    # Check API key
    if not API_KEY or API_KEY == "YOUR_HEYGEN_API_KEY_HERE":
        print("Error: HEYGEN_API_KEY not found in .env file")
        print("Please add your HeyGen API key to the .env file:")
        print("HEYGEN_API_KEY=your_api_key_here")
        return
    
    # Select audio file
    print("Step 1: Select your commentary audio file")
    audio_file_path = select_audio_file()
    
    if not audio_file_path:
        print("No audio file selected. Exiting.")
        return
    
    print(f"\nSelected: {audio_file_path}")
    
    # Upload audio file
    print("\nStep 2: Upload audio to HeyGen")
    audio_url = upload_audio_file(API_KEY, audio_file_path)
    
    if not audio_url:
        print(" Failed to upload audio. Exiting.")
        return
    
    # Get avatar ID (use default or ask user)
    avatar_id = DEFAULT_AVATAR_ID
    print(f"\nStep 3: Using avatar: {avatar_id}")
    print("(You can change DEFAULT_AVATAR_ID in the script to use a different avatar)")
    
    # Generate video title from file name
    file_name = os.path.basename(audio_file_path).replace('.mp3', '')
    video_title = f"Cricket Commentary - {file_name}"
    
    # Ask user about webhook vs polling
    print("\nStep 4: Choose completion notification method")
    print("  1. Webhook (recommended - instant notification, requires public URL)")
    print("  2. Polling (check status every 15 seconds)")
    
    use_webhook = False
    webhook_url_to_use = None
    
    mode_choice = input("Select mode (1/2) [default: 2]: ").strip()
    
    if mode_choice == '1':
        # Try to start webhook server
        if WEBHOOK_URL:
            webhook_url_to_use = WEBHOOK_URL
            print(f"Using webhook URL from .env: {WEBHOOK_URL}")
            use_webhook = True
        else:
            # Ask if user wants to use local webhook server
            local_choice = input("\nNo WEBHOOK_URL in .env. Start local webhook server? (y/n): ").strip().lower()
            
            if local_choice == 'y':
                try:
                    start_webhook_server(WEBHOOK_PORT)
                    
                    # User needs to expose this via ngrok or similar
                    print("\n IMPORTANT: Your webhook server is running locally.")
                    print("   To receive webhooks from HeyGen, you need to expose it publicly.")
                    print("   Options:")
                    print("   1. Use ngrok: ngrok http 5000")
                    print("   2. Deploy to a cloud service")
                    print("   3. Use a service like localtunnel")
                    
                    webhook_input = input(f"\nEnter your public webhook URL (or press Enter to use polling): ").strip()
                    
                    if webhook_input:
                        webhook_url_to_use = webhook_input
                        use_webhook = True
                    else:
                        print("No webhook URL provided. Falling back to polling mode.")
                        use_webhook = False
                except Exception as e:
                    print(f"Error starting webhook server: {e}")
                    print("Falling back to polling mode.")
                    use_webhook = False
    
    # Generate video
    print("\nStep 5: Generate AI video")
    video_id = generate_video(API_KEY, avatar_id, audio_url, video_title, webhook_url_to_use)
    
    if not video_id:
        print("Failed to start video generation. Exiting.")
        return
    
    # Wait for completion
    print("\nStep 6: Wait for video processing")
    video_url = None
    
    if use_webhook and webhook_url_to_use:
        # Try webhook first
        video_url = wait_for_webhook(timeout=600)
        
        # If webhook failed/timeout, fall back to polling
        if not video_url:
            print("\nWebhook failed or timed out. Switching to polling...")
            video_url = poll_video_status(API_KEY, video_id)
    else:
        # Use polling
        video_url = poll_video_status(API_KEY, video_id)
    
    if not video_url:
        print("Video generation failed or timed out.")
        return
    
    # Ask if user wants to download
    download_choice = input("\n Would you like to download the video? (y/n): ").strip().lower()
    
    if download_choice == 'y':
        output_path = f"videos/{file_name}.mp4"
        os.makedirs("videos", exist_ok=True)
        download_video(video_url, output_path)
    
    print("\n" + "="*80)
    print("AI Video generation completed!")
    print(f"Video URL: {video_url}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()