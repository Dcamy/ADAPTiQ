:: path: blackmirror_lite/install_autostart.bat
@echo off
set SCRIPT_PATH=%~dp0blackmirror_lite.py
set PROJECT_PATH=C:\path\to\your\project  :: <-- user edits this!
set PYTHON_PATH=C:\path\to\python.exe     :: <-- or autodetect

set TARGET="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\blackmirror_startup.bat"
echo @echo off > %TARGET%
echo start "" "%PYTHON_PATH%" "%SCRIPT_PATH%" "%PROJECT_PATH%" >> %TARGET%
echo [✔] Startup task created: %TARGET%
pause
