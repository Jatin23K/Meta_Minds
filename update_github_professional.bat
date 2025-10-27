@echo off
REM Professional GitHub Update - Remove venv and update README
echo ========================================
echo  META MINDS - Professional Update
echo ========================================
echo.

echo Step 1: Remove venv from git tracking...
git rm -r --cached venv 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    venv removed from tracking
) else (
    echo    venv not tracked or already removed
)
echo.

echo Step 2: Remove Output folder from git tracking...
git rm -r --cached Output 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    Output removed from tracking
) else (
    echo    Output not tracked or already removed
)
echo.

echo Step 3: Remove other excluded files...
git rm -r --cached __pycache__ 2>nul
git rm --cached .env 2>nul
git rm --cached user_context.json 2>nul
git rm -r --cached logs 2>nul
echo    Cleaned up excluded files
echo.

echo Step 4: Add updated files...
git add .
echo    All current files staged
echo.

echo Step 5: Commit professional update...
git commit -m "META MINDS v2.0 - Professional Repository Setup

REMOVED (per .gitignore):
- venv/ folder (17,000+ files) - users create their own
- Output/ folder (user-generated reports)
- .env file (API keys - security)
- __pycache__/ (Python bytecode)

ADDED/UPDATED:
- Professional README with centered header
- Intelligent column analysis system
- CLI automation (quick/config/batch modes)  
- Multi-format exports (Excel/JSON/HTML)
- Professional emoji system with auto-fallback
- Exact question count enforcement
- Enhanced context collection
- Smart output directory management
- Comprehensive documentation

Repository now follows GitHub best practices.
Clean, professional, production-ready."
echo.

echo Step 6: Push to GitHub...
git push origin main
echo.

echo ========================================
echo  Professional update complete!
echo.
echo  View your repo:
echo  https://github.com/Jatin23K/Meta_Minds_-Question_Generator-
echo.
echo  Next step: Add description and topics on GitHub
echo ========================================
echo.
echo Press any key to open GitHub in browser...
pause
start https://github.com/Jatin23K/Meta_Minds_-Question_Generator-/settings

