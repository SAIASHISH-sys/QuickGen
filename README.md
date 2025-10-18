# 🎬 IPL AI Highlight Generator

An AI-powered web application that automatically generates professional cricket commentary highlights with AI avatars, dynamic scoreboards, and smooth transitions from IPL match data. Uses Google Gemini for commentary generation, ElevenLabs for text-to-speech, HeyGen for AI avatar videos, and FFmpeg for professional video production.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🤖 **AI Commentary Generation**: Uses Google Gemini 2.0 Flash to create engaging cricket commentary
- 🎙️ **Text-to-Speech**: Converts commentary to natural-sounding audio with ElevenLabs
- 👤 **AI Avatar Videos**: Creates professional video highlights with HeyGen avatars (720x1280)
- 📊 **Dynamic Scoreboards**: Auto-generates beautiful scoreboard graphics for both innings
- 🎬 **Professional Video Editing**: Combines avatar video with scoreboards using smooth fade transitions
- 🌐 **Web Interface**: Clean, intuitive interface for easy highlight generation
- � **Multi-Year Support**: Browse IPL matches from 2008 to 2025
- 🔄 **Webhook Support**: Fast video generation with webhook notifications (polling fallback available)
- 💾 **Smart Caching**: Automatically reuses existing files to save time and API credits
- 📁 **Organized Storage**: All outputs saved in year/match-specific folders
- ⚡ **Thread-Safe**: Handles concurrent requests and background processing

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- FFmpeg (for video processing)
- Chromium/Chrome (installed automatically by pyppeteer)
- API Keys for:
  - [Google AI Studio](https://aistudio.google.com/) (Gemini API)
  - [ElevenLabs](https://elevenlabs.io/)
  - [HeyGen](https://heygen.com/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd task3
   ```

2. **Install FFmpeg** (required for video processing)
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Required API Keys
   GOOGLE_API_KEY=your_google_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   HEYGEN_API_KEY=your_heygen_api_key_here
   
   # Optional: Video Configuration
   VIDEO_WIDTH=720
   VIDEO_HEIGHT=1280
   USE_TEST_MODE=true
   
   # Optional: Webhook Configuration (for faster video generation)
   WEBHOOK_URL=your_ngrok_url/webhook
   WEBHOOK_PORT=5000
   ```

5. **Run the application**
   ```bash
   python3 web_app.py
   ```

6. **Open your browser**
   
   Navigate to: `http://localhost:5200`
   
   *Note: Port can be changed in `web_app.py` if needed*

## 📖 Usage

### Web Interface

1. **Select Year**: Choose an IPL season from the dropdown (2008-2025)
2. **Select Match**: Pick a match from the available matches
3. **Generate Highlight**: Click the button and watch the magic happen!
4. **Monitor Progress**: Watch real-time progress updates through all 9 steps:
   - AI commentary generation
   - Text-to-speech conversion
   - Audio upload to HeyGen
   - AI avatar video generation (3-10 minutes)
   - Video download
   - Scoreboard generation
   - Final video production with transitions
5. **View & Download**: The final professional video appears with a download button

**Processing Time**: 3-10 minutes depending on server load (mostly waiting for HeyGen video generation)

**Smart Caching**: If you regenerate the same match, existing files are reused automatically, reducing wait time to seconds!

### Command Line Interface

For advanced users, you can use the command-line version:

```bash
python3 match_selector.py
```

This provides an interactive terminal interface with the same functionality.

## 📂 Project Structure

```
task3/
├── web_app.py                  # Flask web application
├── match_selector.py           # CLI version of the app
├── commentary.py               # AI commentary generation (Gemini)
├── texttospeech.py            # Text-to-speech conversion (ElevenLabs)
├── aivideo.py                 # AI video generation (HeyGen) + webhook handling
├── video_combining.py         # Video production with FFmpeg
├── generate_scoreboards.py    # Scoreboard image generator
├── webhook_server.py          # Standalone webhook server
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .gitignore                # Git ignore rules
├── README.md                  # This file
├── data/                      # IPL match data (JSON files)
│   ├── ipl_2008.json
│   ├── ipl_2009.json
│   └── ... (2008-2025)
├── graphs_gen/                # Scoreboard generation module
│   ├── data_processor.py      # Extract scoreboard data from match JSON
│   ├── img_generator.py       # Generate PNG scoreboards using pyppeteer
│   ├── scoreboard_processor.html  # HTML template for scoreboards
│   └── __pycache__/
├── templates/                 # HTML templates
│   └── index.html            # Web interface
├── static/                    # Static assets (CSS, JS)
├── avatar_info/               # HeyGen avatar information
│   ├── available_avatars.json
│   ├── avatars_viewer.html
│   └── getavatar.py
└── commentaries/              # Generated outputs (organized by year)
    └── YEAR/
        └── match_X_TEAM1_vs_TEAM2/
            ├── match_data.json                    # Match metadata
            ├── commentary.txt                     # AI-generated commentary
            ├── commentary.mp3                     # TTS audio
            ├── video.mp4                         # HeyGen avatar video
            ├── video_url.txt                     # Video URL reference
            ├── scoreboard_inning1.png            # First innings scoreboard
            ├── scoreboard_inning2.png            # Second innings scoreboard
            └── final_video_with_scoreboards.mp4  # Final professional video
```

## 🔧 Configuration

### Video Settings

Adjust video resolution in `.env`:

```env
VIDEO_WIDTH=720    # Default: 720 (free tier compatible)
VIDEO_HEIGHT=1280  # Default: 1280 (portrait mode)
USE_TEST_MODE=true # Use test mode for faster generation
```

**Note**: HeyGen free tier supports `720x1280`. For higher resolutions like `1920x1080`, a paid plan is required.

## ⚡ Performance & Optimization

### Smart Caching System

The application automatically caches generated files to save time and API credits:

| File | Cached? | Benefit |
|------|---------|---------|
| Commentary Text | ✅ | Skip Gemini API call (~5-10s) |
| Audio MP3 | ✅ | Skip ElevenLabs API call (~10-20s) |
| AI Avatar Video | ✅ | Skip HeyGen generation (~3-10 min, 328 credits!) |
| Scoreboards | ✅ | Skip image generation (~10-15s) |
| Final Video | ✅ | Skip video combining (~30-60s) |

**How it works:**
- First run: Generates everything (5-10 minutes)
- Subsequent runs: Uses cached files (instant!)
- Partial regeneration: Only regenerates missing files

**Manual cache control:**
- Delete specific files to force regeneration
- Delete `final_video_with_scoreboards.mp4` to regenerate only the final video
- Delete all files in match folder for complete regeneration

### Processing Time Estimates

| Scenario | Time | Cost |
|----------|------|------|
| **Fresh generation** | 5-10 min | ~328 HeyGen credits + API calls |
| **Cached (complete)** | Instant | Free |
| **Only final video missing** | 30-60s | Free (just FFmpeg) |
| **Only scoreboards missing** | 10-20s | Free (just pyppeteer) |

### Webhook Configuration (Optional but Recommended)

For faster video generation, set up webhooks:

1. **Install ngrok** (if not already installed):
   ```bash
   # Download from https://ngrok.com/download
   ```

2. **Start ngrok**:
   ```bash
   ngrok http 5000
   ```

3. **Update `.env`** with the ngrok URL:
   ```env
   WEBHOOK_URL=https://your-ngrok-url.ngrok.io/webhook
   ```

4. **Run the app** - webhooks will be used automatically!

If webhook setup fails, the system automatically falls back to polling.

## 🛠️ API Information

### Google Gemini
- **Model**: `gemini-2.0-flash-exp`
- **Purpose**: Generates engaging cricket commentary
- **Get API Key**: [Google AI Studio](https://aistudio.google.com/)

### ElevenLabs
- **Voice**: Adam (`pNInz6obpgDQGcFmaJgB`)
- **Purpose**: Converts text commentary to natural speech
- **Get API Key**: [ElevenLabs](https://elevenlabs.io/)

### HeyGen
- **Avatar**: Kristin (default) or any available avatar
- **Purpose**: Creates AI avatar video with synced audio
- **Get API Key**: [HeyGen](https://heygen.com/)

## 📝 Output Files

Each generated highlight creates a folder: `commentaries/YEAR/match_X_TEAM1_vs_TEAM2/`

Contains:
- **match_data.json**: Original match data with metadata and timestamp
- **commentary.txt**: Generated AI commentary text (full text with headers)
- **commentary.mp3**: Audio file of the commentary (~1:30 minutes)
- **video.mp4**: HeyGen AI avatar video (720x1280, portrait mode)
- **video_url.txt**: HeyGen video URL for reference
- **scoreboard_inning1.png**: Dynamic scoreboard image for first innings (~100KB)
- **scoreboard_inning2.png**: Dynamic scoreboard image for second innings (~100KB)
- **final_video_with_scoreboards.mp4**: Professional final video with all elements combined

### Video Structure

The final video includes:
1. **5 seconds** of AI avatar video
2. **Fade transition** (1 second)
3. **3 seconds** of first innings scoreboard
4. **Fade transition** (1 second)
5. **5 seconds** of AI avatar video
6. **Fade transition** (1 second)
7. **3 seconds** of second innings scoreboard
8. **Fade transition** (1 second)
9. **Remaining duration** of AI avatar video

All synchronized with the full commentary audio throughout!

## 🐛 Troubleshooting

### Scoreboard generation fails with "signal only works in main thread"
- This is fixed in the current version (thread-safe event loop implementation)
- If you still see this, ensure you're running the latest version

### Video combining fails
- Verify FFmpeg is installed: `ffmpeg -version`
- Check that video.mp4 and scoreboard images exist in the match folder
- Ensure sufficient disk space for video processing

### Video generation fails
- Check your HeyGen API key
- Ensure video resolution is compatible with your plan (720x1280 for free tier)
- Verify audio file was generated successfully
- Check HeyGen account credits (~328 credits per video)

### Webhook not working
- Check ngrok is running: `ngrok http 5000`
- Verify WEBHOOK_URL in `.env` is correct
- The system will automatically fall back to polling after 10 minutes
- Check webhook server logs for incoming requests

### Audio generation fails
- Check ElevenLabs API key in `.env`
- Verify you have API credits
- Check internet connection
- Ensure commentary text was generated

### Commentary not generating
- Verify Google API key in `.env`
- Check Gemini API quota and limits
- Ensure match data JSON is valid
- Check for proper JSON structure in `data/` folder

### Port already in use
- Change the port in `web_app.py` (last line)
- Or kill the process using the port: `lsof -ti:5200 | xargs kill -9`

### "Job not found" error
- The server may have restarted, clearing in-memory status
- Existing videos can still be accessed - try regenerating
- Check the `commentaries/` folder for existing files

### Pyppeteer/Chromium issues
- Pyppeteer auto-downloads Chromium on first run
- If download fails, manually install: `pyppeteer-install`
- Check internet connection and firewall settings

## 💡 Usage Examples

### Example 1: Generate a Complete Highlight (Web Interface)

1. Start the server: `python3 web_app.py`
2. Open `http://localhost:5200`
3. Select "2010" from year dropdown
4. Select "Match 4: Royal Challengers Bangalore vs Kolkata Knight Riders"
5. Click "Generate Highlight"
6. Wait ~5-10 minutes (first time)
7. Watch and download the final video!

### Example 2: Regenerate Only Final Video

If you have `video.mp4` and want to add scoreboards:

```bash
# Delete only the final video
rm commentaries/2010/match_4_RCB_vs_KKR/final_video_with_scoreboards.mp4

# Regenerate via web interface - it will:
# - Skip commentary (cached)
# - Skip audio (cached)
# - Skip video (cached)
# - Generate scoreboards (if missing)
# - Create final video with scoreboards
# Total time: ~30-60 seconds!
```

### Example 3: CLI Usage

```bash
python3 match_selector.py
# Follow the interactive prompts
# Select year, match, and generate
```

### Example 4: Manual File Management

```bash
# View all generated matches
ls -R commentaries/

# Check file sizes
du -sh commentaries/2010/match_4_RCB_vs_KKR/*

# Delete old cache to regenerate
rm -rf commentaries/2010/match_4_RCB_vs_KKR/

# View scoreboard images
open commentaries/2010/match_4_RCB_vs_KKR/scoreboard_inning*.png
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution

- Additional video transition effects
- More scoreboard templates
- Support for other cricket leagues
- Performance optimizations
- UI/UX improvements
- Documentation enhancements

## 📄 License

This project is licensed under the MIT License.

## � Technical Details

### Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Flask 3.1.0 | Web framework |
| **AI Commentary** | Google Gemini 2.0 Flash | Text generation |
| **Text-to-Speech** | ElevenLabs API | Audio synthesis |
| **AI Avatar** | HeyGen API | Video generation |
| **Scoreboard Rendering** | Pyppeteer 2.0.0 | Headless Chrome automation |
| **Video Processing** | FFmpeg | Video editing & combining |
| **Async Processing** | Python asyncio + threading | Background tasks |
| **Webhook Server** | Flask + ngrok | Real-time notifications |

### Video Production Pipeline

```
Match Data (JSON)
    ↓
[1] Gemini AI → Commentary Text
    ↓
[2] ElevenLabs → Commentary Audio (MP3)
    ↓
[3] HeyGen → AI Avatar Video (MP4, 720x1280)
    ↓
[4] Pyppeteer → Scoreboard Images (PNG, 1920x1080)
    ↓
[5] FFmpeg → Final Video with Transitions
    ↓
Professional Highlight Video ✓
```

### Architecture Highlights

- **Thread-Safe**: Background thread for video generation, main thread for Flask
- **Event Loop Management**: Custom event loop per thread for asyncio operations
- **Signal Handling**: Disabled in pyppeteer to work in background threads
- **Webhook-First**: 10-minute webhook wait, automatic polling fallback
- **Smart Caching**: File existence checks before regeneration
- **Error Recovery**: Try-catch blocks allow partial success
- **Progress Tracking**: Real-time status updates via polling API

### Performance Optimizations

- Reuses existing files automatically
- Parallel video segment processing in FFmpeg
- Efficient frame rate matching (25fps)
- Resolution scaling with quality preservation
- Chunked file downloads for large videos
- Background threading for non-blocking UI

## �🙏 Acknowledgments

- **Google Gemini**: AI commentary generation
- **ElevenLabs**: High-quality text-to-speech
- **HeyGen**: AI avatar video generation
- **FFmpeg**: Professional video processing
- **Pyppeteer**: Headless browser automation
- **IPL Data**: Cricket match statistics

## ❓ Frequently Asked Questions

### Q: How much does it cost to generate one highlight?
**A:** Each highlight costs approximately:
- ~328 HeyGen credits (check your plan)
- Minimal Gemini API calls (usually free tier)
- Minimal ElevenLabs API calls
- FFmpeg and pyppeteer are free

### Q: Can I use my own avatar?
**A:** Yes! Modify the `DEFAULT_AVATAR_ID` in `aivideo.py`. View available avatars in `avatar_info/avatars_viewer.html`.

### Q: Why is video generation taking so long?
**A:** HeyGen video generation typically takes 3-10 minutes. This is normal and depends on HeyGen's server load. The app uses webhooks to speed this up.

### Q: Can I change the video structure (timings, transitions)?
**A:** Yes! Edit `video_combining.py` and modify the parameters:
- `video_before_scoreboard`: Duration before each scoreboard
- `scoreboard_duration`: How long to show scoreboard
- `fade_duration`: Transition fade duration

### Q: What video formats are supported?
**A:** Output is MP4 (H.264 codec, 25fps, 1920x1080). HeyGen provides 720x1280 which is scaled up.

### Q: Can I run this without a GPU?
**A:** Yes! All processing is CPU-based. FFmpeg and pyppeteer work fine without GPU.

### Q: How do I add more IPL seasons?
**A:** Add JSON files to the `data/` folder following the format of existing files (e.g., `ipl_2026.json`).

### Q: Can I use this for other sports?
**A:** Yes, with modifications! You'll need to:
1. Update match data structure
2. Modify scoreboard templates
3. Adjust commentary prompts

### Q: Why are scoreboards 1920x1080 but video is 720x1280?
**A:** Scoreboards are rendered at high resolution, then scaled to match the video. The final video is 1920x1080 with letterboxing for the 720x1280 avatar video.

### Q: Can I host this on a server?
**A:** Yes! Use `app.run(host='0.0.0.0')` and configure firewall/ports. Consider using gunicorn for production.

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues first
- Provide error logs and environment details

## 🗺️ Roadmap

- [ ] Multiple avatar support in UI
- [ ] Custom scoreboard themes
- [ ] Batch processing for multiple matches
- [ ] Video quality settings
- [ ] Export to different resolutions
- [ ] Advanced transition effects
- [ ] Social media optimized formats
- [ ] Real-time match data integration

---

**Made with ❤️ for cricket fans** | [GitHub](https://github.com/SAIASHISH-sys/Ipl_Summary_Dashboard)
