"""Load the skill's config.json (falls back to config.example.json)."""
import json, os

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    for name in ("config.json", "config.example.json"):
        p = os.path.join(SKILL_DIR, name)
        if os.path.exists(p):
            cfg = json.load(open(p, encoding="utf-8"))
            cfg["root"] = os.path.expanduser(cfg["root"])
            return cfg
    raise SystemExit("config.json not found — copy config.example.json to config.json")
