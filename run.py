"""
AURIX — Main Entry Point
"""

import sys
import os
import uvicorn
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = str(Path(__file__).parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import get_settings


def main():
    """Start the AURIX system."""
    settings = get_settings()

    print(r"""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║      █████╗ ██╗   ██╗██████╗ ██╗██╗  ██╗       ║
    ║     ██╔══██╗██║   ██║██╔══██╗██║╚██╗██╔╝       ║
    ║     ███████║██║   ██║██████╔╝██║ ╚███╔╝        ║
    ║     ██╔══██║██║   ██║██╔══██╗██║ ██╔██╗        ║
    ║     ██║  ██║╚██████╔╝██║  ██║██║██╔╝ ██╗       ║
    ║     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝       ║
    ║                                                  ║
    ║      Next-Generation AI Assistant v1.0           ║
    ║      "Your Intelligence, Amplified"              ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)

    print(f"  🧠 AI Model: {settings.ai.model}")
    print(f"  🗣️  Voice: {settings.voice.mode}")
    print(f"  🌐 Search: {'Enabled' if settings.search.serpapi_key else 'Disabled'}")
    print(f"  🧩 Memory: ChromaDB @ {settings.memory.chromadb_path}")
    print(f"  👁️  Face Recognition: {'Enabled' if settings.vision.face_recognition_enabled else 'Disabled'}")
    print(f"  🎨 Image Gen: {'Enabled' if settings.image_gen.api_key else 'Disabled'}")
    print(f"  🖥️  Server: http://{settings.server.host}:{settings.server.port}")
    print()
    print("  Starting AURIX server...")
    print("  ─────────────────────────────────────────────")
    print()

    # Create data directories
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "chromadb"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "faces"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "logs"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "generated_images"), exist_ok=True)

    uvicorn.run(
        "api.server:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
