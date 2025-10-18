#!/usr/bin/env bash
# exit on error
set -o errexit

echo "📦 Installing Python packages..."
# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Installing system dependencies..."
# Update package list
apt-get update

# Install FFmpeg for video processing
echo "Installing FFmpeg..."
apt-get install -y ffmpeg

# Install Chromium and dependencies for Pyppeteer
echo "Installing Chromium..."
apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils

# Clean up to reduce image size
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "✅ Build completed successfully!"
