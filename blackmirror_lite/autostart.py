"""
Autostart installation for BlackMirror Lite across different OSes.
"""
import platform
import sys
import subprocess


def install_autostart_unix():
    """Use user crontab to add @reboot entry for watching all tracked folders."""
    try:
        # Read existing crontab (if any)
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines = res.stdout.splitlines() if res.returncode == 0 else []
        entry = f"@reboot {sys.executable} -m blackmirror_lite watch"
        if entry in lines:
            print("Autostart already installed in crontab.")
            return
        lines.append(entry)
        new = "\n".join(lines) + "\n"
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(new)
        print("Autostart installed via user crontab.")
    except Exception as e:
        print(f"Failed to install autostart via crontab: {e}")


def install_autostart_windows():
    """Add a Run entry in the Windows user registry for auto-launch on login."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        cmd = f'"{sys.executable}" -m blackmirror_lite watch'
        winreg.SetValueEx(key, "BlackMirrorLite", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print("Autostart installed in Windows registry Run key.")
    except Exception as e:
        print(f"Failed to install autostart in registry: {e}")


def install_autostart():
    """Prompt and install OS-native autostart for the watcher."""
    try:
        answer = input("Install autostart so BlackMirror Lite runs on boot? [y/N] ")
    except Exception:
        print("Autostart installation skipped (non-interactive).")
        return
    if not answer.lower().startswith('y'):
        print("Autostart not installed.")
        return

    system = platform.system()
    if system in ("Linux", "Darwin"):
        install_autostart_unix()
    elif system == "Windows":
        install_autostart_windows()
    else:
        print(f"Autostart not supported on platform: {system}")