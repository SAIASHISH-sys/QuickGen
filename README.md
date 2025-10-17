# 🎬 IPL AI Highlight Generator

An AI-powered web application that automatically generates cricket commentary highlights with AI avatars from IPL match data. Uses Google Gemini for commentary generation, ElevenLabs for text-to-speech, and HeyGen for AI avatar video creation.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🤖 **AI Commentary Generation**: Uses Google Gemini to create engaging cricket commentary
- 🎙️ **Text-to-Speech**: Converts commentary to natural-sounding audio with ElevenLabs
- 👤 **AI Avatar Videos**: Creates professional video highlights with HeyGen avatars
- 🌐 **Web Interface**: Clean, intuitive interface for easy highlight generation
- 📊 **Multi-Year Support**: Browse IPL matches from 2008 to 2025
- 🔄 **Webhook Support**: Fast video generation with webhook notifications (polling fallback available)
- 📁 **Organized Storage**: All outputs saved in match-specific folders

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
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

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
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

4. **Run the application**
   ```bash
   python3 web_app.py
   ```

5. **Open your browser**
   
   Navigate to: `http://localhost:5000`

## 📖 Usage

### Web Interface

1. **Select Year**: Choose an IPL season from the dropdown (2008-2025)
2. **Select Match**: Pick a match from the available matches
3. **Generate Highlight**: Click the button and watch the magic happen!
4. **View Result**: The generated video will appear below once processing is complete

### Command Line Interface

For advanced users, you can use the command-line version:

```bash
python3 match_selector.py
```

This provides an interactive terminal interface with the same functionality.

## 📂 Project Structure

```
task3/
├── web_app.py              # Flask web application
├── match_selector.py       # CLI version of the app
├── commentary.py           # AI commentary generation (Gemini)
├── texttospeech.py         # Text-to-speech conversion (ElevenLabs)
├── aivideo.py              # AI video generation (HeyGen)
├── webhook_server.py       # Standalone webhook server
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── .gitignore             # Git ignore rules
├── data/                   # IPL match data (JSON files)
│   ├── ipl_2008.json
│   ├── ipl_2009.json
│   └── ...
├── templates/              # HTML templates
│   └── index.html
├── static/                 # Static assets (CSS, JS)
└── commentaries/           # Generated outputs
    └── match_X_TEAM1_vs_TEAM2/
        ├── match_data.json
        ├── commentary.txt
        ├── commentary.mp3
        ├── video.mp4
        └── video_url.txt
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

Each generated highlight creates a folder: `commentaries/match_X_TEAM1_vs_TEAM2/`

Contains:
- **match_data.json**: Original match data with metadata
- **commentary.txt**: Generated AI commentary text
- **commentary.mp3**: Audio file of the commentary
- **video.mp4**: Final AI avatar video
- **video_url.txt**: HeyGen video URL for reference

## 🐛 Troubleshooting

### Video generation fails
- Check your HeyGen API key
- Ensure video resolution is compatible with your plan
- Verify audio file was generated successfully

### Webhook not working
- Check ngrok is running
- Verify WEBHOOK_URL in `.env`
- The system will automatically fall back to polling

### Audio generation fails
- Check ElevenLabs API key
- Verify you have API credits
- Check internet connection

### Commentary not generating
- Verify Google API key
- Check Gemini API quota
- Ensure match data JSON is valid

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google Gemini**: AI commentary generation
- **ElevenLabs**: High-quality text-to-speech
- **HeyGen**: AI avatar video generation
- **IPL Data**: Cricket match statistics

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ for cricket fans**
