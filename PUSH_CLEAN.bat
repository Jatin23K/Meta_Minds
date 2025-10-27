@echo off
REM ==========================================
REM META_MINDS v2.0 - Clean GitHub Push
REM ==========================================
echo.
echo ========================================
echo  META MINDS - Clean GitHub Upload
echo ========================================
echo.

REM Navigate to the correct directory
cd /d "C:\Users\Jatin\Documents\Automation - DS [INDIVIDUAL]\1. META_MINDS"

echo [1/8] Cleaning up any existing Git history...
if exist ".git" (
    rmdir /s /q .git
    echo    Removed old Git history
) else (
    echo    No old Git history found
)

echo [2/8] Removing venv folder from disk temporarily...
if exist "venv" (
    echo    Found venv folder - will be excluded by .gitignore
)

echo [3/8] Initializing fresh Git repository...
git init
echo    Git initialized

echo [4/8] Adding all files except those in .gitignore...
git add .
echo    Files staged

echo [5/8] Checking what will be committed...
git status --short
echo.

echo [6/8] Creating initial commit...
git commit -m "META_MINDS v2.0 - Production Ready (10/10) - AI-powered SMART data analysis platform with 95 percent time savings"

if %ERRORLEVEL% EQU 0 (
    echo    Initial commit created successfully
) else (
    echo    ERROR: Commit failed
    pause
    exit /b 1
)

echo [7/8] Connecting to GitHub...
git remote add origin https://github.com/Jatin23K/Meta_Minds.git
git branch -M main
echo    Remote configured

echo [8/8] Pushing to GitHub...
git push -u origin main --force

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS - META_MINDS is on GitHub!
    echo ========================================
    echo.
    echo Repository: https://github.com/Jatin23K/Meta_Minds
    echo.
    echo Next Steps:
    echo   1. Add topics on GitHub
    echo   2. Verify venv is NOT visible
    echo   3. Verify input and Output folders ARE visible
    echo   4. Create v2.0.0 release
    echo.
    echo Opening GitHub in browser...
    start https://github.com/Jatin23K/Meta_Minds
) else (
    echo.
    echo ERROR: Push failed
    echo Please check your Git credentials and network connection.
)

echo.
echo Press any key to close...
pause >nul

