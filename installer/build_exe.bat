@echo off
setlocal
cd /d "%~dp0.."
where py >nul 2>nul || (echo Python launcher not found.&pause&exit /b 1)
py -m pip install --upgrade pyinstaller
py -m PyInstaller --noconfirm --clean maxguard.spec
if errorlevel 1 (echo PyInstaller build failed.&pause&exit /b 1)
echo EXE build complete: dist\MaxGuard\MaxGuard.exe
pause
