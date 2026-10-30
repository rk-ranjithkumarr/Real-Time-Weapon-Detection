@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python launcher ^(py^) was not found.
    echo Install Python 3.11 from https://www.python.org/downloads/ and try again.
    pause
    exit /b 1
)

py -3.11 -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [OK] Environment installed.
echo First run will download the 5.47 MB YOLO11n weapon model.
echo.
pause
