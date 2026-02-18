@echo off
echo ========================================
echo GitHub Push Helper for ExamForms.org
echo ========================================
echo.
echo Please enter your GitHub Personal Access Token when prompted
echo (Create one at: https://github.com/settings/tokens)
echo.
set /p TOKEN="Enter your GitHub token: "
echo.
echo Pushing to GitHub...
git push https://%TOKEN%@github.com/captosoftdigital/examforms.git main
echo.
echo Done! Check https://github.com/captosoftdigital/examforms
pause
