#!/usr/bin/env python3
"""
Quick Start Script for IPL Commentary AI Video Generator

This script helps you get started quickly by checking your setup
and guiding you through the first run.
"""

import os
import sys

def print_header(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80 + "\n")

def check_env_file():
    """Check if .env file exists and has required keys."""
    if not os.path.exists('.env'):
        print("❌ .env file not found!\n")
        print("Creating a template .env file for you...")
        
        with open('.env', 'w') as f:
            f.write("# API Keys\n")
            f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
            f.write("ELEVENLABS_API_KEY=your_elevenlabs_api_key_here\n")
            f.write("HEYGEN_API_KEY=your_heygen_api_key_here\n")
            f.write("\n# Webhook Configuration (Optional)\n")
            f.write("#WEBHOOK_URL=https://your-domain.com/webhook\n")
            f.write("#WEBHOOK_PORT=5000\n")
            f.write("\n# Video Resolution (Default: 720x1280 for free tier)\n")
            f.write("# Free tier: 720x1280 or 1280x720\n")
            f.write("# Paid plans: 1920x1080 or 1080x1920\n")
            f.write("VIDEO_WIDTH=720\n")
            f.write("VIDEO_HEIGHT=1280\n")
            f.write("USE_TEST_MODE=true\n")
        
        print("✅ Created .env file!")
        print("\n⚠️  IMPORTANT: Edit .env and add your API keys before continuing.\n")
        
        choice = input("Press Enter after adding your API keys, or 'q' to quit: ").strip()
        if choice.lower() == 'q':
            sys.exit(0)
        
        return False
    return True

def quick_start():
    """Quick start wizard."""
    print_header("IPL CRICKET COMMENTARY AI VIDEO GENERATOR")
    print("Welcome! This script will help you get started.\n")
    
    # Step 1: Check .env
    print("Step 1: Checking environment setup...")
    if not check_env_file():
        print("Please add your API keys to .env and run this script again.")
        return
    
    print("✅ .env file exists\n")
    
    # Step 2: Test setup
    print("Step 2: Testing dependencies...")
    choice = input("Run dependency test? (y/n) [y]: ").strip().lower()
    
    if choice != 'n':
        os.system('python3 test_setup.py')
        input("\nPress Enter to continue...")
    
    # Step 3: Choose mode
    print_header("CHOOSE YOUR MODE")
    
    print("What would you like to do?\n")
    print("1. Complete workflow (select match → generate commentary → create video)")
    print("2. Generate video from existing audio file")
    print("3. Run standalone webhook server")
    print("4. View documentation")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5) [1]: ").strip()
    
    if not choice:
        choice = '1'
    
    if choice == '1':
        print("\n🚀 Starting complete workflow...\n")
        os.system('python3 match_selector.py')
    
    elif choice == '2':
        print("\n🎬 Starting video generator...\n")
        os.system('python3 aivideo.py')
    
    elif choice == '3':
        print("\n🔔 Starting webhook server...\n")
        print("In another terminal, run: ngrok http 5000")
        print("Then use the ngrok URL when generating videos.\n")
        input("Press Enter to start the webhook server...")
        os.system('python3 webhook_server.py')
    
    elif choice == '4':
        print("\n📚 Documentation:\n")
        print("  README.md        - Main documentation")
        print("  WEBHOOK_GUIDE.md - Webhook setup guide")
        print("  WORKFLOW.md      - Complete workflow guide")
        print("\nOpen these files in your text editor or browser.")
        input("\nPress Enter to continue...")
        quick_start()
    
    elif choice == '5':
        print("\n👋 Goodbye!\n")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice. Please try again.\n")
        quick_start()

def main():
    """Main function."""
    try:
        quick_start()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
