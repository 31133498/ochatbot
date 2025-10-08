@echo off
echo [STARTING] OpportunityBot...
echo.
echo [1] Starting backend server...
start /B python final_bot.py
timeout /t 3 /nobreak >nul
echo [2] Starting ngrok tunnel...
start /B ngrok http 8000
timeout /t 5 /nobreak >nul
echo.
echo [OK] OpportunityBot is starting!
echo.
echo Dashboard: http://localhost:8000
echo Ngrok URL: Check ngrok terminal for public URL
echo.
pause