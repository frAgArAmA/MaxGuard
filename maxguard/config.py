from pathlib import Path
from .storage.jsondb import JSONDB
if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
    USER_DATA = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "MaxGuard"
else:
    ROOT = Path(__file__).resolve().parent.parent
    USER_DATA = ROOT

DATA = USER_DATA / "data"
QUARANTINE = USER_DATA / "Quarantine"
LOCALIZATION = ROOT / "localization"

DATA.mkdir(parents=True, exist_ok=True)
QUARANTINE.mkdir(parents=True, exist_ok=True)
class Config:
    def __init__(self):
        self.db = JSONDB(DATA / "settings.json")
        self.data = self.db.read({})
        self.defaults = {
            "language": None, "heuristics": True, "scan_archives": True,
            "realtime": False, "realtime_paths": [], "excluded_paths": [],
            "auto_quarantine": False, "sample_size_mb": 8
        }
        for k,v in self.defaults.items():
            self.data.setdefault(k,v)
        self.save()

    def save(self):
        self.db.write(self.data)
