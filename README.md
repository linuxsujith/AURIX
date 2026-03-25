<img width="1031" height="316" alt="image" src="https://github.com/user-attachments/assets/457256fd-00d8-4682-8456-1a78cef15212" />




# 🤖 AURIX — Next-Generation AI Assistant(linuxsujith)

> *"Your Intelligence, Amplified"*

AURIX is a fully functional JARVIS-like AI assistant with autonomous intelligence, voice interaction, system control, and a futuristic Iron Man-style interface.

---

## ⚡ Quick Start

```bash
# 1. Navigate to AURIX
cd ~/jarvis/aurix

# 2. Run setup
chmod +x setup.sh
./setup.sh

# 3. Start AURIX
source venv/bin/activate
python run.py

# 4. Open UI
# → http://localhost:8000
```
or 
download and deploy in vercal.com
---

## 🏗️ Architecture

```
aurix/
├── run.py                     # Main entry point
├── .env                       # API keys & configuration
├── requirements.txt           # Python dependencies
├── setup.sh                   # Installation script
│
├── config/                    # Configuration management
│   └── settings.py            # Pydantic settings
│
├── core/                      # AI Intelligence Core
│   ├── brain.py               # NVIDIA GPT engine
│   ├── orchestrator.py        # Agent coordinator
│   └── agents/
│       ├── task_agent.py      # Command execution
│       ├── research_agent.py  # Web search & research
│       ├── memory_agent.py    # ChromaDB memory
│       └── system_agent.py    # OS control
│
├── voice/                     # Voice System
│   ├── stt.py                 # Whisper speech-to-text
│   └── tts.py                 # Coqui text-to-speech
│
├── vision/                    # Computer Vision
│   └── face_recognition_module.py
│
├── creative/                  # Generative AI
│   └── image_gen.py           # NVIDIA image generation
│
├── security/                  # Security Layer
│   └── auth.py                # Auth + activity logging
│
├── api/                       # API Server
│   └── server.py              # FastAPI + WebSocket
│
└── ui/                        # Futuristic Web Interface
    ├── index.html             # Main HUD layout
    ├── css/aurix.css          # Neon tech styling
    └── js/
        ├── app.js             # Main app controller
        ├── three-scene.js     # Particle background
        ├── hud.js             # Gauge widgets
        ├── voice.js           # Waveform visualizer
        └── websocket.js       # Real-time comms
```

---

## 🎯 Demo Commands

Try these in the AURIX console:

| Command | What it does |
|---|---|
| `What time is it?` | Natural conversation |
| `Show system status` | CPU, RAM, disk info |
| `Search for latest AI news` | Web search via SerpAPI |
| `Open firefox` | Launch applications |
| `Take a screenshot` | Capture screen |
| `Remember that I prefer dark themes` | Store preference |
| `What do you remember about me?` | Recall memories |
| `Generate a cyberpunk cityscape` | AI image generation |
| `Show running processes` | List top processes |
| `Set volume to 50` | Control system volume |

---

## 🧠 AI Modules

| Module | Technology | Status |
|---|---|---|
| AI Brain | NVIDIA API (GPT-OSS-120B) | ✅ |
| Task Agent | Python subprocess | ✅ |
| Research Agent | SerpAPI | ✅ |
| Memory Agent | ChromaDB | ✅ |
| System Agent | psutil + PyAutoGUI | ✅ |
| Voice STT | OpenAI Whisper | ✅ |
| Voice TTS | Coqui TTS | ✅ |
| Face Recognition | OpenCV + dlib | ✅ |
| Image Generation | NVIDIA API | ✅ |
| Security | SHA-256 + face auth | ✅ |

---

## 🔐 Security

- **Face unlock** via webcam
- **Password authentication**
- **Activity logging** (JSON logs in `data/logs/`)
- **Safe command execution** (dangerous commands blocked)

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serve AURIX UI |
| `/api/chat` | POST | Send message to AI |
| `/api/system/stats` | GET | System monitoring data |
| `/api/search` | POST | Web search |
| `/api/memory/store` | POST | Store a memory |
| `/api/memory/recall` | POST | Recall memories |
| `/api/image/generate` | POST | Generate image |
| `/api/auth` | POST | Authenticate |
| `/api/logs` | GET | Activity logs |
| `/api/health` | GET | Health check |
| `/ws` | WebSocket | Real-time streaming |

---

## 📜 License

MIT — Built for personal use and learning.
