import hashlib, json, shutil
from pathlib import Path
from datetime import datetime

class Quarantine:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        self.meta = self.folder / "index.json"
        if not self.meta.exists():
            self.meta.write_text("[]", encoding="utf-8")

    def _read(self):
        try: return json.loads(self.meta.read_text(encoding="utf-8"))
        except Exception: return []

    def _write(self, x):
        self.meta.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding="utf-8")

    def put(self, source):
        source = Path(source)
        if not source.is_file(): return None
        token = hashlib.sha256(str(source).encode("utf-8")).hexdigest()[:16]
        target = self.folder / f"{token}_{source.name}"
        shutil.move(str(source), str(target))
        items = self._read()
        items.append({"id": token, "original": str(source), "stored": str(target),
                      "time": datetime.now().isoformat(timespec="seconds")})
        self._write(items)
        return token

    def items(self):
        return self._read()

    def restore(self, token):
        items = self._read()
        for item in items:
            if item["id"] == token:
                src, dst = Path(item["stored"]), Path(item["original"])
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                items.remove(item)
                self._write(items)
                return True
        return False

    def delete(self, token):
        items = self._read()
        for item in items:
            if item["id"] == token:
                try: Path(item["stored"]).unlink(missing_ok=True)
                except Exception: pass
                items.remove(item)
                self._write(items)
                return True
        return False
