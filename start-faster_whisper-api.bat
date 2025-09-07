@echo off
rem %~dp0 会获取当前bat文件所在的目录
call "%~dp0venv\scripts\activate.bat"
echo "Python executable in use:"
where python
echo.

echo "Launching the app..."
D:\Artificial_Intelligence\TTS\faster-whisper-api\venv\Scripts\python.exe "%~dp0app.py"
echo "The app has finished."
pause