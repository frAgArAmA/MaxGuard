import math, os, re, zipfile
from pathlib import Path

MAGIC = {
    b"MZ": "PE executable",
    b"\x7fELF": "ELF executable",
    b"PK\x03\x04": "ZIP/archive",
    b"%PDF": "PDF document",
    b"\x89PNG": "PNG image",
    b"\xff\xd8\xff": "JPEG image"
}
SCRIPT_EXT = {".ps1",".bat",".cmd",".vbs",".vbe",".js",".jse",".wsf",".hta",".py",".psm1"}

def entropy(data):
    if not data: return 0.0
    counts = [0]*256
    for b in data: counts[b] += 1
    n = len(data)
    return -sum((c/n)*math.log2(c/n) for c in counts if c)

def analyze(path, signatures, trusted, heuristics=True, scan_archives=True, sample_mb=8):
    p = Path(path)
    result = {"path": str(p), "status":"CLEAN", "risk":0, "confidence":0,
              "sha256":"", "evidence":[]}
    try:
        h = __import__("hashlib").sha256()
        sample_limit = max(1, int(sample_mb))*1024*1024
        sample = bytearray()
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024*1024)
                if not chunk: break
                h.update(chunk)
                if len(sample) < sample_limit:
                    sample.extend(chunk[:sample_limit-len(sample)])
        result["sha256"] = h.hexdigest()

        if result["sha256"] in trusted:
            result["status"]="TRUSTED"; result["confidence"]=100
            result["evidence"].append("Trusted SHA-256")
            return result

        if result["sha256"] in signatures:
            result["status"]="THREAT"; result["risk"]=100; result["confidence"]=100
            result["evidence"].append("Exact signature match")
            return result

        data = bytes(sample)
        ext = p.suffix.lower()
        head = next((name for magic,name in MAGIC.items() if data.startswith(magic)), None)

        if heuristics:
            if head == "PE executable" and ext not in {".exe",".dll",".scr",".sys",".cpl"}:
                result["risk"] += 25
                result["evidence"].append("Executable content with unusual extension")
            if ext in SCRIPT_EXT:
                result["risk"] += 8
                result["evidence"].append("Script file")
            if re.search(r"\.(pdf|jpg|png|docx|xlsx|zip)\.(exe|scr|bat|cmd|js|vbs|ps1)$", p.name.lower()):
                result["risk"] += 45
                result["evidence"].append("Double extension")
            if head and ext in {".txt",".jpg",".png",".pdf"} and "executable" in head.lower():
                result["risk"] += 20
                result["evidence"].append("Type mismatch")
            e = entropy(data)
            if e >= 7.6:
                result["risk"] += 18
                result["evidence"].append(f"High entropy ({e:.2f})")
            elif e >= 7.1:
                result["risk"] += 8
                result["evidence"].append(f"Elevated entropy ({e:.2f})")
            if ext in SCRIPT_EXT and re.search(rb"(powershell|wscript|cscript|invoke-expression|downloadstring|frombase64string)", data, re.I):
                result["risk"] += 30
                result["evidence"].append("Suspicious script indicators")

        if scan_archives and data.startswith(b"PK\x03\x04"):
            try:
                with zipfile.ZipFile(p) as z:
                    names = z.namelist()
                    suspicious = [n for n in names if Path(n).suffix.lower() in SCRIPT_EXT or Path(n).suffix.lower() in {".exe",".scr"}]
                    if suspicious:
                        result["risk"] += min(25, 5 + len(suspicious)*3)
                        result["evidence"].append(f"Archive contains executable/script entries ({len(suspicious)})")
            except Exception:
                result["evidence"].append("Archive could not be inspected")

        result["risk"] = min(100, result["risk"])
        if result["risk"] >= 80: result["status"]="CRITICAL"
        elif result["risk"] >= 60: result["status"]="HIGH RISK"
        elif result["risk"] >= 40: result["status"]="SUSPICIOUS"
        elif result["risk"] >= 20: result["status"]="LOW RISK"
        else: result["status"]="CLEAN"
        result["confidence"] = min(100, result["risk"] + (25 if len(result["evidence"]) >= 2 else 0))
        return result
    except Exception as e:
        result["status"]="ERROR"; result["evidence"]=[str(e)]
        return result
