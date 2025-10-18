import json
import os
import sys
from datetime import datetime
from pathlib import Path
from commentary import get_langchain_response
from texttospeech import text_to_speech_file, clean_commentary_text


def load_matches(json_file_path):
    """Load matches from the JSON file."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        return matches
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file_path}'.")
        return None


def display_matches(matches):
    """Display all matches with their numbers and basic info."""
    print("\n" + "="*80)
    print("IPL 2008 - MATCH LIST")
    print("="*80 + "\n")
    
    for idx, match in enumerate(matches, 1):
        teams = match.get('teams', [])
        team_info = " vs ".join(teams) if teams else "Unknown teams"
        
        print(f"Match {idx}: {team_info}")
    
    print("\n" + "="*80 + "\n")


def select_match(matches):
    """Allow user to select a match by number."""
    while True:
        try:
            choice = input(f"Enter match number (1-{len(matches)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            match_num = int(choice)
            
            if 1 <= match_num <= len(matches):
                return matches[match_num - 1], match_num
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(matches)}.")
        
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")


def generate_commentary(match_data, match_num):
    """Send match data to commentary.py and get the commentary."""
    print("\n Generating commentary...\n")
    
    # Convert match data to a formatted string for the LLM
    match_json_str = json.dumps(match_data, indent=2)
    
    # Create match-specific folder
    teams = match_data.get('teams', ['Unknown', 'Unknown'])
    team_names = "_vs_".join(teams)
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    os.makedirs(match_folder, exist_ok=True)
    
    # Save match data to JSON file
    match_data_file = f"{match_folder}/match_data.json"
    
    try:
        with open(match_data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "match_number": match_num,
                "teams": teams,
                "match_data": match_data,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
        print(f"Match data saved to: {match_data_file}\n")
    except Exception as e:
        print(f"Warning: Could not save match data: {e}\n")
    
    # Create a user-friendly prompt with the match data
    prompt = f"""Here is the match data for IPL 2008 Match #{match_num}:

{match_json_str}

Please generate an exciting and detailed 1:30 minute cricket commentary summarizing this match."""
    
    # Get commentary from the LangChain model
    commentary = get_langchain_response(prompt)
    
    return commentary


def save_commentary(commentary, match_num, teams):
    """Save commentary to a text file."""
    # Create match-specific folder
    team_names = "_vs_".join(teams) if teams else "unknown_teams"
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    os.makedirs(match_folder, exist_ok=True)
    
    # Create filename in the match folder
    filename = f"{match_folder}/commentary.txt"
    
    # Save commentary
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"IPL 2008 - Match {match_num}\n")
            f.write(f"Teams: {' vs '.join(teams)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(commentary)
            f.write("\n\n" + "="*80 + "\n")
        
        print(f"\nCommentary saved to: {filename}\n")
        return filename
    
    except Exception as e:
        print(f"\nError saving commentary: {e}\n")
        return None


def display_file_summary(match_folder):
    """Display summary of all saved files in the match folder."""
    print("\n" + "="*80)
    print(f"📁 ALL FILES SAVED IN: {match_folder}/")
    print("="*80)
    try:
        if os.path.exists(match_folder):
            files = os.listdir(match_folder)
            if files:
                for file in sorted(files):
                    file_path = os.path.join(match_folder, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        size_str = f"{size / (1024*1024):.2f} MB" if size > 1024*1024 else f"{size / 1024:.2f} KB"
                        print(f"  ✓ {file} ({size_str})")
            else:
                print("  (No files generated)")
        else:
            print("  (Folder not found)")
    except Exception as e:
        print(f"  ⚠️ Could not list files: {e}")
    print("="*80 + "\n")


def generate_audio_commentary(commentary, match_num, teams):
    """Generate audio commentary from text."""
    # Create match-specific folder
    team_names = "_vs_".join(teams) if teams else "unknown_teams"
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    os.makedirs(match_folder, exist_ok=True)
    
    # Create audio filename in the match folder
    audio_filename = f"{match_folder}/commentary.mp3"
    
    # Check if audio file already exists
    if os.path.exists(audio_filename):
        file_size = os.path.getsize(audio_filename)
        if file_size > 0:
            print(f"\n✓ Audio file already exists: {audio_filename} ({file_size / 1024:.2f} KB)")
            print("   Skipping audio generation...\n")
            return audio_filename
    
    print("\n🎵 Converting commentary to speech...\n")
    
    # Clean the commentary text for TTS
    cleaned_text = clean_commentary_text(commentary)
    
    try:
        # Generate audio file
        audio_path = text_to_speech_file(cleaned_text, audio_filename)
        print(f"\n✅ Audio commentary saved to: {audio_path}\n")
        return audio_path
    
    except Exception as e:
        print(f"\n❌ Error generating audio commentary: {e}\n")
        print("Note: Make sure ELEVENLABS_API_KEY is set in your .env file")
        return None

def generate_scoreboards(match_folder):
    """Generate scoreboard images for the match."""
    # Check if scoreboards already exist
    scoreboard1 = Path(match_folder) / "scoreboard_inning1.png"
    scoreboard2 = Path(match_folder) / "scoreboard_inning2.png"
    
    if scoreboard1.exists() or scoreboard2.exists():
        existing = []
        if scoreboard1.exists():
            size1 = scoreboard1.stat().st_size
            existing.append(f"scoreboard_inning1.png ({size1 / 1024:.2f} KB)")
        if scoreboard2.exists():
            size2 = scoreboard2.stat().st_size
            existing.append(f"scoreboard_inning2.png ({size2 / 1024:.2f} KB)")
        
        print(f"\n✓ Scoreboard(s) already exist: {', '.join(existing)}")
        print("   Skipping scoreboard generation...\n")
        return True
    
    print("\n📊 Generating scoreboard images...\n")
    
    try:
        # Add graphs_gen to Python path
        sys.path.insert(0, str(Path(__file__).parent / "graphs_gen"))
        from img_generator import generate_scoreboards_sync
        
        # Generate scoreboards
        generated_images = generate_scoreboards_sync(match_folder)
        
        if generated_images:
            print(f"\n✅ Generated {len(generated_images)} scoreboard image(s)")
            return True
        else:
            print("\n⚠️ No scoreboard images generated (match_data.json may not have innings data)")
            return False
            
    except Exception as e:
        print(f"\n❌ Error generating scoreboards: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_ai_video(audio_file, match_num, teams):
    """Generate AI video with HeyGen."""
    # Check if video already exists
    team_names = "_vs_".join(teams)
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    output_path = f"{match_folder}/video.mp4"
    
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        if file_size > 0:
            print(f"\n✓ Video file already exists: {output_path} ({file_size / (1024*1024):.2f} MB)")
            print("   Skipping video generation...\n")
            return output_path
    
    print("\n🎬 Generating AI video with HeyGen...\n")
    
    try:
        from aivideo import (upload_audio_file, generate_video, wait_for_video_with_webhook_fallback, 
                            download_video, API_KEY, DEFAULT_AVATAR_ID, WEBHOOK_URL)
        
        if not API_KEY or API_KEY == "YOUR_HEYGEN_API_KEY_HERE":
            print("❌ HEYGEN_API_KEY not found in .env file. Skipping video generation.")
            return None
        
        # Upload audio
        print("  Uploading audio to HeyGen...")
        audio_url = upload_audio_file(API_KEY, audio_file)
        
        if not audio_url:
            print("❌ Failed to upload audio")
            return None
        
        # Generate video
        video_title = f"IPL 2008 - Match {match_num} - {' vs '.join(teams)}"
        print(f"  Creating AI avatar video...")
        
        video_id = generate_video(API_KEY, DEFAULT_AVATAR_ID, audio_url, video_title, WEBHOOK_URL)
        
        if not video_id:
            print("❌ Failed to generate video")
            return None
        
        # Wait for video (webhook with polling fallback)
        print("  Waiting for video generation (this may take a few minutes)...")
        video_url = wait_for_video_with_webhook_fallback(API_KEY, video_id, WEBHOOK_URL)
        
        if not video_url:
            print("❌ Failed to get video URL")
            return None
        
        print(f"\n✅ Video generated successfully!")
        print(f"   Video URL: {video_url}\n")
        
        # Download video
        print("  Downloading video...")
        if download_video(video_url, output_path):
            print(f"✅ Video downloaded to: {output_path}")
            
            # Save video URL for reference
            try:
                with open(f"{match_folder}/video_url.txt", 'w') as f:
                    f.write(f"Video URL: {video_url}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            except Exception as e:
                print(f"⚠️ Could not save video URL: {e}")
            
            return output_path
        else:
            print("❌ Failed to download video")
            return None
            
    except ImportError as e:
        print(f"❌ Could not import aivideo module: {e}")
        return None
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()
        return None


def combine_video_with_scoreboards(match_folder):
    """Combine video with scoreboard overlays."""
    print("\n🎥 Creating final video with scoreboard overlays...\n")
    
    try:
        from video_combining import combine_video_with_scoreboards
        
        result = combine_video_with_scoreboards(
            match_folder,
            video_before_scoreboard=5,
            scoreboard_duration=3,
            fade_duration=1.0
        )
        
        if result:
            print(f"\n✅ Final video created successfully!")
            return result
        else:
            print("\n❌ Failed to create final video")
            return None
            
    except Exception as e:
        print(f"\n❌ Error combining video with scoreboards: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to run the match selector."""
    json_file = "data/ipl_2008.json"
    
    # Load matches
    print("Loading matches from IPL 2008...")
    matches = load_matches(json_file)
    
    if not matches:
        print("Failed to load matches. Exiting.")
        return
    
    print(f"Loaded {len(matches)} matches successfully!")
    
    # Display matches
    display_matches(matches)
    
    # Select a match
    selection = select_match(matches)
    
    if selection is None:
        print("Exiting. Goodbye!")
        return
    
    match_data, match_num = selection
    teams = match_data.get('teams', ['Unknown', 'Unknown'])
    
    print(f"\n Selected Match {match_num}: {' vs '.join(teams)}")
    
    # Generate commentary
    commentary = generate_commentary(match_data, match_num)
    
    # Display commentary
    print("\n" + "="*80)
    print("  MATCH COMMENTARY")
    print("="*80 + "\n")
    print(commentary)
    print("\n" + "="*80 + "\n")
    
    # Save commentary text
    save_commentary(commentary, match_num, teams)
    
    # Create match folder path
    team_names = "_vs_".join(teams)
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    
    # Step 1: Generate scoreboards automatically
    print("\n" + "="*80)
    print("STEP 1: GENERATING SCOREBOARDS")
    print("="*80)
    generate_scoreboards(match_folder)
    
    # Step 2: Generate audio commentary automatically
    print("\n" + "="*80)
    print("STEP 2: GENERATING AUDIO COMMENTARY")
    print("="*80)
    audio_file = generate_audio_commentary(commentary, match_num, teams)
    
    if not audio_file:
        print("\n⚠️ Audio generation failed. Cannot proceed with video generation.")
        display_file_summary(match_folder)
        return
    
    # Step 3: Ask if user wants to generate AI video
    print("\n" + "="*80)
    print("STEP 3: AI VIDEO GENERATION")
    print("="*80)
    video_choice = input("\nWould you like to generate AI avatar video? (y/n): ").strip().lower()
    
    video_file = None
    if video_choice == 'y':
        video_file = generate_ai_video(audio_file, match_num, teams)
        
        # Step 4: If video was generated, automatically create final video with scoreboards
        if video_file:
            print("\n" + "="*80)
            print("STEP 4: CREATING FINAL VIDEO WITH SCOREBOARDS")
            print("="*80)
            
            # Check if scoreboards exist
            scoreboard1 = Path(match_folder) / "scoreboard_inning1.png"
            scoreboard2 = Path(match_folder) / "scoreboard_inning2.png"
            
            if scoreboard1.exists() or scoreboard2.exists():
                final_video = combine_video_with_scoreboards(match_folder)
                if final_video:
                    print(f"\n🎉 Complete! Final video ready: {final_video}")
            else:
                print("\n⚠️ No scoreboards found. Final video will not include scoreboards.")
                print(f"   You can still find the avatar video at: {video_file}")
    
    # Display summary of all saved files
    display_file_summary(match_folder)
    
    # Ask if user wants to select another match
    another = input("\nWould you like to select another match? (y/n): ").strip().lower()
    if another == 'y':
        main()  # Recursive call to start over
    else:
        print("\nThank you for using the IPL Match Commentary Generator! ")

if __name__ == "__main__":
    main()
