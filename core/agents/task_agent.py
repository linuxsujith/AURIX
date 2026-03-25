"""
Task Agent — Executes commands and manages task workflows.
"""

import subprocess
import asyncio
import json
from typing import Optional


class TaskAgent:
    """Handles task execution — running commands, managing workflows."""

    def __init__(self):
        self.task_history = []

    async def execute(self, action: dict) -> dict:
        """Execute a task action and return result."""
        action_type = action.get("action", "")
        params = action.get("params", {})

        handlers = {
            "run_command": self._run_command,
            "open_app": self._open_app,
            "close_app": self._close_app,
            "manage_file": self._manage_file,
            "open_url": self._open_url,
            "open_folder": self._open_folder,
            "open_terminal": self._open_terminal,
        }

        handler = handlers.get(action_type)
        if handler:
            result = await handler(params)
            self.task_history.append({"action": action, "result": result})
            return result

        return {"success": False, "error": f"Unknown action: {action_type}"}

    async def _run_command(self, params: dict) -> dict:
        """Run a shell command safely."""
        command = params.get("command", "")
        if not command:
            return {"success": False, "error": "No command provided"}

        # Safety: block dangerous commands
        dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb"]
        if any(d in command.lower() for d in dangerous):
            return {"success": False, "error": "Command blocked for safety"}

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=30
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode()[:2000],
                "stderr": stderr.decode()[:500],
                "return_code": process.returncode
            }
        except asyncio.TimeoutError:
            return {"success": False, "error": "Command timed out (30s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _open_app(self, params: dict) -> dict:
        """Open an application."""
        app_name = params.get("name", "")
        if not app_name:
            return {"success": False, "error": "No app name provided"}

        try:
            process = await asyncio.create_subprocess_shell(
                f"nohup {app_name} &>/dev/null &",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return {"success": True, "message": f"Opened {app_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _close_app(self, params: dict) -> dict:
        """Close an application by name."""
        app_name = params.get("name", "")
        if not app_name:
            return {"success": False, "error": "No app name provided"}

        try:
            process = await asyncio.create_subprocess_shell(
                f"pkill -f {app_name}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return {"success": True, "message": f"Closed {app_name}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _open_url(self, params: dict) -> dict:
        """Open a URL in the system's default browser."""
        import webbrowser
        url = params.get("url", "")
        if not url:
            return {"success": False, "error": "No URL provided"}

        # Ensure URL has a protocol
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            # Use Python's built-in webbrowser which reliably detaches
            success = webbrowser.open(url)
            if success:
                return {"success": True, "message": f"Opened {url} in browser", "url": url}
            else:
                return {"success": False, "error": "Could not open browser"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _open_folder(self, params: dict) -> dict:
        """Open a folder in the system file manager."""
        import os
        import subprocess
        path = params.get("path", os.path.expanduser("~"))

        if not os.path.isdir(path):
            return {"success": False, "error": f"Directory not found: {path}"}

        try:
            # Use Popen to detach the process completely so we don't hang waiting for it
            subprocess.Popen(
                ["xdg-open", path],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {"success": True, "message": f"Opened folder: {path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _open_terminal(self, params: dict) -> dict:
        """Open a new terminal window."""
        working_dir = params.get("path", "")

        # Try common terminal emulators in order
        terminals = [
            "gnome-terminal", "xfce4-terminal", "konsole",
            "mate-terminal", "tilix", "x-terminal-emulator"
        ]

        for term in terminals:
            try:
                cmd = f"nohup {term}"
                if working_dir:
                    cmd += f" --working-directory='{working_dir}'"
                cmd += " &>/dev/null &"

                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                if process.returncode == 0 or process.returncode is None:
                    return {"success": True, "message": f"Opened {term}"}
            except Exception:
                continue

        return {"success": False, "error": "No terminal emulator found"}

    async def _manage_file(self, params: dict) -> dict:
        """File operations: create, read, delete, list."""
        import os
        operation = params.get("operation", "")
        path = params.get("path", "")

        if operation == "read":
            try:
                with open(path, 'r') as f:
                    content = f.read()[:5000]
                return {"success": True, "content": content}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif operation == "create":
            content = params.get("content", "")
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
                return {"success": True, "message": f"Created {path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif operation == "delete":
            try:
                os.remove(path)
                return {"success": True, "message": f"Deleted {path}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        elif operation == "list":
            try:
                items = os.listdir(path)
                return {"success": True, "items": items[:100]}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Unknown file operation: {operation}"}
