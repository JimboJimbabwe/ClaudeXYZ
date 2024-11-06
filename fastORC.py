import subprocess
import sys
import time
from pathlib import Path
import anthropic
import requests
import pygame
import asyncio
import aiofiles

class APIHandler:
    def __init__(self):
        self.claude = anthropic.Anthropic(api_key='')
        self.eleven_labs_key = ''
        self.voice_id = ""
        pygame.mixer.init()

    async def process_claude_request(self, input_file: str, sections_file: str, output_file: str, is_section_selection: bool = False) -> bool:
        """Handle Claude API requests"""
        try:
            async with aiofiles.open(input_file, 'r', encoding='utf-8') as f:
                input_content = await f.read()
            async with aiofiles.open(sections_file, 'r', encoding='utf-8') as f:
                sections_content = await f.read()

            combined_content = f"""Input Query:
{input_content}

Available Sections:
{sections_content}"""

            system_msg = (
                "You are to receive the text of the User and decide which topics would be best to query based on the list you receive. "
                "You will repeat back the numbers corresponding to your decision at hand. Each value is separated by a new line."
            ) if is_section_selection else (
                "You are to receive helpful data that is relevant to the goal at hand, which is based on the prompt you receive. "
                "You will receive a request, and then helpful data to enrich your response."
            )

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.claude.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=512,
                    system=system_msg,
                    messages=[{"role": "user", "content": [{"type": "text", "text": combined_content}]}]
                )
            )

            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(response.content[0].text)
            return True

        except Exception as e:
            print(f"Error in Claude processing: {e}")
            return False

    async def process_eleven_labs(self, input_file: str, output_file: str = "output.mp3") -> bool:
        """Handle ElevenLabs API requests and play audio"""
        try:
            async with aiofiles.open(input_file, 'r', encoding='utf-8') as f:
                text = await f.read()

            print("Making ElevenLabs API request...")
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream",
                    headers={
                        "Accept": "application/json",
                        "xi-api-key": self.eleven_labs_key
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.8,
                            "style": 0.0,
                            "use_speaker_boost": True
                        }
                    },
                    stream=True
                )
            )

            if response.ok:
                print("Saving audio stream...")
                with open(output_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)

                print("Audio saved, preparing playback...")
                # Re-initialize pygame mixer
                pygame.mixer.quit()
                pygame.mixer.init()

                # Load and play the audio
                try:
                    pygame.mixer.music.load(output_file)
                    pygame.mixer.music.play()

                    print("Playing audio...")
                    # Wait for playback to complete
                    while pygame.mixer.music.get_busy():
                        await asyncio.sleep(0.1)

                    pygame.mixer.music.unload()
                    print("Audio playback completed.")
                    return True
                except Exception as audio_error:
                    print(f"Error during audio playback: {audio_error}")
                    return False
            else:
                print(f"ElevenLabs API error: {response.status_code}")
                print(f"Error message: {response.text}")
                return False

        except Exception as e:
            print(f"Error in ElevenLabs processing: {e}")
            return False
        finally:
            # Ensure pygame mixer is properly closed
            pygame.mixer.quit()

def run_script(script_name: str) -> bool:
    """Run a Python script"""
    try:
        print(f"\n{'=' * 50}")
        print(f"Running {script_name}...")
        print(f"{'=' * 50}")

        result = subprocess.run([sys.executable, f"{script_name}.py"], check=True)
        print(f"\nSuccessfully completed {script_name}")
        return result.returncode == 0

    except Exception as e:
        print(f"\nError executing {script_name}: {e}")
        return False

async def main():
    # Initialize API handler
    api_handler = APIHandler()

    # Script sequence - no flags needed as scripts handle their own data passing
    scripts = [
        "InitialComparePasser",     # Will automatically run mdExtractForPrompt
        "integerExtract",
        "compare2PathPasser",       # Will automatically run markdownisoBatch
    ]

    print("\nStarting script execution sequence...")
    start_time = time.time()

    for i, script in enumerate(scripts, 1):
        print(f"\nStep {i}/{len(scripts)}")

        script_path = Path(f"{script}.py")
        if not script_path.exists():
            print(f"Error: {script_path} not found")
            sys.exit(1)

        success = run_script(script)

        if not success:
            print(f"\nExecution stopped at {script}")
            sys.exit(1)

        # Add small delay between scripts
        await asyncio.sleep(1)

    # Handle Claude section selection
    print("\nProcessing Claude section selection...")
    success = await api_handler.process_claude_request(
        "myInput.txt",
        "Available_sections.txt",
        "IntegerList.txt",
        is_section_selection=True
    )
    if not success:
        print("Failed at Claude section selection")
        sys.exit(1)

    # Handle final Claude response
    print("\nProcessing final Claude response...")
    success = await api_handler.process_claude_request(
        "myInput.txt",
        "SuggestedHelp.txt",
        "ClaudeFinal.txt"
    )
    if not success:
        print("Failed at final Claude response")
        sys.exit(1)

    # Handle ElevenLabs processing
    print("\nProcessing text-to-speech...")
    success = await api_handler.process_eleven_labs("ClaudeFinal.txt")
    if not success:
        print("Failed at text-to-speech conversion")
        sys.exit(1)

    await asyncio.sleep(0.5)

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "=" * 50)
    print("Execution Summary:")
    print("=" * 50)
    print(f"All steps completed successfully")
    print(f"Total execution time: {duration:.2f} seconds")
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)