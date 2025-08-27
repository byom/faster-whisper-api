@echo off

if not exist "%~dp0\venv\Scripts" (
    echo Creating venv...
    python -m venv venv
)
echo checked the venv folder. now installing requirements..

call "%~dp0\venv\scripts\activate"

python -m pip install -U pip
pip install Flask
pip install faster-whisper
pip install requests
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118

if errorlevel 1 (
    echo.
    echo Requirements installation failed. please remove venv folder and run install.bat again.
) else (
    echo.
    echo Requirements installed successfully.
)
pause