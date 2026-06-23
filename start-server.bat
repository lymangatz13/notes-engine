@echo off
cd /d "%~dp0"
echo ============================================
echo  Simple Notes Generator -- backend
echo ============================================
echo Installing dependencies (first run only)...
pip install -r requirements.txt
echo.
echo Starting server at http://localhost:5000
echo Leave this window open while you use the page.
echo.
python transcribe.py
pause
