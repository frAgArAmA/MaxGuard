# MaxGuard Website 1.0

Static landing page for MaxGuard 1.0.

## Files
- `site/index.html` — main page
- `site/style.css` — dark MaxGuard UI
- `site/script.js` — EN/UK/ES language switcher
- `site/downloads/` — place `MaxGuard-1.0-Setup.exe` here before publishing

## Local test
Open `site/index.html` in a browser.

For a local server:
`python -m http.server 8080 --directory site`

Then open:
`http://localhost:8080`

## Production
Replace the placeholder installer with the real signed installer:
`site/downloads/MaxGuard-1.0-Setup.exe`

For a real public release, publish the installer over HTTPS and provide its SHA-256 hash.
