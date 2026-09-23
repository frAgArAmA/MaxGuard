# MaxGuard 1.0

A defensive, user-mode antivirus-like scanner built with Python and Tkinter.

Features:
- Dashboard
- Quick / Full / Custom Scan
- SHA-256 signatures
- Trusted hashes
- Safe heuristic analysis
- Magic-byte and extension checks
- Entropy analysis
- PE/script/archive inspection
- Risk score and evidence
- Threat Center
- Quarantine / restore / delete
- Scan history
- Activity log
- Settings
- English / Ukrainian / Spanish
- Optional user-mode real-time folder monitoring

This is not a kernel-level replacement for Microsoft Defender or a commercial antivirus.
It does not execute scanned files and does not use stealth, persistence, credential theft,
process injection, or other offensive behavior.

Run:
    python main.py
