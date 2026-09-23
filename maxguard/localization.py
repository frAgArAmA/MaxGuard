import json
from pathlib import Path

class I18N:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.lang = "en"
        self.data = {}
        self.load("en")

    def load(self, lang):
        path = self.folder / f"{lang}.json"
        if not path.exists():
            lang = "en"
            path = self.folder / "en.json"
        self.lang = lang
        self.data = json.loads(path.read_text(encoding="utf-8"))
        return self.data

    def t(self, key):
        return self.data.get(key, key)
