import threading, time
from pathlib import Path

class RealtimeMonitor:
    def __init__(self, paths, callback):
        self.paths = [Path(p) for p in paths]
        self.callback = callback
        self.stop_event = threading.Event()
        self.thread = None
        self.snapshot = {}

    def start(self):
        if self.thread and self.thread.is_alive(): return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def _scan_snapshot(self):
        current = {}
        for root in self.paths:
            if not root.exists(): continue
            try:
                for p in root.rglob("*"):
                    if p.is_file():
                        try: current[str(p)] = p.stat().st_mtime_ns
                        except OSError: pass
            except (OSError, PermissionError):
                pass
        return current

    def _run(self):
        self.snapshot = self._scan_snapshot()
        while not self.stop_event.wait(3):
            new = self._scan_snapshot()
            for p, stamp in new.items():
                if p not in self.snapshot or self.snapshot[p] != stamp:
                    self.callback(Path(p))
            self.snapshot = new
