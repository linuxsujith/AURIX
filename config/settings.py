"""
AURIX Configuration Management
Loads and validates all settings from .env file.
"""

import os
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class AISettings(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("NVIDIA_API_KEY", ""))
    base_url: str = Field(default_factory=lambda: os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"))
    model: str = Field(default_factory=lambda: os.getenv("NVIDIA_MODEL", "openai/gpt-oss-120b"))
    max_tokens: int = 4096
    temperature: float = 0.7


class VoiceSettings(BaseModel):
    mode: str = Field(default_factory=lambda: os.getenv("VOICE_MODE", "offline"))
    whisper_model: str = "base"
    wake_word: str = "hey aurix"
    sample_rate: int = 16000


class SearchSettings(BaseModel):
    serpapi_key: str = Field(default_factory=lambda: os.getenv("SERPAPI_KEY", ""))
    enabled: bool = True


class MemorySettings(BaseModel):
    chromadb_path: str = Field(default_factory=lambda: os.getenv("CHROMADB_PATH", "./data/chromadb"))
    collection_name: str = "aurix_memory"


class VisionSettings(BaseModel):
    face_recognition_enabled: bool = Field(
        default_factory=lambda: os.getenv("FACE_RECOGNITION_ENABLED", "true").lower() == "true"
    )
    face_data_path: str = Field(default_factory=lambda: os.getenv("FACE_DATA_PATH", "./data/faces"))


class ImageGenSettings(BaseModel):
    api_key: str = Field(default_factory=lambda: os.getenv("NVIDIA_IMAGE_API_KEY", ""))
    base_url: str = "https://integrate.api.nvidia.com/v1"


class ServerSettings(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))


class Settings(BaseModel):
    ai: AISettings = Field(default_factory=AISettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    vision: VisionSettings = Field(default_factory=VisionSettings)
    image_gen: ImageGenSettings = Field(default_factory=ImageGenSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    project_root: str = str(PROJECT_ROOT)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
