from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from dotenv import load_dotenv
import glob
from datetime import datetime
from commentary import get_langchain_response
from texttospeech import text_to_speech_file, clean_commentary_text
from aivideo import (upload_audio_file, generate_video, wait_for_video_with_webhook_fallback,
                     DEFAULT_AVATAR_ID, WEBHOOK_URL)
import threading
import sys
from pathlib import Path

# Add graphs_gen to path for scoreboard generation
sys.path.insert(0, str(Path(__file__).parent / "graphs_gen"))
from img_generator import generate_scoreboards_sync

# Import video combining
from video_combining import combine_video_with_scoreboards

load_dotenv()
API_KEY = os.getenv("HEYGEN_API_KEY")
app = Flask(__name__)

# Global variable to track generation status
generation_status = {}

def load_matches(year):
    """Load matches from the JSON file for a specific year."""
    json_file = f"data/ipl_{year}.json"
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        return matches
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def get_available_years():
    """Get list of available IPL years from data folder."""
    years = []
    for file in glob.glob("data/ipl_*.json"):
        year = file.split('_')[1].split('.')[0]
        years.append(year)
    return sorted(years)

def generate_highlight_async(year, match_num, match_data):
    """Generate highlight asynchronously."""
    global generation_status
    
    job_id = f"{year}_{match_num}"
    
    # Update existing status instead of reinitializing
    # (status was already initialized in the /api/generate endpoint)
    if job_id not in generation_status:
        generation_status[job_id] = {
            "status": "starting",
            "progress": 0,
            "message": "Initializing...",
            "video_url": None,
            "error": None
        }
    
    try:
        # Update status
        generation_status[job_id]["status"] = "starting"
        generation_status[job_id]["progress"] = 5
        generation_status[job_id]["message"] = "Setting up..."
        
        teams = match_data.get('teams', ['Unknown', 'Unknown'])
        team_names = "_vs_".join(teams)
        # Create folder structure: commentaries/year/match_X_TEAM_vs_TEAM
        match_folder = f"commentaries/{year}/match_{match_num}_{team_names}"
        os.makedirs(match_folder, exist_ok=True)
        
        # Step 1: Save match data
        generation_status[job_id]["status"] = "saving_data"
        generation_status[job_id]["progress"] = 10
        generation_status[job_id]["message"] = "Saving match data..."
        
        match_data_file = f"{match_folder}/match_data.json"
        with open(match_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "match_number": match_num,
                "year": year,
                "teams": teams,
                "match_data": match_data,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        
        # Step 2: Generate commentary
        commentary_file = f"{match_folder}/commentary.txt"
        
        if os.path.exists(commentary_file):
            generation_status[job_id]["status"] = "loading_commentary"
            generation_status[job_id]["progress"] = 20
            generation_status[job_id]["message"] = "Loading existing commentary..."
            
            # Read existing commentary
            with open(commentary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract just the commentary text (skip header)
                parts = content.split("="*80)
                if len(parts) >= 2:
                    commentary = parts[1].strip()
                else:
                    commentary = content
            print(f"[DEBUG] Loaded existing commentary from {commentary_file}")
        else:
            generation_status[job_id]["status"] = "generating_commentary"
            generation_status[job_id]["progress"] = 20
            generation_status[job_id]["message"] = "Generating AI commentary..."
            
            match_json_str = json.dumps(match_data, indent=2)
            prompt = f"""Here is the match data for IPL {year} Match #{match_num}:

{match_json_str}

Please generate an exciting and detailed 1:30 minute cricket commentary summarizing this match."""
            
            commentary = get_langchain_response(prompt)
            
            # Save commentary
            with open(commentary_file, 'w', encoding='utf-8') as f:
                f.write(f"IPL {year} - Match {match_num}\n")
                f.write(f"Teams: {' vs '.join(teams)}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                f.write(commentary)
                f.write("\n\n" + "="*80 + "\n")
            print(f"[DEBUG] Generated new commentary and saved to {commentary_file}")
        
        # Step 3: Generate audio
        audio_filename = f"{match_folder}/commentary.mp3"
        
        if os.path.exists(audio_filename):
            generation_status[job_id]["status"] = "loading_audio"
            generation_status[job_id]["progress"] = 40
            generation_status[job_id]["message"] = "Using existing audio file..."
            audio_path = audio_filename
            print(f"[DEBUG] Using existing audio from {audio_filename}")
        else:
            generation_status[job_id]["status"] = "generating_audio"
            generation_status[job_id]["progress"] = 40
            generation_status[job_id]["message"] = "Converting to speech..."
            
            cleaned_text = clean_commentary_text(commentary)
            audio_path = text_to_speech_file(cleaned_text, audio_filename)
            print(f"[DEBUG] Generated new audio and saved to {audio_filename}")
        
        # Step 4: Upload audio (only if we need to generate video)
        video_path = f"{match_folder}/video.mp4"
        video_url_file = f"{match_folder}/video_url.txt"
        
        if os.path.exists(video_path):
            generation_status[job_id]["status"] = "loading_video"
            generation_status[job_id]["progress"] = 80
            generation_status[job_id]["message"] = "Using existing video file..."
            
            # Try to read video URL from file
            video_url = None
            if os.path.exists(video_url_file):
                with open(video_url_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith("Video URL:"):
                            video_url = line.replace("Video URL:", "").strip()
                            break
            
            print(f"[DEBUG] Using existing video from {video_path}")
        else:
            # Need to generate video - upload audio first
            generation_status[job_id]["status"] = "uploading_audio"
            generation_status[job_id]["progress"] = 60
            generation_status[job_id]["message"] = "Uploading audio to HeyGen..."
            
            audio_url = upload_audio_file(API_KEY, audio_path)
            
            if not audio_url:
                raise Exception("Failed to upload audio to HeyGen")
            
            # Step 5: Generate video
            generation_status[job_id]["status"] = "generating_video"
            generation_status[job_id]["progress"] = 70
            generation_status[job_id]["message"] = "Generating AI video (this may take a few minutes)..."
            
            video_title = f"IPL {year} - Match {match_num} - {' vs '.join(teams)}"
            
            # Generate video with webhook URL if available
            video_id = generate_video(API_KEY, DEFAULT_AVATAR_ID, audio_url, video_title, WEBHOOK_URL)
            
            if not video_id:
                raise Exception("Failed to start video generation")
            
            # Step 6: Wait for video completion (webhook first, then polling as fallback)
            generation_status[job_id]["status"] = "processing_video"
            generation_status[job_id]["progress"] = 80
            generation_status[job_id]["message"] = "Waiting for HeyGen video generation (this can take 3-10 minutes via webhook)..."
            
            # Create a status callback to update progress during webhook wait
            def update_webhook_status(message):
                generation_status[job_id]["message"] = message
            
            video_url = wait_for_video_with_webhook_fallback(
                API_KEY, video_id, WEBHOOK_URL, 
                status_callback=update_webhook_status
            )
            
            if not video_url:
                raise Exception("Video generation failed or timed out")
            
            # Save video URL
            with open(video_url_file, 'w') as f:
                f.write(f"Video URL: {video_url}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Step 7: Download video
            generation_status[job_id]["status"] = "downloading_video"
            generation_status[job_id]["progress"] = 85
            generation_status[job_id]["message"] = "Downloading video..."
            
            import requests
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"[DEBUG] Downloaded video to {video_path}")
            else:
                raise Exception(f"Failed to download video: HTTP {response.status_code}")
        
        # Step 8: Generate scoreboards
        scoreboard1_path = f"{match_folder}/scoreboard_inning1.png"
        scoreboard2_path = f"{match_folder}/scoreboard_inning2.png"
        final_video_file = f"{match_folder}/final_video_with_scoreboards.mp4"
        
        # Check if we need scoreboards (only if final video doesn't exist)
        need_scoreboards = not os.path.exists(final_video_file) and not (os.path.exists(scoreboard1_path) and os.path.exists(scoreboard2_path))
        
        if need_scoreboards:
            generation_status[job_id]["status"] = "generating_scoreboards"
            generation_status[job_id]["progress"] = 90
            generation_status[job_id]["message"] = "Generating scoreboard images..."
            
            try:
                generate_scoreboards_sync(match_folder)
                generation_status[job_id]["message"] = "Scoreboards generated successfully!"
                print(f"[DEBUG] Generated new scoreboards in {match_folder}")
            except Exception as scoreboard_error:
                # Continue even if scoreboards fail
                generation_status[job_id]["message"] = f"Warning: Scoreboard generation failed: {scoreboard_error}"
                print(f"Scoreboard generation error: {scoreboard_error}")
        else:
            if os.path.exists(scoreboard1_path) and os.path.exists(scoreboard2_path):
                generation_status[job_id]["status"] = "loading_scoreboards"
                generation_status[job_id]["progress"] = 90
                generation_status[job_id]["message"] = "Using existing scoreboard images..."
                print(f"[DEBUG] Using existing scoreboards from {match_folder}")
        
        # Step 9: Combine video with scoreboards
        # Always check if final video needs to be created
        if os.path.exists(final_video_file):
            generation_status[job_id]["status"] = "loading_final_video"
            generation_status[job_id]["progress"] = 95
            generation_status[job_id]["message"] = "Using existing final video..."
            generation_status[job_id]["final_video"] = final_video_file
            print(f"[DEBUG] Using existing final video from {final_video_file}")
        else:
            # Check if we have the required files to create final video
            if not os.path.exists(video_path):
                raise Exception("Cannot create final video: base video.mp4 not found")
                
            generation_status[job_id]["status"] = "combining_video"
            generation_status[job_id]["progress"] = 95
            generation_status[job_id]["message"] = "Creating final video with scoreboards..."
            
            try:
                final_video_path = combine_video_with_scoreboards(
                    match_folder,
                    video_before_scoreboard=6,
                    scoreboard_duration=5,
                    fade_duration=1.0
                )
                if final_video_path:
                    generation_status[job_id]["message"] = "Final video created successfully!"
                    generation_status[job_id]["final_video"] = final_video_path
                    print(f"[DEBUG] Generated final video: {final_video_path}")
                else:
                    generation_status[job_id]["message"] = "Warning: Could not create final video with scoreboards"
            except Exception as combine_error:
                # Continue even if combining fails
                generation_status[job_id]["message"] = f"Warning: Video combining failed: {combine_error}"
                print(f"Video combining error: {combine_error}")
        
        # Complete
        generation_status[job_id]["status"] = "complete"
        generation_status[job_id]["progress"] = 100
        generation_status[job_id]["message"] = "Complete! Highlight video with scoreboards generated successfully!"
        # Set video_url to local download endpoint instead of HeyGen URL
        generation_status[job_id]["video_url"] = f"/api/download/{job_id}"
        generation_status[job_id]["match_folder"] = match_folder
        
    except Exception as e:
        generation_status[job_id]["status"] = "error"
        generation_status[job_id]["message"] = str(e)
        generation_status[job_id]["error"] = str(e)

@app.route('/')
def index():
    """Render the main page."""
    years = get_available_years()
    return render_template('index.html', years=years)

@app.route('/api/matches/<year>')
def get_matches(year):
    """Get matches for a specific year."""
    try:
        matches = load_matches(year)
        
        # Format matches for dropdown
        match_list = []
        for idx, match in enumerate(matches, 1):
            teams = match.get('teams', [])
            team_info = " vs ".join(teams) if teams else "Unknown teams"
            match_list.append({
                "number": idx,
                "label": f"Match {idx}: {team_info}",
                "teams": teams
            })
        
        return jsonify({"matches": match_list})
    except Exception as e:
        return jsonify({"error": str(e), "matches": []}), 500

@app.route('/api/generate', methods=['POST'])
def generate_highlight():
    """Start generating a highlight video."""
    try:
        data = request.json
        year = data.get('year')
        match_num = data.get('match_number')
        
        if not year or not match_num:
            return jsonify({"error": "Year and match number required"}), 400
        
        # Load match data
        matches = load_matches(year)
        if not matches or match_num < 1 or match_num > len(matches):
            return jsonify({"error": "Invalid match number"}), 400
        
        match_data = matches[match_num - 1]
        
        # Check if video already exists
        job_id = f"{year}_{match_num}"
        teams = match_data.get('teams', ['Unknown', 'Unknown'])
        team_names = "_vs_".join(teams)
        match_folder = f"commentaries/{year}/match_{match_num}_{team_names}"
        
        final_video = f"{match_folder}/final_video_with_scoreboards.mp4"
        regular_video = f"{match_folder}/video.mp4"
        
        # Only skip if final video exists (not just regular video)
        if os.path.exists(final_video):
            # Final video already exists, return it immediately
            generation_status[job_id] = {
                "status": "complete",
                "progress": 100,
                "message": "Final video already exists!",
                "video_url": f"/api/download/{job_id}",
                "match_folder": match_folder
            }
            return jsonify({"job_id": job_id, "status": "already_exists", "message": "Final video already exists!"})
        
        # If only regular video exists but not final video, we'll regenerate scoreboards and final video
        
        # Initialize status BEFORE starting thread to avoid race condition
        generation_status[job_id] = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting generation...",
            "video_url": None,
            "error": None
        }
        
        print(f"[DEBUG] Initialized status for job {job_id}")
        
        # Start generation in background thread
        thread = threading.Thread(target=generate_highlight_async, args=(year, match_num, match_data))
        thread.daemon = True
        thread.start()
        
        print(f"[DEBUG] Started background thread for job {job_id}")
        
        return jsonify({"job_id": job_id, "status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get generation status."""
    print(f"[DEBUG] Status requested for job {job_id}")
    print(f"[DEBUG] Current jobs in status: {list(generation_status.keys())}")
    
    if job_id in generation_status:
        return jsonify(generation_status[job_id])
    else:
        # Check if video already exists from a previous generation
        try:
            year, match_num = job_id.split('_')
            matches = load_matches(year)
            if matches and int(match_num) <= len(matches):
                match_data = matches[int(match_num) - 1]
                teams = match_data.get('teams', ['Unknown', 'Unknown'])
                team_names = "_vs_".join(teams)
                match_folder = f"commentaries/{year}/match_{match_num}_{team_names}"
                
                # Check if final video exists (not just regular video)
                final_video = f"{match_folder}/final_video_with_scoreboards.mp4"
                
                if os.path.exists(final_video):
                    # Return completed status for existing final video
                    return jsonify({
                        "status": "complete",
                        "progress": 100,
                        "message": "Final video already exists!",
                        "video_url": f"/api/download/{job_id}",
                        "match_folder": match_folder
                    })
        except Exception as e:
            print(f"Error checking existing video: {e}")
        
        return jsonify({"error": "Job not found"}), 404

@app.route('/api/download/<job_id>')
def download_video(job_id):
    """Download the final video."""
    if job_id not in generation_status:
        return jsonify({"error": "Job not found"}), 404
    
    status = generation_status[job_id]
    
    if status.get("status") != "complete":
        return jsonify({"error": "Video not ready yet"}), 400
    
    match_folder = status.get("match_folder")
    if not match_folder:
        return jsonify({"error": "Match folder not found"}), 404
    
    # Try final video first, fallback to regular video
    final_video = f"{match_folder}/final_video_with_scoreboards.mp4"
    regular_video = f"{match_folder}/video.mp4"
    
    if os.path.exists(final_video):
        return send_file(final_video, mimetype='video/mp4', as_attachment=False, download_name=f"ipl_highlight_{job_id}.mp4")
    elif os.path.exists(regular_video):
        return send_file(regular_video, mimetype='video/mp4', as_attachment=False, download_name=f"ipl_highlight_{job_id}.mp4")
    else:
        return jsonify({"error": "Video file not found"}), 404

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('commentaries', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*80)
    print("🎬 IPL HIGHLIGHT GENERATOR - WEB INTERFACE")
    print("="*80)
    print("\n🌐 Starting web server...")
    print("   Open your browser and go to: http://localhost:5200")
    print("\n   Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5200)
