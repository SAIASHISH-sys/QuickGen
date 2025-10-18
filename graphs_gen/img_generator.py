"""
Image Generator - Generate scoreboard images using pyppeteer
"""
import json
import os
import asyncio
from pathlib import Path
from pyppeteer import launch
from data_processor import extract_scoreboard_data


async def capture_scoreboard_image(scoreboard_data, output_path, html_template_path):
    """
    Generate a scoreboard image using pyppeteer.
    
    Args:
        scoreboard_data: Dictionary containing scoreboard information
        output_path: Path where the PNG image should be saved
        html_template_path: Path to the HTML template file
    """
    browser = None
    try:
        # Read the HTML template
        with open(html_template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject the scoreboard data into the HTML
        scoreboard_json = json.dumps(scoreboard_data, indent=2)
        injection_script = f"""
        <script>
            // Injected scoreboard data
            const scoreboardData = {scoreboard_json};
            console.log('Scoreboard data loaded:', scoreboardData);
            
            // Execute immediately when DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', () => {{
                    console.log('DOM loaded, rendering scoreboard');
                    renderScoreboard(scoreboardData);
                }});
            }} else {{
                console.log('DOM already loaded, rendering scoreboard immediately');
                renderScoreboard(scoreboardData);
            }}
        </script>
        """
        
        # Insert before closing body tag
        html_content = html_content.replace('</body>', f'{injection_script}</body>')
        
        # Launch browser
        browser = await launch(
            headless=True,
            handleSIGINT=False,  # Don't handle signals (fixes thread issue)
            handleSIGTERM=False,
            handleSIGHUP=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # Set content directly
        await page.setContent(html_content)
        
        # Wait for the page to load
        await asyncio.sleep(1)
        
        # Execute the renderScoreboard function directly with the data
        scoreboard_json_str = json.dumps(scoreboard_data)
        await page.evaluate(f'''() => {{
            const data = {scoreboard_json_str};
            console.log('Calling renderScoreboard with:', data);
            renderScoreboard(data);
        }}''')
        
        # Wait a bit more for rendering to complete
        await asyncio.sleep(1)
        
        # Take screenshot - use a specific element or fullPage
        await page.screenshot({'path': output_path, 'fullPage': True})
        
        print(f"✓ Generated: {output_path}")
        
    except Exception as e:
        print(f"❌ Error capturing scoreboard: {e}")
    finally:
        if browser:
            await browser.close()


async def generate_scoreboards_for_match(match_folder_path):
    """
    Generate scoreboard images for a match.
    
    Args:
        match_folder_path: Path to the match folder containing match_data.json
        
    Returns:
        List of generated image paths
    """
    match_folder = Path(match_folder_path)
    
    # Check if match_data.json exists
    match_data_file = match_folder / "match_data.json"
    if not match_data_file.exists():
        print(f"❌ match_data.json not found in {match_folder}")
        return []
    
    # Load match data
    with open(match_data_file, 'r', encoding='utf-8') as f:
        match_data = json.load(f)
    
    print(f"📊 Generating scoreboards for {match_folder.name}...")
    
    # Extract scoreboard data
    scoreboards = extract_scoreboard_data(match_data)
    
    if not scoreboards:
        print("❌ No innings data found in match_data.json")
        return []
    
    # Get HTML template path
    script_dir = Path(__file__).parent
    html_template = script_dir / "scoreboard_processor.html"
    
    if not html_template.exists():
        print(f"❌ HTML template not found: {html_template}")
        return []
    
    # Generate images for each innings
    generated_paths = []
    for idx, scoreboard in enumerate(scoreboards, 1):
        output_path = match_folder / f"scoreboard_inning{idx}.png"
        team_name = scoreboard.get('name', f'Inning {idx}')
        
        print(f"  Generating scoreboard for {team_name}...")
        await capture_scoreboard_image(scoreboard, str(output_path), str(html_template))
        generated_paths.append(str(output_path))
    
    print(f"✅ Generated {len(scoreboards)} scoreboard image(s)")
    return generated_paths


def generate_scoreboards_sync(match_folder_path):
    """
    Synchronous wrapper for generating scoreboards.
    Thread-safe version that works from background threads.
    
    Args:
        match_folder_path: Path to the match folder containing match_data.json
        
    Returns:
        List of generated image paths
    """
    import threading
    
    # Check if we're in the main thread
    is_main_thread = threading.current_thread() is threading.main_thread()
    current_thread_name = threading.current_thread().name
    
    print(f"[SCOREBOARD] Running in thread: {current_thread_name} (main={is_main_thread})")
    
    if is_main_thread:
        # We're in main thread, can use asyncio.run() normally
        return asyncio.run(generate_scoreboards_for_match(match_folder_path))
    else:
        # We're in a background thread, need to create a new event loop
        print("[SCOREBOARD] Creating new event loop for background thread...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(generate_scoreboards_for_match(match_folder_path))
            return result
        finally:
            loop.close()
            asyncio.set_event_loop(None)

async def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) > 1:
        match_folder = sys.argv[1]
    else:
        match_folder = "../commentaries/match_22_KXIP_vs_KKR"
    
    if not os.path.exists(match_folder):
        print(f"❌ Folder not found: {match_folder}")
        return
    
    generated_images = await generate_scoreboards_for_match(match_folder)
    print(f"\n📁 Generated images:")
    for img in generated_images:
        print(f"   {img}")
    return



    generated_images = await generate_scoreboards_for_match(json_file)
    print(f"All scoreboards generated: {generated_images}")

if __name__ == "__main__":
    asyncio.run(main())