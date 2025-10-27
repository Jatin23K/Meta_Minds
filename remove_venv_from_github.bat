@echo off
REM Remove venv from GitHub repository
echo ========================================
echo  Removing venv from GitHub
echo ========================================
echo.

echo Step 1: Remove venv from git cache...
git rm -r --cached venv
echo.

echo Step 2: Ensure .gitignore is correct...
echo venv/ >> .gitignore
echo.

echo Step 3: Commit the removal...
git add .gitignore
git commit -m "Remove venv folder from repository

- Removed 17,000+ venv files
- Updated .gitignore to exclude venv/
- Users should create their own virtual environment"
echo.

echo Step 4: Push to GitHub (force if needed)...
git push origin main
echo.

echo ========================================
echo  venv removed from GitHub!
echo  Repository is now clean.
echo ========================================
pause

