import os, re, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "fastapi": [r"\bFastAPI\s*\(", r"from\s+fastapi\s+import\s+FastAPI"],
    "flask": [r"\bFlask\s*\(", r"from\s+flask\s+import\s+Flask"],
    "django": [r"DJANGO_SETTINGS_MODULE", r"from\s+django"],
    "sqlalchemy": [r"from\s+sqlalchemy", r"\bcreate_engine\s*\("],
    "alembic": [r"\balembic\.ini\b", r"\bversions\b"],
    "prisma": [r"\bschema\.prisma\b", r"@prisma/client"],
    "node_express": [r"\bexpress\s*\(", r"require\(['\"]express['\"]\)"],
    "docker": [r"\bDockerfile\b", r"\bdocker-compose\.yml\b|\bdocker-compose\.yaml\b"],
}
ROUTE_PATTERNS = [
    ("fastapi_route", r"@app\.(get|post|put|patch|delete)\(\s*['\"]([^'\"]+)['\"]"),
    ("flask_route", r"@app\.route\(\s*['\"]([^'\"]+)['\"]"),
    ("django_url", r"path\(\s*['\"]([^'\"]+)['\"]"),
]
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
def iter_files():
    for p in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix.lower() in {".py",".ts",".tsx",".js",".cjs",".mjs",".json",".yml",".yaml",".ini",".toml",".md"}:
            yield p
def scan_text(p: Path, max_bytes=2_000_000):
    try:
        data = p.read_bytes()
        if len(data) > max_bytes:
            return ""
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""
def main():
    hits = {"frameworks": {}, "routes": [], "db_candidates": [], "files": []}
    for p in iter_files():
        rel = str(p.relative_to(ROOT))
        text = scan_text(p)
        if not text:
            continue
        hits["files"].append(rel)
        # framework hints
        for k, regs in PATTERNS.items():
            for r in regs:
                if re.search(r, text):
                    hits["frameworks"].setdefault(k, 0)
                    hits["frameworks"][k] += 1
        # route hints
        if p.suffix.lower() in {".py"}:
            for kind, r in ROUTE_PATTERNS:
                for m in re.finditer(r, text):
                    if kind == "fastapi_route":
                        hits["routes"].append({"kind": kind, "method": m.group(1), "path": m.group(2), "file": rel})
                    else:
                        hits["routes"].append({"kind": kind, "path": m.group(1), "file": rel})
        # db candidates
        if any(x in rel.lower() for x in ["alembic", "migrations", "schema.prisma", "database", "db", "models"]):
            if rel not in hits["db_candidates"]:
                hits["db_candidates"].append(rel)
    print("# Local Repo Architecture Report")
    print()
    print("## Framework / tool signals (heuristic counts)")
    print("```json")
    print(json.dumps(hits["frameworks"], indent=2, sort_keys=True))
    print("```")
    print()
    print("## Discovered route-like patterns (heuristic)")
    print("```json")
    print(json.dumps(hits["routes"][:200], indent=2))
    print("```")
    if len(hits["routes"]) > 200:
        print(f"\n(Truncated: {len(hits['routes'])} total route hits)\n")
    print()
    print("## DB & schema candidate paths")
    for path in sorted(hits["db_candidates"])[:200]:
        print(f"- {path}")
    print()
    print("## Next step instructions")
    print("1) Paste this report back into ChatGPT.")
    print("2) Tell me what DB you use (Postgres? SQLite?) and how you run the API locally.")
    print()
if __name__ == "__main__":
    main()
