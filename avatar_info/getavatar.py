import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.heygen.com/v2/avatars"

# Get API key from environment or use the provided one
api_key = os.getenv("HEYGEN_API_KEY", "sk_V2_hgu_kvOxarqEVeC_WLgOCMzNiYe5vC7MfVw1cDKMdJtkXqic")

headers = {
    "accept": "application/json",
    "x-api-key": api_key
}

print("🔍 Fetching available HeyGen avatars...\n")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    avatars = data.get('data', {}).get('avatars', [])
    
    print("="*100)
    print(f"FOUND {len(avatars)} AVATARS")
    print("="*100 + "\n")
    
    # Separate public and private avatars
    public_avatars = [a for a in avatars if a.get('is_public', False)]
    private_avatars = [a for a in avatars if not a.get('is_public', False)]
    
    # Display public avatars first
    if public_avatars:
        print("🌐 PUBLIC AVATARS (Free to use):")
        print("-"*100)
        for idx, avatar in enumerate(public_avatars, 1):
            avatar_id = avatar.get('avatar_id', 'N/A')
            avatar_name = avatar.get('avatar_name', 'Unnamed')
            gender = avatar.get('gender', 'N/A')
            preview_image = avatar.get('preview_image_url', 'No image')
            preview_video = avatar.get('preview_video_url', 'No video')
            
            print(f"\n{idx}. {avatar_name}")
            print(f"   ID: {avatar_id}")
            print(f"   Gender: {gender}")
            print(f"   Preview Image: {preview_image}")
            print(f"   Preview Video: {preview_video}")
            print(f"   Public: ✅ Yes")
    
    # Display private avatars
    if private_avatars:
        print("\n\n🔒 PRIVATE AVATARS (Your custom avatars):")
        print("-"*100)
        for idx, avatar in enumerate(private_avatars, 1):
            avatar_id = avatar.get('avatar_id', 'N/A')
            avatar_name = avatar.get('avatar_name', 'Unnamed')
            gender = avatar.get('gender', 'N/A')
            preview_image = avatar.get('preview_image_url', 'No image')
            preview_video = avatar.get('preview_video_url', 'No video')
            
            print(f"\n{idx}. {avatar_name}")
            print(f"   ID: {avatar_id}")
            print(f"   Gender: {gender}")
            print(f"   Preview Image: {preview_image}")
            print(f"   Preview Video: {preview_video}")
            print(f"   Public: ❌ No (Custom)")
    
    # Save to file for easy reference
    output_file = "available_avatars.json"
    with open(output_file, 'w') as f:
        json.dump(avatars, f, indent=2)
    
    print("\n" + "="*100)
    print(f"✅ Avatar list saved to: {output_file}")
    print("="*100)
    
    # Create a simple HTML viewer for images
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>HeyGen Avatars</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; text-align: center; }
        .avatar-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .avatar-card { background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .avatar-card img { width: 100%; border-radius: 5px; }
        .avatar-card h3 { margin: 10px 0 5px 0; color: #333; }
        .avatar-card p { margin: 5px 0; color: #666; font-size: 14px; }
        .badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }
        .public { background: #4CAF50; color: white; }
        .private { background: #FF9800; color: white; }
        .male { background: #2196F3; color: white; }
        .female { background: #E91E63; color: white; }
        .video-link { display: inline-block; margin-top: 10px; padding: 8px 15px; background: #673AB7; color: white; text-decoration: none; border-radius: 5px; font-size: 14px; }
        .video-link:hover { background: #512DA8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 HeyGen Available Avatars</h1>
        <p style="text-align: center; color: #666;">Total: """ + str(len(avatars)) + """ avatars</p>
        <div class="avatar-grid">
"""
    
    for avatar in avatars:
        avatar_id = avatar.get('avatar_id', 'N/A')
        avatar_name = avatar.get('avatar_name', 'Unnamed')
        gender = avatar.get('gender', 'Unknown')
        preview_image = avatar.get('preview_image_url', '')
        preview_video = avatar.get('preview_video_url', '')
        is_public = avatar.get('is_public', False)
        
        public_badge = '<span class="badge public">Public</span>' if is_public else '<span class="badge private">Custom</span>'
        gender_badge = f'<span class="badge {gender.lower()}">{gender}</span>' if gender != 'Unknown' else ''
        
        html_content += f"""
            <div class="avatar-card">
                <img src="{preview_image}" alt="{avatar_name}" onerror="this.src='https://via.placeholder.com/300x400?text=No+Preview'">
                <h3>{avatar_name}</h3>
                <p><strong>ID:</strong> <code>{avatar_id}</code></p>
                <p>{public_badge} {gender_badge}</p>
                {f'<a href="{preview_video}" class="video-link" target="_blank">▶ Preview Video</a>' if preview_video else ''}
            </div>
"""
    
    html_content += """
        </div>
    </div>
</body>
</html>
"""
    
    html_file = "avatars_viewer.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"\n📸 HTML viewer created: {html_file}")
    print(f"   Open in browser: file://{os.path.abspath(html_file)}")
    print("\nTo view avatar images, open the HTML file in your browser!")
    
    # Optionally open in browser automatically
    try:
        import webbrowser
        open_browser = input("\n🌐 Open HTML viewer in browser now? (y/n): ").strip().lower()
        if open_browser == 'y':
            webbrowser.open('file://' + os.path.abspath(html_file))
            print("✅ Opened in browser!")
    except:
        pass
    
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)