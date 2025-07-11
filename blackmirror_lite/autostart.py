"""
Autostart installation for BlackMirror Lite across different OSes.
"""
import platform
import sys
import subprocess


def install_autostart_unix():
    """
    Create a shell script to activate the project environment and start the watcher,
    then register it in the user's crontab to run on reboot.
    """
    import os

    # Determine project root for the autostart wrapper script
    project_root = os.getcwd()

    # Detect virtual environment directory (common names)
    venv_dir = None
    for name in ("env", ".venv", "venv"):
        if os.path.isdir(os.path.join(project_root, name)):
            venv_dir = name
            break

    # Detect available shells from /etc/shells
    shells = []
    try:
        with open("/etc/shells", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    shells.append(os.path.basename(line))
    except Exception:
        pass
    if "bash" not in shells:
        shells.append("bash")
    shells = sorted(set(shells))

    # Prompt user to select the shell for the wrapper script
    print("Detected shells for autostart script:")
    for idx, sh in enumerate(shells, start=1):
        print(f"  {idx}. {sh}")
    choice = input(f"Select shell [1-{len(shells)}] (default 1): ").strip()
    try:
        sh_idx = int(choice) - 1 if choice else 0
        shell = shells[sh_idx]
    except Exception:
        shell = "bash"

    # Determine activation command for virtualenv, if detected
    act_cmd = ""
    if venv_dir:
        bin_dir = os.path.join(project_root, venv_dir, "bin")
        script_map = {"fish": "activate.fish", "csh": "activate.csh", "tcsh": "activate.csh"}
        act_script = os.path.join(bin_dir, script_map.get(shell, "activate"))
        if os.path.isfile(act_script):
            if shell == "fish":
                act_cmd = f". \"{act_script}\""
            else:
                act_cmd = f"source \"{act_script}\""
        else:
            print(f"Warning: no activation script found at {act_script}")

    # Confirm or override the activation command
    if act_cmd:
        ans = input(f"Use activation command '{act_cmd}'? [Y/n]: ").strip().lower()
        if ans.startswith("n"):
            act_cmd = input("Enter custom activation command: ").strip()

    # Determine watcher startup command
    import shutil

    default_watch = (
        "bml watch" if shutil.which("bml")
        else f"\"{sys.executable}\" -m blackmirror_lite watch"
    )
    watch_cmd = input(
        f"Watcher startup command (default: {default_watch!r}): "
    ).strip() or default_watch

    # Build the wrapper script content
    script_lines = [f"#!/usr/bin/env {shell}", f"cd \"{project_root}\""]
    if act_cmd:
        script_lines.append(act_cmd)
    script_lines.append(watch_cmd)
    script_text = "\n".join(script_lines) + "\n"

    # Write the wrapper script into the project root
    script_path = os.path.join(project_root, "bml_autostart.sh")
    try:
        with open(script_path, "w") as f:
            f.write(script_text)
        os.chmod(script_path, 0o755)
    except Exception as e:
        print(f"Failed to write autostart script: {e}")
        return

    # Register the wrapper script in the user's crontab
    try:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines = res.stdout.splitlines() if res.returncode == 0 else []
        entry = f"@reboot {script_path}"
        if entry in lines:
            print("Autostart already installed in crontab.")
            return
        lines.append(entry)
        new_cron = "\n".join(lines) + "\n"
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(new_cron)
        print(f"Autostart installed via crontab; wrapper script at {script_path}")
    except Exception as e:
        print(f"Failed to install autostart via crontab: {e}")


def install_autostart_windows():
    """Add a Run entry in the Windows user registry for auto-launch on login."""
    try:
        import winreg
        import shutil

        # Choose default startup command: prefer 'bml' on PATH, else use module invocation
        default_cmd = "bml watch" if shutil.which("bml") else f'"{sys.executable}" -m blackmirror_lite watch'
        prompt = (
            f"Enter the command to run on login (leave blank for default: {default_cmd}): "
        )
        try:
            user_cmd = input(prompt).strip()
        except Exception:
            user_cmd = ""
        cmd_line = user_cmd or default_cmd
        # Wrap in cmd.exe /k so the terminal stays open until manually closed
        wrapped = f'cmd.exe /k "{cmd_line}"'
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "BlackMirrorLite", 0, winreg.REG_SZ, wrapped)
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