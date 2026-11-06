@echo off
title Stop Grand Azure Servers
echo Stopping Hotel Backend (Port 8000) and Frontend (Port 3000)...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /f /pid %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /f /pid %%a 2>nul

echo Done! Both servers have been stopped.
pause

