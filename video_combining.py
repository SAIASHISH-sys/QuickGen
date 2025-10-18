"""
Video Combiner - Combines HeyGen video, commentary audio, and scoreboard images
Creates a final video with:
1. HeyGen AI avatar video with commentary audio
2. Scoreboard images overlaid at appropriate times

Usage: python video_combining.py <match_folder_path>
Example: python video_combining.py commentaries/match_22_KXIP_vs_KKR
"""
import subprocess
import os
import json
from pathlib import Path


def get_duration(file_path):
    """Get the duration of a media file using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 0.0




def run_ffmpeg_cmd(cmd, description="Running FFmpeg command"):
    """Execute an FFmpeg command and handle errors."""
    print(f"\n{description}...")
    print(f"Command: {cmd}\n")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg Error: {result.stderr}")
        raise Exception(f"FFmpeg command failed: {cmd}")
    print(f"✓ {description} completed")
    return result


def create_scoreboard_video_clip(image_path, duration, output_path):
    """Convert a scoreboard image to a video clip."""
    cmd = (
        f'ffmpeg -y -loop 1 -i "{image_path}" -t {duration} '
        f'-c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
        f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" -r 30 "{output_path}"'
    )
    run_ffmpeg_cmd(cmd, f"Creating video clip from {Path(image_path).name}")


def combine_video_with_scoreboards(match_folder_path, video_before_scoreboard=6, scoreboard_duration=5, 
                                  fade_duration=0.5):
    """
    Combine HeyGen video with scoreboard overlays using fade transitions.
    
    Structure:
    - 5 seconds of video.mp4
    - Fade to scoreboard 1 for 3 seconds (with fade transition)
    - 5 seconds of video.mp4
    - Fade to scoreboard 2 for 3 seconds (with fade transition)
    - Rest of video.mp4
    - Commentary audio plays throughout
    
    Args:
        match_folder_path: Path to the match folder containing video.mp4, commentary.mp3, and scoreboard images
        video_before_scoreboard: Seconds of video before each scoreboard (default: 5)
        scoreboard_duration: How long to show each scoreboard (seconds, default: 4)
        fade_duration: Fade transition duration (seconds, default: 1.0)
    """
    match_folder = Path(match_folder_path)
    
    # Check if match folder exists
    if not match_folder.exists():
        print(f"❌ Match folder not found: {match_folder}")
        return None
    
    # Define file paths
    video_file = match_folder / "video.mp4"
    audio_file = match_folder / "commentary.mp3"
    scoreboard1 = match_folder / "scoreboard_inning1.png"
    scoreboard2 = match_folder / "scoreboard_inning2.png"
    
    # Check required files
    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return None
    
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        return None
    
    print(f"\n{'='*80}")
    print(f"🎬 Creating Combined Video for {match_folder.name}")
    print(f"{'='*80}\n")
    
    # Create temp directory
    temp_dir = match_folder / "temp_video_combining"
    temp_dir.mkdir(exist_ok=True)
    
    # Get video duration
    video_duration = get_duration(video_file)
    audio_duration = get_duration(audio_file)
    
    print(f"📹 Video duration: {video_duration:.2f}s")
    print(f"🎵 Audio duration: {audio_duration:.2f}s")
    
    # Check if scoreboards exist
    has_scoreboard1 = scoreboard1.exists()
    has_scoreboard2 = scoreboard2.exists()
    
    if has_scoreboard1:
        print(f"✓ Found {scoreboard1.name}")
    if has_scoreboard2:
        print(f"✓ Found {scoreboard2.name}")
    
    # Output file
    output_file = match_folder / "final_video_with_scoreboards.mp4"
    
    if not has_scoreboard1 and not has_scoreboard2:
        # No scoreboards, just combine video with audio
        print(f"\n🎵 No scoreboards found. Adding commentary audio to video...")
        cmd = (
            f'ffmpeg -y -i "{video_file}" -i "{audio_file}" '
            f'-c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 '
            f'-shortest "{output_file}"'
        )
        run_ffmpeg_cmd(cmd, "Adding audio to video")
        final_duration = get_duration(output_file)
        print(f"\n✅ Created video: {output_file} ({final_duration:.2f}s)")
        return str(output_file)
    
    print(f"\n📊 Creating video with scoreboard overlays and fade transitions...")
    
    # Create scoreboard video clips with matching frame rate
    if has_scoreboard1:
        scoreboard1_video = temp_dir / "scoreboard1_clip.mp4"
        cmd = (
            f'ffmpeg -y -loop 1 -i "{scoreboard1}" -t {scoreboard_duration} '
            f'-c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
            f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25" -r 25 "{scoreboard1_video}"'
        )
        run_ffmpeg_cmd(cmd, f"Creating video clip from {scoreboard1.name}")
    
    if has_scoreboard2:
        scoreboard2_video = temp_dir / "scoreboard2_clip.mp4"
        cmd = (
            f'ffmpeg -y -loop 1 -i "{scoreboard2}" -t {scoreboard_duration} '
            f'-c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
            f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25" -r 25 "{scoreboard2_video}"'
        )
        run_ffmpeg_cmd(cmd, f"Creating video clip from {scoreboard2.name}")
    
    # Split the main video into segments and scale them to 1920x1080
    # Segment 1: 0 to video_before_scoreboard seconds
    video_segment1 = temp_dir / "video_seg1.mp4"
    cmd = (
        f'ffmpeg -y -i "{video_file}" -ss 0 -t {video_before_scoreboard} '
        f'-vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
        f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" '
        f'-c:v libx264 -preset medium -crf 23 -c:a copy "{video_segment1}"'
    )
    run_ffmpeg_cmd(cmd, "Extracting and scaling video segment 1")
    
    # Calculate time offsets
    offset_after_sb1 = video_before_scoreboard + scoreboard_duration
    
    # Segment 2: After scoreboard1 for video_before_scoreboard seconds
    video_segment2 = temp_dir / "video_seg2.mp4"
    cmd = (
        f'ffmpeg -y -i "{video_file}" -ss {video_before_scoreboard} -t {video_before_scoreboard} '
        f'-vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
        f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" '
        f'-c:v libx264 -preset medium -crf 23 -c:a copy "{video_segment2}"'
    )
    run_ffmpeg_cmd(cmd, "Extracting and scaling video segment 2")
    
    # Segment 3: Rest of the video
    offset_after_sb2 = video_before_scoreboard + video_before_scoreboard + scoreboard_duration
    remaining_duration = video_duration - (video_before_scoreboard * 2)
    video_segment3 = temp_dir / "video_seg3.mp4"
    cmd = (
        f'ffmpeg -y -i "{video_file}" -ss {video_before_scoreboard * 2} '
        f'-vf "scale=1920:1080:force_original_aspect_ratio=decrease,'
        f'pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1" '
        f'-c:v libx264 -preset medium -crf 23 -c:a copy "{video_segment3}"'
    )
    run_ffmpeg_cmd(cmd, "Extracting and scaling video segment 3")
    
    # Now create the final video with xfade transitions
    print(f"\n🎬 Creating video with fade transitions...")
    
    # Build complex filter for xfade transitions
    # Structure: [seg1] -> fade -> [scoreboard1] -> fade -> [seg2] -> fade -> [scoreboard2] -> fade -> [seg3]
    
    filter_parts = []
    input_files = []
    
    # Add video segment 1
    input_files.append(str(video_segment1))
    current_label = "[0:v]"
    offset = 0.0
    
    if has_scoreboard1:
        # Add scoreboard 1
        input_files.append(str(scoreboard1_video))
        input_idx = len(input_files) - 1
        offset += video_before_scoreboard - fade_duration
        
        # Fade from video to scoreboard1
        filter_parts.append(
            f"{current_label}[{input_idx}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[v{input_idx}]"
        )
        current_label = f"[v{input_idx}]"
        offset += scoreboard_duration
    
    # Add video segment 2
    input_files.append(str(video_segment2))
    input_idx = len(input_files) - 1
    offset -= fade_duration
    
    filter_parts.append(
        f"{current_label}[{input_idx}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[v{input_idx}]"
    )
    current_label = f"[v{input_idx}]"
    offset += video_before_scoreboard
    
    if has_scoreboard2:
        # Add scoreboard 2
        input_files.append(str(scoreboard2_video))
        input_idx = len(input_files) - 1
        offset -= fade_duration
        
        # Fade from video to scoreboard2
        filter_parts.append(
            f"{current_label}[{input_idx}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[v{input_idx}]"
        )
        current_label = f"[v{input_idx}]"
        offset += scoreboard_duration
    
    # Add video segment 3
    input_files.append(str(video_segment3))
    input_idx = len(input_files) - 1
    offset -= fade_duration
    
    filter_parts.append(
        f"{current_label}[{input_idx}:v]xfade=transition=fade:duration={fade_duration}:offset={offset}[vout]"
    )
    
    # Build the ffmpeg command
    inputs = " ".join([f'-i "{f}"' for f in input_files])
    filter_complex = ";".join(filter_parts)
    
    final_video_no_audio = temp_dir / "final_video_no_audio.mp4"
    cmd = (
        f'ffmpeg -y {inputs} '
        f'-filter_complex "{filter_complex}" '
        f'-map "[vout]" -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p '
        f'"{final_video_no_audio}"'
    )
    run_ffmpeg_cmd(cmd, "Creating video with fade transitions")
    
    # Add commentary audio
    print(f"\n🎵 Adding commentary audio to video...")
    cmd = (
        f'ffmpeg -y -i "{final_video_no_audio}" -i "{audio_file}" '
        f'-c:v copy -c:a aac -b:a 192k -map 0:v:0 -map 1:a:0 '
        f'-shortest "{output_file}"'
    )
    run_ffmpeg_cmd(cmd, "Adding audio to video")
    
    # Cleanup temp files
    print(f"\n🧹 Cleaning up temporary files...")
    for temp_file in temp_dir.glob("*"):
        temp_file.unlink()
    temp_dir.rmdir()
    
    final_duration = get_duration(output_file)
    
    print(f"\n{'='*80}")
    print(f"✅ Successfully created combined video!")
    print(f"{'='*80}")
    print(f"📁 Output: {output_file}")
    print(f"⏱️  Duration: {final_duration:.2f}s")
    print(f"{'='*80}\n")
    
    return str(output_file)


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_combining.py <match_folder_path> [video_before_scoreboard] [scoreboard_duration] [fade_duration]")
        print("\nExample:")
        print("  python video_combining.py commentaries/match_22_KXIP_vs_KKR")
        print("\nDefault values:")
        print("  video_before_scoreboard: 5 seconds")
        print("  scoreboard_duration: 3 seconds")
        print("  fade_duration: 1.0 seconds")
        sys.exit(1)
    
    match_folder = sys.argv[1]
    video_before_scoreboard = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
    scoreboard_duration = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    fade_duration = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    
    try:
        result = combine_video_with_scoreboards(
            match_folder, 
            video_before_scoreboard=video_before_scoreboard,
            scoreboard_duration=scoreboard_duration,
            fade_duration=fade_duration
        )
        if result:
            print(f"✓ Video created successfully: {result}")
        else:
            print("❌ Failed to create video")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
