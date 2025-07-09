"""
Add BlackMirror Lite to OS autostart with a single command.

Usage:
    python -m blackmirror_lite.install_autostart /absolute/path/to/project

• Windows   ─>  Writes a .bat file into %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
• macOS     ─>  Creates ~/Library/LaunchAgents/com.blackmirror.lite.plist
• Linux     ─>  Creates ~/.config/autostart/blackmirror.desktop  (XDG spec)

The watcher will start at boot and mirror the targeted project path.
"""
from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from textwrap import dedent
import plistlib

SCRIPT_PATH = Path(__file__).parent / "blackmirror_lite.py"


def err(msg: str, code: int = 1):
    print(f"[❌] {msg}")
    sys.exit(code)


def add_windows_autostart(target: Path):
    startup_dir = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    bat_path = startup_dir / "blackmirror_lite_autostart.bat"

    python_exe = Path(sys.executable).resolve()
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(f'start "" "{python_exe}" "{SCRIPT_PATH}" "{target}"\n')
    print(f"[✅] Windows autostart created → {bat_path}")


def add_macos_autostart(target: Path):
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / "com.blackmirror.lite.plist"

    plist = {
        "Label": "com.blackmirror.lite",
        "ProgramArguments": [str(Path(sys.executable).resolve()), str(SCRIPT_PATH), str(target)],
        "RunAtLoad": True,
        "StandardOutPath": str(Path.home() / "Library/Logs/blackmirror_lite.out.log"),
        "StandardErrorPath": str(Path.home() / "Library/Logs/blackmirror_lite.err.log"),
        "EnvironmentVariables": {},
    }
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    print(f"[✅] macOS autostart created → {plist_path}")
    print("ℹ️  Run `launchctl load ~/Library/LaunchAgents/com.blackmirror.lite.plist` to enable immediately.")


def add_linux_autostart(target: Path):
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop_path = autostart_dir / "blackmirror_lite.desktop"

    desktop_file = dedent(
        f"""\
        [Desktop Entry]
        Type=Application
        Name=BlackMirror Lite
        Exec={sys.executable} {SCRIPT_PATH} {target}
        X-GNOME-Autostart-enabled=true
        Comment=Git failsafe auto-backup
        """
    )
    with open(desktop_path, "w", encoding="utf-8") as f:
        f.write(desktop_file)
    print(f"[✅] Linux autostart created → {desktop_path}")


def main():
    if len(sys.argv) != 2:
        err("Usage: python -m blackmirror_lite.install_autostart /absolute/path/to/project")

    target_path = Path(sys.argv[1]).expanduser().resolve()
    if not target_path.exists():
        err(f"Provided path does not exist: {target_path}")

    os_type = platform.system()
    print(f"[🔧] Detected OS: {os_type}")

    try:
        if os_type == "Windows":
            add_windows_autostart(target_path)
        elif os_type == "Darwin":
            add_macos_autostart(target_path)
        elif os_type == "Linux":
            add_linux_autostart(target_path)
        else:
            err(f"Unsupported OS: {os_type}")
    except Exception as e:
        err(f"Failed to set autostart: {e}")


if __name__ == "__main__":
    main()
