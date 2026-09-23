import json
from pathlib import Path
from threading import RLock

class JSONDB:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        if not self.path.exists():
            self.write([])

    def read(self, default):
        with self.lock:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return default

    def write(self, value):
        with self.lock:
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.path)
