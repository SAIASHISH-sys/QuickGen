#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies
echo "Installing system dependencies..."

# Note: FFmpeg and Chromium need to be installed via Render's system packages
# Add these in Render Dashboard -> Environment -> Native Dependencies
