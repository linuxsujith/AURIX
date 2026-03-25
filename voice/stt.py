"""
AURIX Speech-to-Text Engine — Using OpenAI Whisper (offline).
"""

import asyncio
import tempfile
import wave
import os
import numpy as np
from typing import Optional


class SpeechToText:
    """Offline speech-to-text using OpenAI Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self._loaded = False

    def _ensure_loaded(self):
        """Lazy load Whisper model."""
        if self._loaded:
            return
        try:
            import whisper
            self.model = whisper.load_model(self.model_size)
            self._loaded = True
            print(f"[STT] Whisper model '{self.model_size}' loaded")
        except Exception as e:
            print(f"[STT] Failed to load Whisper: {e}")

    async def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Transcribe audio bytes to text."""
        self._ensure_loaded()
        if not self._loaded:
            return ""

        # Save audio to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
            with wave.open(f, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(audio_data)

        try:
            # Run whisper in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(temp_path, language="en")
            )
            return result.get("text", "").strip()
        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            return ""
        finally:
            os.unlink(temp_path)

    async def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file to text."""
        self._ensure_loaded()
        if not self._loaded:
            return ""

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(file_path, language="en")
            )
            return result.get("text", "").strip()
        except Exception as e:
            print(f"[STT] File transcription error: {e}")
            return ""

    def is_available(self) -> bool:
        """Check if STT is available."""
        try:
            import whisper
            return True
        except ImportError:
            return False
