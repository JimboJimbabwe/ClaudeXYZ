import requests
import json
from pathlib import Path
import pygame
import time
from typing import Optional


class TextToSpeech:
    def __init__(self):
        self.CHUNK_SIZE = 1024
        self.XI_API_KEY = ""  # You'll add this later
        self.VOICE_ID = ""  # You'll add this later
        self.INPUT_FILE = "ClaudeFinal.txt"  # Read from this file
        self.OUTPUT_PATH = "output.mp3"

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

    def read_input_text(self) -> Optional[str]:
        """Read text from input file"""
        try:
            with open(self.INPUT_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading input file: {e}")
            return None

    def convert_to_speech(self) -> bool:
        """Convert text to speech using ElevenLabs API"""
        # Read input text
        text_to_speak = self.read_input_text()
        if not text_to_speak:
            return False

        # API endpoint
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.VOICE_ID}/stream"

        # Headers and data payload
        headers = {
            "Accept": "application/json",
            "xi-api-key": self.XI_API_KEY
        }

        data = {
            "text": text_to_speak,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        try:
            # Make API request
            response = requests.post(tts_url, headers=headers, json=data, stream=True)

            if response.ok:
                # Save audio stream
                with open(self.OUTPUT_PATH, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                        f.write(chunk)
                print("Audio stream saved successfully.")
                return True
            else:
                print(f"Error from API: {response.text}")
                return False

        except Exception as e:
            print(f"Error during conversion: {e}")
            return False

    def play_audio(self):
        """Play the generated audio file"""
        try:
            if Path(self.OUTPUT_PATH).exists():
                print("Playing audio...")
                pygame.mixer.music.load(self.OUTPUT_PATH)
                pygame.mixer.music.play()

                # Wait for the audio to finish playing
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                pygame.mixer.music.unload()
                print("Audio playback completed.")
            else:
                print("Audio file not found.")
        except Exception as e:
            print(f"Error playing audio: {e}")


def main():
    tts = TextToSpeech()

    print(f"Reading text from {tts.INPUT_FILE}...")
    if tts.convert_to_speech():
        print(f"Successfully converted text to speech. Saved as {tts.OUTPUT_PATH}")
        tts.play_audio()
    else:
        print("Failed to convert text to speech.")


if __name__ == "__main__":
    main()