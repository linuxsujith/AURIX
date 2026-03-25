"""
AURIX Security — Authentication and activity logging.
"""

import json
import os
import hashlib
from datetime import datetime
from config.settings import get_settings


class SecurityManager:
    """Handles authentication and activity logging."""

    def __init__(self):
        settings = get_settings()
        self.log_dir = os.path.join(settings.project_root, "data", "logs")
        self.auth_file = os.path.join(settings.project_root, "data", "auth.json")
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        self.authenticated = False
        self.current_user = None

    def setup_password(self, password: str) -> dict:
        """Set up password authentication."""
        try:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            auth_data = self._load_auth()
            auth_data["password_hash"] = hashed
            self._save_auth(auth_data)
            return {"success": True, "message": "Password set"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_password(self, password: str) -> bool:
        """Verify password."""
        auth_data = self._load_auth()
        stored_hash = auth_data.get("password_hash", "")
        if not stored_hash:
            return True  # No password set, allow access
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash

    def authenticate(self, method: str = "password", **kwargs) -> dict:
        """Authenticate user."""
        if method == "password":
            password = kwargs.get("password", "")
            if self.verify_password(password):
                self.authenticated = True
                self.current_user = "owner"
                self.log_activity("authentication", "Password login successful")
                return {"success": True, "user": "owner"}
            else:
                self.log_activity("authentication", "Failed password attempt")
                return {"success": False, "error": "Invalid password"}

        elif method == "face":
            from vision.face_recognition_module import FaceRecognition
            fr = FaceRecognition()
            result = fr.verify_face()
            if result.get("authenticated"):
                self.authenticated = True
                self.current_user = result.get("user", "owner")
                self.log_activity("authentication", f"Face login: {self.current_user}")
                return {"success": True, "user": self.current_user}
            return {"success": False, "error": "Face not recognized"}

        return {"success": False, "error": f"Unknown auth method: {method}"}

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.authenticated

    def log_activity(self, category: str, description: str, level: str = "info"):
        """Log an activity."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "description": description,
                "level": level,
                "user": self.current_user or "system"
            }

            log_file = os.path.join(self.log_dir, f"activity_{datetime.now().strftime('%Y%m%d')}.jsonl")
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

    def get_recent_logs(self, count: int = 50) -> list:
        """Get recent activity logs."""
        try:
            log_file = os.path.join(self.log_dir, f"activity_{datetime.now().strftime('%Y%m%d')}.jsonl")
            if not os.path.exists(log_file):
                return []

            logs = []
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        logs.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        pass
            return logs[-count:]
        except Exception:
            return []

    def _load_auth(self) -> dict:
        """Load auth data."""
        try:
            if os.path.exists(self.auth_file):
                with open(self.auth_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_auth(self, data: dict):
        """Save auth data."""
        with open(self.auth_file, 'w') as f:
            json.dump(data, f, indent=2)
