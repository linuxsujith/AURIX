"""
AURIX Image Generation — NVIDIA API integration.
"""

import aiohttp
import base64
import os
from datetime import datetime
from config.settings import get_settings


class ImageGenerator:
    """Generate images using NVIDIA API."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.image_gen.api_key
        self.base_url = settings.image_gen.base_url
        self.output_dir = os.path.join(settings.project_root, "data", "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate(self, prompt: str, filename: str = None) -> dict:
        """Generate an image from a text prompt."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            payload = {
                "model": "stabilityai/stable-diffusion-xl-turbo",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/images/generations",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"success": False, "error": f"API error ({response.status}): {error_text[:200]}"}

                    data = await response.json()

            # Save the image
            if not filename:
                filename = f"aurix_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = os.path.join(self.output_dir, filename)

            if data.get("data") and len(data["data"]) > 0:
                image_data = data["data"][0]
                if "b64_json" in image_data:
                    img_bytes = base64.b64decode(image_data["b64_json"])
                    with open(output_path, 'wb') as f:
                        f.write(img_bytes)
                elif "url" in image_data:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_data["url"]) as img_resp:
                            img_bytes = await img_resp.read()
                            with open(output_path, 'wb') as f:
                                f.write(img_bytes)

                return {
                    "success": True,
                    "path": output_path,
                    "prompt": prompt,
                    "message": f"Image generated and saved to {output_path}"
                }

            return {"success": False, "error": "No image data in response"}

        except Exception as e:
            return {"success": False, "error": str(e)}
