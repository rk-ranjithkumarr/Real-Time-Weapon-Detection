@echo off
setlocal
if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found.
    echo Run install_windows.bat first.
    pause
    exit /b 1
)
set /p VIDEO=Enter video path (example: sample.mp4):
call .venv\Scripts\activate
python app.py --source "%VIDEO%"
pause
