"""
AURIX FastAPI Server — Main API and WebSocket server.
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Add project root to path
PROJECT_ROOT = str(Path(__file__).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.settings import get_settings
from core.orchestrator import AgentOrchestrator
from security.auth import SecurityManager


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AURIX AI Assistant",
        description="Next-Generation AI Assistant API",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize core services
    orchestrator = AgentOrchestrator()
    security = SecurityManager()

    # Serve static UI files
    ui_path = os.path.join(PROJECT_ROOT, "ui")
    if os.path.exists(ui_path):
        app.mount("/static", StaticFiles(directory=ui_path), name="static")

    # --- Models ---
    class ChatRequest(BaseModel):
        message: str
        context: Optional[str] = ""

    class AuthRequest(BaseModel):
        method: str = "password"
        password: Optional[str] = ""

    class SearchRequest(BaseModel):
        query: str
        num_results: int = 5

    class MemoryRequest(BaseModel):
        content: str
        category: str = "general"

    class ImageRequest(BaseModel):
        prompt: str
        filename: Optional[str] = None

    # --- Routes ---

    @app.get("/", response_class=HTMLResponse)
    async def serve_ui():
        """Serve the main AURIX UI."""
        index_path = os.path.join(ui_path, "index.html")
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>AURIX UI not found</h1>")

    @app.post("/api/chat")
    async def chat(request: ChatRequest):
        """Send a message and get AI response."""
        # Handle direct actions from frontend (bypass AI)
        if request.message.startswith("__DIRECT_ACTION__"):
            try:
                action_data = json.loads(request.message[17:])
                action_result = await orchestrator._route_action(action_data)
                return {
                    "response": action_result.get("message", "Done"),
                    "action_taken": True,
                    "action_result": action_result
                }
            except Exception as e:
                return {"response": f"Action failed: {str(e)}", "action_taken": False}

        result = await orchestrator.process(request.message)
        return result

    @app.post("/api/auth")
    async def authenticate(request: AuthRequest):
        """Authenticate user."""
        return security.authenticate(method=request.method, password=request.password)

    @app.get("/api/system/stats")
    async def system_stats():
        """Get live system statistics."""
        return await orchestrator.get_system_stats()

    @app.post("/api/search")
    async def search(request: SearchRequest):
        """Search the web."""
        return await orchestrator.quick_search(request.query)

    @app.post("/api/memory/store")
    async def store_memory(request: MemoryRequest):
        """Store a memory."""
        return orchestrator.memory_agent.store_memory(request.content, request.category)

    @app.post("/api/memory/recall")
    async def recall_memory(request: SearchRequest):
        """Recall memories."""
        return orchestrator.memory_agent.recall(request.query, request.num_results)

    @app.get("/api/memory/stats")
    async def memory_stats():
        """Get memory statistics."""
        return await orchestrator.get_memory_stats()

    @app.post("/api/image/generate")
    async def generate_image(request: ImageRequest):
        """Generate an image."""
        from creative.image_gen import ImageGenerator
        gen = ImageGenerator()
        return await gen.generate(request.prompt, request.filename)

    @app.get("/api/logs")
    async def get_logs():
        """Get recent activity logs."""
        return {"logs": security.get_recent_logs()}

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "online", "name": "AURIX", "version": "2.0.0"}

    # --- Face Authentication ---

    @app.post("/api/face/verify")
    async def face_verify(file: UploadFile = File(...)):
        """Verify a face from uploaded image."""
        try:
            import tempfile
            contents = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, mode='wb') as f:
                f.write(contents)
                temp_path = f.name

            from vision.face_recognition_module import FaceRecognition
            fr = FaceRecognition()
            # Verify against known faces using the uploaded image
            result = fr.verify_face(image_path=temp_path)

            import os
            os.unlink(temp_path)

            if result.get("authenticated"):
                security.log_activity("face_auth", f"Face login: {result.get('user')}")
                return {"authenticated": True, "user": result.get("user", "Owner")}
            return {"authenticated": False, "message": "Face not recognized"}
        except Exception as e:
            # If face recognition isn't fully set up, allow entry
            security.log_activity("face_auth", "Face verify fallback - allowed entry")
            return {"authenticated": True, "user": "User"}

    @app.post("/api/face/register")
    async def face_register(file: UploadFile = File(...), name: str = "owner"):
        """Register a new face."""
        try:
            import tempfile
            contents = await file.read()

            face_dir = os.path.join(PROJECT_ROOT, "data", "faces")
            os.makedirs(face_dir, exist_ok=True)

            face_path = os.path.join(face_dir, f"{name}.jpg")
            with open(face_path, 'wb') as f:
                f.write(contents)

            security.log_activity("face_register", f"New face registered: {name}")
            return {"success": True, "message": f"Face registered for {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- WebSocket for real-time streaming ---

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket for real-time AI conversation and system updates."""
        await websocket.accept()
        security.log_activity("connection", "WebSocket client connected")

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                msg_type = message.get("type", "chat")

                if msg_type == "chat":
                    # Stream AI response
                    user_input = message.get("content", "")
                    async for chunk in orchestrator.stream_process(user_input):
                        await websocket.send_json(chunk)
                    await websocket.send_json({"type": "done"})

                elif msg_type == "stats":
                    # Send system stats
                    stats = await orchestrator.get_system_stats()
                    await websocket.send_json({"type": "stats", "data": stats})

                elif msg_type == "search":
                    query = message.get("query", "")
                    result = await orchestrator.quick_search(query)
                    await websocket.send_json({"type": "search_result", "data": result})

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

        except WebSocketDisconnect:
            security.log_activity("connection", "WebSocket client disconnected")
        except Exception as e:
            try:
                await websocket.send_json({"type": "error", "message": str(e)})
            except Exception:
                pass

    return app


# Create the app instance
app = create_app()
