#!/usr/bin/env python3
"""
Quick test script to verify all modules are working correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("TESTING IPL COMMENTARY SYSTEM")
print("="*80 + "\n")

# Test 1: Check environment variables
print("Test 1: Checking environment variables...")
api_keys = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
    "HEYGEN_API_KEY": os.getenv("HEYGEN_API_KEY")
}

for key, value in api_keys.items():
    if value:
        print(f"  ✅ {key}: Found (length: {len(value)})")
    else:
        print(f"  ❌ {key}: Not found")

# Test 2: Check required modules
print("\nTest 2: Checking Python modules...")
modules_to_test = [
    ("dotenv", "python-dotenv"),
    ("langchain_google_genai", "langchain-google-genai"),
    ("langchain_core", "langchain-core"),
    ("elevenlabs", "elevenlabs"),
    ("requests", "requests"),
]

missing_modules = []
for module, package in modules_to_test:
    try:
        __import__(module)
        print(f"  ✅ {module}: Installed")
    except ImportError:
        print(f"  ❌ {module}: Not installed (pip install {package})")
        missing_modules.append(package)

# Test 3: Check data files
print("\nTest 3: Checking data files...")
data_dir = "data"
if os.path.exists(data_dir):
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    print(f"  ✅ Found {len(json_files)} JSON files in {data_dir}/")
    for f in json_files[:5]:  # Show first 5
        print(f"     - {f}")
    if len(json_files) > 5:
        print(f"     ... and {len(json_files) - 5} more")
else:
    print(f"  ❌ {data_dir}/ directory not found")

# Test 4: Check output directories
print("\nTest 4: Checking output directories...")
for dir_name in ["commentaries", "videos"]:
    if os.path.exists(dir_name):
        files = os.listdir(dir_name)
        print(f"  ✅ {dir_name}/: {len(files)} files")
    else:
        print(f"  ℹ️  {dir_name}/: Will be created on first use")

# Test 5: Try importing local modules
print("\nTest 5: Checking local modules...")
local_modules = ["commentary", "texttospeech", "aivideo", "match_selector"]
for module in local_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}.py: OK")
    except Exception as e:
        print(f"  ❌ {module}.py: Error - {str(e)[:50]}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80 + "\n")

all_good = True

if not all(api_keys.values()):
    print("⚠️  Some API keys are missing. Add them to .env file:")
    for key, value in api_keys.items():
        if not value:
            print(f"   {key}=your_key_here")
    all_good = False

if missing_modules:
    print("\n⚠️  Some Python modules are missing. Install them with:")
    print(f"   pip install {' '.join(missing_modules)}")
    all_good = False

if all_good:
    print("✅ All checks passed! You're ready to run:")
    print("   python3 match_selector.py")
    print("   or")
    print("   python3 aivideo.py")
else:
    print("\n❌ Please fix the issues above before running the main scripts.")

print("\n" + "="*80 + "\n")
