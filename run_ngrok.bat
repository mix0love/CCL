@echo off
echo Starting Local Server and Ngrok...
echo.
echo 1. Starting Python Server on port 8000...
start "Local Server" python -m http.server 8000
echo.
echo 2. Starting Ngrok Tunnel...
echo    (If this fails, make sure 'ngrok.exe' is in this folder or installed)
echo.
ngrok http 8000
pause
