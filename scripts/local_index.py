#!/usr/bin/env python3
"""Print a compact JSON index of what is already on disk, for canvas_scan.js.

Output: {"config": {...}, "index": {"<term folder>/<COURSE>": ["lowercased name", ...]}}
(paste it in place of __DATA__ in canvas_scan.js)
Every file AND folder name anywhere under a course folder counts as "already have",
so files the user moved into subfolders (hw/, week 2 data/ ...) are not re-downloaded,
and a folder named like a zip's stem means that zip was already extracted.
"""
import json, os, sys, unicodedata
import config

CFG = config.load()
ROOT = CFG["root"]
# Files the user said they don't want (e.g. big files they declined), one per line:
#   大二秋季/ACCT2200/Alibaba_annual report_2024.pdf
IGNORE = os.path.join(ROOT, ".canvas_sync_ignore")


def main():
    index = {}
    for term in sorted(os.listdir(ROOT)):
        tdir = os.path.join(ROOT, term)
        # only semester folders like 大二秋季 — canvas_scan.js only ever looks those up
        if not os.path.isdir(tdir) or not term.endswith("季"):
            continue
        for course in sorted(os.listdir(tdir)):
            cdir = os.path.join(tdir, course)
            if not os.path.isdir(cdir) or course.startswith("."):
                continue
            names = set()
            for _, dirs, files in os.walk(cdir):
                names.update(d.lower() for d in dirs)
                names.update(f.lower() for f in files if not f.startswith((".", "~$")))
            index[f"{term}/{course}"] = names
    if os.path.exists(IGNORE):
        for line in open(IGNORE, encoding="utf-8"):
            key, _, name = line.strip().rpartition("/")
            if key and name:
                index.setdefault(key, set()).add(name.lower())
    # macOS may store names decomposed (NFD) while Canvas sends NFC; compare in NFC
    nfc = lambda x: unicodedata.normalize("NFC", x)
    index = {nfc(k): sorted({nfc(n) for n in v}) for k, v in index.items()}
    data = {"config": {"entry_year": CFG["entry_year"], "max_mb": CFG["max_mb"]}, "index": index}
    json.dump(data, sys.stdout, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
