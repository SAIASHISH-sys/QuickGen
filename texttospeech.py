
import os
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def text_to_speech_file(text: str, output_path: str = None) -> str:
    """
    Convert text to speech and save as MP3 file.
    Args:
        text: The text to convert to speech
        output_path: Optional custom path for the output file. If None, generates a unique filename.
    Returns:
        Path to the saved audio file
    """
    # Calling the text_to_speech conversion API with detailed parameters
    response = elevenlabs.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.2,
        ),
    )
    # uncomment the line below to play the audio back
    # play(response)
    # Use provided path or generate a unique file name
    if output_path is None:
        save_file_path = f"{uuid.uuid4()}.mp3"
    else:
        save_file_path = output_path
    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"🎵 Audio saved to: {save_file_path}")
    # Return the path of the saved audio file
    return save_file_path


def clean_commentary_text(commentary: str) -> str:
    """
    Clean commentary text for TTS by removing special characters and formatting.
    Args:
        commentary: Raw commentary text
    Returns:
        Cleaned text suitable for TTS
    """
    # Remove excessive newlines and whitespace
    cleaned = " ".join(commentary.split())
    # Remove markdown formatting if present
    cleaned = cleaned.replace("**", "").replace("*", "")
    # Remove special characters that might cause issues
    cleaned = cleaned.replace("—", "-").replace("–", "-")
    return cleaned

