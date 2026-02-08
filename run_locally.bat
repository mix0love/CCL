@echo off
echo Starting Local Server...
echo.
echo Open your browser and go to: http://localhost:8000
echo.
echo To stop the server, verify this window is active and press Ctrl+C.
echo.
python -m http.server 8000
pause
