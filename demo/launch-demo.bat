@echo off
echo Starting AI Health Navigator Demo...
echo.
echo Opening demo in your default browser...
echo.

REM Try to open the demo HTML file
start "" "%~dp0launch-demo.html"

echo Demo launched successfully!
echo.
echo If the demo doesn't open automatically, please:
echo 1. Navigate to the demo folder
echo 2. Open launch-demo.html in your web browser
echo.
echo Press any key to exit...
pause >nul
