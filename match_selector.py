import json
import os
from datetime import datetime
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


def generate_audio_commentary(commentary, match_num, teams):
    """Generate audio commentary from text."""
    print("\nConverting commentary to speech...\n")
    
    # Clean the commentary text for TTS
    cleaned_text = clean_commentary_text(commentary)
    
    # Create match-specific folder
    team_names = "_vs_".join(teams) if teams else "unknown_teams"
    match_folder = f"commentaries/match_{match_num}_{team_names}"
    os.makedirs(match_folder, exist_ok=True)
    
    # Create audio filename in the match folder
    audio_filename = f"{match_folder}/commentary.mp3"
    
    try:
        # Generate audio file
        audio_path = text_to_speech_file(cleaned_text, audio_filename)
        print(f"\nAudio commentary saved to: {audio_path}\n")
        return audio_path
    
    except Exception as e:
        print(f"\n Error generating audio commentary: {e}\n")
        print("Note: Make sure ELEVENLABS_API_KEY is set in your .env file")
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
    
    # Generate audio commentary
    audio_choice = input("\nWould you like to generate audio commentary? (y/n): ").strip().lower()
    audio_file = None
    if audio_choice == 'y':
        audio_file = generate_audio_commentary(commentary, match_num, teams)
    
    # Generate AI video
    if audio_file:
        video_choice = input("\nWould you like to generate AI video with this commentary? (y/n): ").strip().lower()
        if video_choice == 'y':
            try:
                from aivideo import (upload_audio_file, generate_video, wait_for_video_with_webhook_fallback, 
                                    download_video, API_KEY, DEFAULT_AVATAR_ID, WEBHOOK_URL)
                
                if not API_KEY or API_KEY == "YOUR_HEYGEN_API_KEY_HERE":
                    print("  HEYGEN_API_KEY not found in .env file. Skipping video generation.")
                else:
                    print("\n Uploading audio to HeyGen...")
                    audio_url = upload_audio_file(API_KEY, audio_file)
                    
                    if audio_url:
                        video_title = f"IPL 2008 - Match {match_num} - {' vs '.join(teams)}"
                        print(f"\n Generating AI video...")
                        
                        # Generate video with webhook URL if available
                        video_id = generate_video(API_KEY, DEFAULT_AVATAR_ID, audio_url, video_title, WEBHOOK_URL)
                        
                        if video_id:
                            # Try webhook first, then fall back to polling
                            video_url = wait_for_video_with_webhook_fallback(API_KEY, video_id, WEBHOOK_URL)
                            
                            if video_url:
                                print(f"\n Video generated successfully!")
                                print(f" Video URL: {video_url}")
                                
                                # Ask if user wants to download
                                download_choice = input("\n Download the video? (y/n): ").strip().lower()
                                if download_choice == 'y':
                                    team_names = "_vs_".join(teams)
                                    match_folder = f"commentaries/match_{match_num}_{team_names}"
                                    os.makedirs(match_folder, exist_ok=True)
                                    output_path = f"{match_folder}/video.mp4"
                                    download_video(video_url, output_path)
                                    
                                    # Also save video URL for reference
                                    try:
                                        with open(f"{match_folder}/video_url.txt", 'w') as f:
                                            f.write(f"Video URL: {video_url}\n")
                                            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                    except Exception as e:
                                        print(f"Could not save video URL: {e}")
            except ImportError:
                print("Could not import aivideo module. Make sure aivideo.py is in the same directory.")
            except Exception as e:
                print(f"Error generating video: {e}")
    
    # Display summary of saved files
    if audio_file or video_choice == 'y':
        team_names = "_vs_".join(teams)
        match_folder = f"commentaries/match_{match_num}_{team_names}"
        print("\n" + "="*80)
        print(f"All files saved in: {match_folder}/")
        print("="*80)
        try:
            files = os.listdir(match_folder)
            for file in sorted(files):
                file_path = os.path.join(match_folder, file)
                size = os.path.getsize(file_path)
                size_str = f"{size / (1024*1024):.2f} MB" if size > 1024*1024 else f"{size / 1024:.2f} KB"
                print(f"  {file} ({size_str})")
        except Exception as e:
            print(f"   Could not list files: {e}")
        print("="*80 + "\n")
    
    # Ask if user wants to select another match
    another = input("\nWould you like to select another match? (y/n): ").strip().lower()
    if another == 'y':
        main()  # Recursive call to start over
    else:
        print("\nThank you for using the IPL Match Commentary Generator! ")

if __name__ == "__main__":
    main()
