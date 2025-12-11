@echo off
title Tourli Launcher

echo Starting Tourli Backend API...
start cmd /k "cd /d C:\Users\akhda\Desktop\uni\python projects\final progect & python chatbot_api.py"

echo Waiting for backend to boot...
timeout /t 2 >nul

echo Starting Tourli Frontend Website...
start cmd /k "cd /d C:\Users\akhda\Desktop\uni\python projects\final progect\tourli-website & python -m http.server 8000"

echo Opening website in browser...
timeout /t 1 >nul
start http://localhost:8000

echo All done! Enjoy Tourli 😎
pause
