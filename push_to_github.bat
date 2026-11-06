@echo off
title Push Project to GitHub
color 0a

echo ==============================================================================
echo    PUSHING HOTEL SUPPORT AUTOMATION TO GITHUB (imran7976)
echo ==============================================================================
echo.
echo Make sure you have created the empty repository on GitHub first:
echo https://github.com/new
echo (Repository Name: hotel-guest-support-automation)
echo.
echo Press any key to push to origin main...
pause >nul

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==============================================================================
    echo    SUCCESS! Project successfully pushed to GitHub!
    echo    View your repo at: https://github.com/imran7976/hotel-guest-support-automation
    echo ==============================================================================
) else (
    echo.
    echo [ERROR] Push failed. If the repository does not exist yet:
    echo 1. Go to https://github.com/new
    echo 2. Create a repository named "hotel-guest-support-automation"
    echo 3. Run this file again.
)

pause
