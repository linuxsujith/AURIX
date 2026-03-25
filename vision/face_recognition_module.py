"""
AURIX Vision Module — Face recognition and screen analysis.
"""

import os
import cv2
import numpy as np
from typing import Optional, List
from config.settings import get_settings


class FaceRecognition:
    """Face recognition for authentication and security."""

    def __init__(self):
        settings = get_settings()
        self.face_data_path = settings.vision.face_data_path
        self.enabled = settings.vision.face_recognition_enabled
        self.known_faces = {}
        self.face_cascade = None
        self._initialized = False

    def _ensure_init(self):
        """Initialize OpenCV components."""
        if self._initialized:
            return
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            os.makedirs(self.face_data_path, exist_ok=True)
            self._load_known_faces()
            self._initialized = True
            print("[Vision] Face recognition initialized")
        except Exception as e:
            print(f"[Vision] Init error: {e}")

    def _load_known_faces(self):
        """Load registered face encodings."""
        try:
            import face_recognition
            for filename in os.listdir(self.face_data_path):
                if filename.endswith(('.jpg', '.png', '.jpeg')):
                    path = os.path.join(self.face_data_path, filename)
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        name = os.path.splitext(filename)[0]
                        self.known_faces[name] = encodings[0]
                        print(f"[Vision] Loaded face: {name}")
        except ImportError:
            print("[Vision] face_recognition not available, using OpenCV only")
        except Exception as e:
            print(f"[Vision] Error loading faces: {e}")

    def register_face(self, name: str, image_path: str = None) -> dict:
        """Register a new face from image or webcam."""
        self._ensure_init()
        try:
            if image_path:
                import shutil
                dest = os.path.join(self.face_data_path, f"{name}.jpg")
                shutil.copy2(image_path, dest)
            else:
                # Capture from webcam
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    dest = os.path.join(self.face_data_path, f"{name}.jpg")
                    cv2.imwrite(dest, frame)
                else:
                    return {"success": False, "error": "Could not capture from webcam"}

            self._load_known_faces()
            return {"success": True, "message": f"Face registered for {name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_face(self, image_path: str = None) -> dict:
        """Verify face against registered faces.
        If image_path is provided, uses that image (faster).
        Otherwise falls back to webcam (slow initialization).
        """
        self._ensure_init()
        try:
            import face_recognition

            if image_path:
                # Use provided image from frontend (Instantaneous)
                frame = cv2.imread(image_path)
                if frame is None:
                    return {"success": False, "error": "Could not read provided image"}
            else:
                # Capture from webcam (Slow)
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    return {"success": False, "error": "Could not access webcam"}

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for encoding in face_encodings:
                for name, known_encoding in self.known_faces.items():
                    matches = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.6)
                    if matches[0]:
                        return {"success": True, "authenticated": True, "user": name}

            return {"success": True, "authenticated": False, "message": "Face not recognized"}
        except ImportError:
            return {"success": False, "error": "face_recognition library not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def detect_faces(self, frame=None) -> List[dict]:
        """Detect faces in a frame or from webcam."""
        self._ensure_init()
        try:
            if frame is None:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    return []

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            return [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]
        except Exception:
            return []
