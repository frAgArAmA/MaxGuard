@echo off
setlocal
cd /d "%~dp0.."
call installer\build_exe.bat
if errorlevel 1 exit /b 1
where ISCC.exe >nul 2>nul || (echo Inno Setup ISCC.exe not found. Install Inno Setup first.&pause&exit /b 1)
ISCC.exe installer\MaxGuard.iss
if errorlevel 1 (echo Inno Setup build failed.&pause&exit /b 1)
echo Installer created in installer\output\MaxGuard-1.0-Setup.exe
pause
