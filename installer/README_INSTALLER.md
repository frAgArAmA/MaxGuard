# MaxGuard 1.0 Windows Installer

This package builds MaxGuard into a Windows application and then creates an Inno Setup installer.

## Local Windows build

1. Install Python 3.14.
2. Install Inno Setup 6.
3. Run `installer\build_installer.bat`.
4. The installer will be created at `installer\output\MaxGuard-1.0-Setup.exe`.

## GitHub Actions build

The repository includes `.github/workflows/build-windows.yml`.

You can run it manually from GitHub Actions (`workflow_dispatch`) or create a tag such as `v1.0.0` to trigger a build.

The workflow produces a downloadable installer artifact and prints its SHA-256 hash.

## Safety

MaxGuard is a user-mode defensive scanner. The installer does not add kernel drivers, exploit code, credential theft, persistence tricks, or malware behavior.
