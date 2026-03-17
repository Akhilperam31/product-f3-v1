import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SpeechService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def transcribe_audio(self, audio_content: bytes) -> str:
        """Transcribe audio bytes using Whisper (in-memory)."""
        import io
        
        # Create a file-like object in memory
        audio_file = io.BytesIO(audio_content)
        audio_file.name = "blob.webm" # Metadata for Whisper to identify format
        
        try:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        except Exception as e:
            print(f"Whisper API error: {e}")
            raise e
            
        return transcript.text

    def text_to_speech(self, text: str) -> bytes:
        """Generate speech from text and return bytes."""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        # return the raw bytes
        return response.content
