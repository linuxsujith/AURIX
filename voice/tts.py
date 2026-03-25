"""
AURIX Text-to-Speech Engine — Using Coqui TTS (offline).
"""

import asyncio
import tempfile
import os
from typing import Optional


class TextToSpeech:
    """Offline text-to-speech using Coqui TTS."""

    def __init__(self):
        self.tts = None
        self._loaded = False
        self.output_dir = tempfile.mkdtemp(prefix="aurix_tts_")

    def _ensure_loaded(self):
        """Lazy load TTS model."""
        if self._loaded:
            return
        try:
            from TTS.api import TTS
            self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            self._loaded = True
            print("[TTS] Coqui TTS model loaded")
        except Exception as e:
            print(f"[TTS] Failed to load Coqui TTS: {e}")

    async def speak(self, text: str) -> Optional[str]:
        """Convert text to speech and return audio file path."""
        self._ensure_loaded()
        if not self._loaded:
            return None

        try:
            output_path = os.path.join(self.output_dir, f"speech_{hash(text) & 0xFFFFFF}.wav")

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.tts.tts_to_file(text=text, file_path=output_path)
            )
            return output_path
        except Exception as e:
            print(f"[TTS] Speech synthesis error: {e}")
            return None

    async def speak_and_play(self, text: str):
        """Convert text to speech and play it immediately."""
        audio_path = await self.speak(text)
        if audio_path:
            await self._play_audio(audio_path)

    async def _play_audio(self, file_path: str):
        """Play an audio file."""
        try:
            import sounddevice as sd
            import soundfile as sf

            data, samplerate = sf.read(file_path)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: sd.play(data, samplerate, blocking=True)
            )
        except Exception as e:
            # Fallback to system player
            try:
                proc = await asyncio.create_subprocess_shell(
                    f"aplay {file_path} 2>/dev/null || paplay {file_path} 2>/dev/null",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.communicate()
            except Exception:
                print(f"[TTS] Playback error: {e}")

    def is_available(self) -> bool:
        """Check if TTS is available."""
        try:
            from TTS.api import TTS
            return True
        except ImportError:
            return False

    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        try:
            shutil.rmtree(self.output_dir, ignore_errors=True)
        except Exception:
            pass
