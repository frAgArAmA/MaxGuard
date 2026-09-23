# MaxGuard 1.0 — Release Build

This is the Windows release-ready source for MaxGuard 1.0.

The safest path is to push this project to GitHub and use the included GitHub Actions workflow to build the Windows installer on a Windows runner.

Output:
- `MaxGuard.exe`
- `MaxGuard-1.0-Setup.exe`
- SHA-256 hash printed by the workflow

After the installer is built, upload `MaxGuard-1.0-Setup.exe` to the website's `downloads/` folder or attach it to a GitHub Release.
