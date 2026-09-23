from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .analyzer import analyze

class Scanner:
    def __init__(self, config, dbs, on_result=None, on_progress=None):
        self.config = config
        self.dbs = dbs
        self.on_result = on_result
        self.on_progress = on_progress
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

    def files_from(self, paths):
        for base in paths:
            p = Path(base)
            if p.is_file():
                yield p
            elif p.is_dir():
                try:
                    for x in p.rglob("*"):
                        if self.stop_flag: return
                        if x.is_file() and not any(str(x).startswith(str(e)) for e in self.config.data["excluded_paths"]):
                            yield x
                except (PermissionError, OSError):
                    continue

    def scan(self, paths):
        self.stop_flag = False
        files = list(self.files_from(paths))
        total = len(files)
        done = 0
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = []
            signatures = self.dbs["signatures"].read([])
            trusted = self.dbs["trusted"].read([])
            for p in files:
                if self.stop_flag: break
                futures.append(pool.submit(
                    analyze, p,
                    signatures, trusted,
                    self.config.data["heuristics"],
                    self.config.data["scan_archives"],
                    self.config.data["sample_size_mb"]))
            for fut in as_completed(futures):
                if self.stop_flag: break
                r = fut.result()
                done += 1
                if self.on_result: self.on_result(r)
                if self.on_progress: self.on_progress(done, total)
        return done
