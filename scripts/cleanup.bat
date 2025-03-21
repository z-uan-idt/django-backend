@echo off
echo Cleaning up Python cache files...
powershell -Command "Get-ChildItem -Path . -Include '__pycache__' -Directory -Recurse | Remove-Item -Recurse -Force"
pause