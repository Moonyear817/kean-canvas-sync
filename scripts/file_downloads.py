#!/usr/bin/env python3
"""Move files Chrome downloaded from Canvas into the course folders.

    python3 file_downloads.py <todo.tsv> <start_epoch_seconds> [--wait 120]

todo.tsv rows: key<TAB>id<TAB>size<TAB>name   (key = "大二秋季/ACCT2200")
start_epoch: time the downloads were started; only files in ~/Downloads modified
after it are considered, so an older same-named file the user kept there
(maybe an edited copy) is never picked up or touched.

A downloaded file matches a row when its name is the row's name or Chrome's
duplicate form "stem (N).ext", AND its byte size equals the Canvas size.
Zips are also extracted into a same-name folder next to them.
Prints a JSON report: moved / already_there / missing.
"""
import json, os, re, shutil, sys, time, unicodedata, zipfile
import config

ROOT = config.load()["root"]
DL = os.path.expanduser("~/Downloads")


def candidates(name, size, start):
    nfc = lambda x: unicodedata.normalize("NFC", x)
    stem, ext = os.path.splitext(nfc(name))
    pat = re.compile(r"^" + re.escape(stem) + r"( \(\d+\))?" + re.escape(ext) + r"$")
    out = []
    for f in os.listdir(DL):
        p = os.path.join(DL, f)
        if pat.match(nfc(f)) and os.path.isfile(p):
            st = os.stat(p)
            if st.st_size == size and st.st_mtime >= start:
                out.append((st.st_mtime, p))
    return [p for _, p in sorted(out, reverse=True)]


def main():
    todo_path, start = sys.argv[1], float(sys.argv[2])
    wait = int(sys.argv[sys.argv.index("--wait") + 1]) if "--wait" in sys.argv else 120
    rows = []
    for line in open(todo_path, encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 4:
            rows.append((parts[0], parts[1], int(parts[2]), os.path.basename(parts[3])))

    # wait for Chrome to finish (no .crdownload left and every file present), up to `wait` s
    deadline = time.time() + wait
    while time.time() < deadline:
        busy = any(f.endswith(".crdownload") for f in os.listdir(DL))
        pending = [r for r in rows
                   if not os.path.exists(os.path.join(ROOT, r[0], r[3])) and not candidates(r[3], r[2], start)]
        if not busy and not pending:
            break
        time.sleep(3)

    report = {"moved": [], "already_there": [], "missing": [], "extracted": []}
    for key, fid, size, name in rows:
        dest_dir = os.path.join(ROOT, key)
        dest = os.path.join(dest_dir, name)
        existing = {unicodedata.normalize("NFC", f) for f in os.listdir(dest_dir)} if os.path.isdir(dest_dir) else set()
        if unicodedata.normalize("NFC", name) in existing:
            report["already_there"].append(f"{key}/{name}")
            continue
        found = candidates(name, size, start)
        if not found:
            report["missing"].append({"key": key, "id": fid, "name": name})
            continue
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(found[0], dest)
        report["moved"].append(f"{key}/{name}")
        if name.lower().endswith(".zip"):
            out_dir = os.path.join(dest_dir, os.path.splitext(name)[0])
            try:
                with zipfile.ZipFile(dest) as z:
                    z.extractall(out_dir)
                shutil.rmtree(os.path.join(out_dir, "__MACOSX"), ignore_errors=True)
                report["extracted"].append(f"{key}/{os.path.splitext(name)[0]}/")
            except zipfile.BadZipFile:
                pass
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
