from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import glob
from datetime import datetime
from commentary import get_langchain_response
from texttospeech import text_to_speech_file, clean_commentary_text
from aivideo import (upload_audio_file, generate_video, wait_for_video_with_webhook_fallback,
                     API_KEY, DEFAULT_AVATAR_ID, WEBHOOK_URL)
import threading

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
    generation_status[job_id] = {
        "status": "starting",
        "progress": 0,
        "message": "Initializing...",
        "video_url": None,
        "error": None
    }
    
    try:
        teams = match_data.get('teams', ['Unknown', 'Unknown'])
        team_names = "_vs_".join(teams)
        match_folder = f"commentaries/match_{match_num}_{team_names}"
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
        generation_status[job_id]["status"] = "generating_commentary"
        generation_status[job_id]["progress"] = 20
        generation_status[job_id]["message"] = "Generating AI commentary..."
        
        match_json_str = json.dumps(match_data, indent=2)
        prompt = f"""Here is the match data for IPL {year} Match #{match_num}:

{match_json_str}

Please generate an exciting and detailed 1:30 minute cricket commentary summarizing this match."""
        
        commentary = get_langchain_response(prompt)
        
        # Save commentary
        commentary_file = f"{match_folder}/commentary.txt"
        with open(commentary_file, 'w', encoding='utf-8') as f:
            f.write(f"IPL {year} - Match {match_num}\n")
            f.write(f"Teams: {' vs '.join(teams)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(commentary)
            f.write("\n\n" + "="*80 + "\n")
        
        # Step 3: Generate audio
        generation_status[job_id]["status"] = "generating_audio"
        generation_status[job_id]["progress"] = 40
        generation_status[job_id]["message"] = "Converting to speech..."
        
        cleaned_text = clean_commentary_text(commentary)
        audio_filename = f"{match_folder}/commentary.mp3"
        audio_path = text_to_speech_file(cleaned_text, audio_filename)
        
        # Step 4: Upload audio
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
        generation_status[job_id]["message"] = "Processing video (trying webhook, will fallback to polling if needed)..."
        
        video_url = wait_for_video_with_webhook_fallback(API_KEY, video_id, WEBHOOK_URL)
        
        if not video_url:
            raise Exception("Video generation failed or timed out")
        
        # Save video URL
        with open(f"{match_folder}/video_url.txt", 'w') as f:
            f.write(f"Video URL: {video_url}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Complete
        generation_status[job_id]["status"] = "complete"
        generation_status[job_id]["progress"] = 100
        generation_status[job_id]["message"] = "Highlight video generated successfully!"
        generation_status[job_id]["video_url"] = video_url
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

@app.route('/api/generate', methods=['POST'])
def generate_highlight():
    """Start generating a highlight video."""
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
    
    # Start generation in background thread
    job_id = f"{year}_{match_num}"
    thread = threading.Thread(target=generate_highlight_async, args=(year, match_num, match_data))
    thread.daemon = True
    thread.start()
    
    return jsonify({"job_id": job_id, "status": "started"})

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get generation status."""
    if job_id in generation_status:
        return jsonify(generation_status[job_id])
    else:
        return jsonify({"error": "Job not found"}), 404

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('commentaries', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*80)
    print("🎬 IPL HIGHLIGHT GENERATOR - WEB INTERFACE")
    print("="*80)
    print("\n🌐 Starting web server...")
    print("   Open your browser and go to: http://localhost:5010")
    print("\n   Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5010)
