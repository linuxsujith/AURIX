"""
System Agent — Controls the operating system.
"""

import asyncio
import psutil
import platform
import os
from datetime import datetime


class SystemAgent:
    """Handles OS control, system monitoring, and automation."""

    def __init__(self):
        self.os_type = platform.system().lower()

    async def execute(self, action: dict) -> dict:
        """Execute a system action."""
        action_type = action.get("action", "")
        params = action.get("params", {})

        handlers = {
            "system_info": self._get_system_info,
            "take_screenshot": self._take_screenshot,
            "set_volume": self._set_volume,
            "set_brightness": self._set_brightness,
            "lock_screen": self._lock_screen,
            "list_processes": self._list_processes,
            "kill_process": self._kill_process,
        }

        handler = handlers.get(action_type)
        if handler:
            return await handler(params)

        return {"success": False, "error": f"Unknown system action: {action_type}"}

    async def _get_system_info(self, params: dict = None) -> dict:
        """Get comprehensive system information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            battery = psutil.sensors_battery()
            boot_time = datetime.fromtimestamp(psutil.boot_time())

            return {
                "success": True,
                "system": {
                    "os": platform.system(),
                    "os_version": platform.version(),
                    "hostname": platform.node(),
                    "architecture": platform.machine(),
                    "uptime": str(datetime.now() - boot_time),
                },
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "physical_cores": psutil.cpu_count(logical=False),
                    "freq_mhz": round(psutil.cpu_freq().current, 0) if psutil.cpu_freq() else 0,
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent,
                },
                "network": {
                    "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
                    "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
                },
                "battery": {
                    "percent": battery.percent if battery else None,
                    "charging": battery.power_plugged if battery else None,
                } if battery else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_live_stats(self) -> dict:
        """Get quick live stats for the HUD widgets."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()

            return {
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "memory_used_gb": round(mem.used / (1024**3), 1),
                "memory_total_gb": round(mem.total / (1024**3), 1),
                "disk_percent": disk.percent,
                "net_sent_mb": round(net.bytes_sent / (1024**2), 1),
                "net_recv_mb": round(net.bytes_recv / (1024**2), 1),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _take_screenshot(self, params: dict = None) -> dict:
        """Take a screenshot."""
        try:
            import pyautogui
            path = params.get("path", f"/tmp/aurix_screenshot_{int(datetime.now().timestamp())}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _set_volume(self, params: dict) -> dict:
        """Set system volume (Linux)."""
        level = params.get("level", 50)
        try:
            proc = await asyncio.create_subprocess_shell(
                f"amixer set Master {level}%",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return {"success": True, "volume": level}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _set_brightness(self, params: dict) -> dict:
        """Set screen brightness (Linux)."""
        level = params.get("level", 50)
        try:
            proc = await asyncio.create_subprocess_shell(
                f"xrandr --output $(xrandr | grep ' connected' | head -1 | cut -d' ' -f1) --brightness {level/100}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return {"success": True, "brightness": level}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _lock_screen(self, params: dict = None) -> dict:
        """Lock the screen."""
        try:
            cmd = "loginctl lock-session" if self.os_type == "linux" else "rundll32.exe user32.dll,LockWorkStation"
            proc = await asyncio.create_subprocess_shell(cmd)
            await proc.communicate()
            return {"success": True, "message": "Screen locked"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _list_processes(self, params: dict = None) -> dict:
        """List running processes sorted by CPU usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] and info['cpu_percent'] > 0:
                        processes.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return {"success": True, "processes": processes[:20]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _kill_process(self, params: dict) -> dict:
        """Kill a process by name or PID."""
        pid = params.get("pid")
        name = params.get("name")

        try:
            if pid:
                p = psutil.Process(int(pid))
                p.terminate()
                return {"success": True, "message": f"Terminated PID {pid}"}
            elif name:
                killed = 0
                for proc in psutil.process_iter(['name']):
                    if name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed += 1
                return {"success": True, "message": f"Terminated {killed} processes matching '{name}'"}
            return {"success": False, "error": "Provide pid or name"}
        except Exception as e:
            return {"success": False, "error": str(e)}
