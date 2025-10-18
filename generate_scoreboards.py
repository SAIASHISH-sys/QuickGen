"""
Generate Scoreboards - Wrapper script to generate scoreboard images for a match
Usage: python generate_scoreboards.py <match_folder_path>
Example: python generate_scoreboards.py commentaries/match_22_KXIP_vs_KKR
"""
import sys
import os
from pathlib import Path

# Add graphs_gen to Python path
sys.path.insert(0, str(Path(__file__).parent / "graphs_gen"))

from img_generator import generate_scoreboards_sync


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_scoreboards.py <match_folder_path>")
        print("\nExample:")
        print("  python generate_scoreboards.py commentaries/match_22_KXIP_vs_KKR")
        sys.exit(1)
    
    match_folder = sys.argv[1]
    
    if not os.path.exists(match_folder):
        print(f"❌ Folder not found: {match_folder}")
        sys.exit(1)
    
    # Check if match_data.json exists
    match_data_file = Path(match_folder) / "match_data.json"
    if not match_data_file.exists():
        print(f"❌ match_data.json not found in {match_folder}")
        sys.exit(1)
    
    print(f"🎯 Generating scoreboards for {match_folder}...\n")
    
    generated_images = generate_scoreboards_sync(match_folder)
    
    if generated_images:
        print(f"\n✅ Success! Generated {len(generated_images)} scoreboard image(s)")
        print("\n📁 Files created:")
        for img in generated_images:
            print(f"   {img}")
    else:
        print("\n❌ Failed to generate scoreboard images")
        sys.exit(1)


if __name__ == "__main__":
    main()
