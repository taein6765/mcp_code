"""
normalize_repos.py

For each repository folder, recursively extract source files and produce
a normalized, concatenated text representation suitable for similarity
estimation or other NLP tasks.

Normalization steps:
  1. Skip excluded directories (.git, node_modules, dist, build, __pycache__, …)
  2. Skip binary / archive file extensions
  3. Strip comments using language-aware rules (keyed by file extension)
  4. Collapse whitespace and lowercase
  5. Discard repositories with fewer than --min-tokens normalized tokens

Output: a single JSON file (--output-json) with structure:
  {
    "metadata": { "total_repos": N, "kept": K, "skipped": S, "min_tokens": T },
    "repositories": [
      { "repo_name": "…", "token_count": N, "kept": true/false, "normalized_text": "…" },
      …
    ]
  }
  Skipped repos have normalized_text set to "" to keep file size manageable.

Usage:
    python normalize_repos.py \\
        --repos-dir  ./repos \\
        --output-json ./normalized.json \\
        [--min-tokens 50] [--verbose]
"""

# MCP repository normalization and tokenization pipeline for MCP vs Skills experiments

import argparse
import json
import os
import re
import sys
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__",
    ".tox", ".venv", "venv", "env", ".mypy_cache", ".pytest_cache",
    "target", "out", ".gradle", "vendor", "_build", "deps",
    ".stack-work", "pkg", "bin", "obj",
    ".dart_tool", ".pub-cache",
}

EXCLUDED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".wasm",
    ".class", ".jar",
    ".pyc", ".o", ".obj",
    ".mp3", ".mp4", ".wav",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".db", ".sqlite", ".sqlite3",
}

EXCLUDED_FILENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Cargo.lock", "go.sum",
    "poetry.lock", "Pipfile.lock",
    "flake.lock",
}

MIN_TOKENS = 50

_PAT = {
    "c_block": re.compile(r"/\*.*?\*/", re.DOTALL),
    "c_line": re.compile(r"//[^\n]*"),
    "hash_line": re.compile(r"#[^\n]*"),
    "py_doc": re.compile(r'""".*?"""|\'\'\'.*?\'\'\'', re.DOTALL),
}

def _apply(text, *keys):
    for k in keys:
        text = _PAT[k].sub(" ", text)
    return text

def _python(t): return _apply(t, "py_doc", "hash_line")
def _c_style(t): return _apply(t, "c_block", "c_line")
def _hash(t): return _apply(t, "hash_line")
def _fallback(t): return _apply(t, "c_block", "c_line", "hash_line")

EXT_TO_STRIPPER = {
    ".py": _python,
    ".c": _c_style, ".cpp": _c_style, ".h": _c_style,
    ".js": _c_style, ".ts": _c_style,
    ".go": _c_style, ".rs": _c_style,
    ".java": _c_style,
    ".rb": _hash, ".sh": _hash,
    ".json": lambda x: x,
}

WS_RE = re.compile(r"\s+")

def normalize(text, ext):
    fn = EXT_TO_STRIPPER.get(ext.lower(), _fallback)
    text = fn(text).lower()
    return WS_RE.sub(" ", text).strip()

def count_tokens(text):
    return len(text.split()) if text else 0

def is_text(path: Path):
    try:
        chunk = path.read_bytes()[:8192]
        return b"\x00" not in chunk
    except Exception:
        return False

def iter_files(repo):
    for d, ds, fs in os.walk(repo):
        ds[:] = [x for x in ds if x not in EXCLUDED_DIRS]
        for f in fs:
            p = Path(d) / f
            if f in EXCLUDED_FILENAMES:
                continue
            if p.suffix in EXCLUDED_EXTENSIONS:
                continue
            if not is_text(p):
                continue
            yield p

def process(repo):
    parts = []
    for f in iter_files(repo):
        try:
            raw = f.read_text(errors="ignore")
            parts.append(normalize(raw, f.suffix))
        except Exception:
            continue
    text = " ".join(parts)
    return text, count_tokens(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repos-dir", type=Path, required=True)
    ap.add_argument("--output-json", type=Path, required=True)
    ap.add_argument("--min-tokens", type=int, default=MIN_TOKENS)
    args = ap.parse_args()

    repos = sorted([p for p in args.repos_dir.iterdir() if p.is_dir()])
    out = []
    kept = skipped = 0

    for r in repos:
        text, n = process(r)
        ok = n >= args.min_tokens

        out.append({
            "repo_name": r.name,
            "token_count": n,
            "kept": ok,
            "normalized_text": text if ok else ""
        })

        if ok:
            kept += 1
        else:
            skipped += 1

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps({
        "metadata": {
            "total": len(out),
            "kept": kept,
            "skipped": skipped
        },
        "repositories": out
    }, indent=2))

if __name__ == "__main__":
    main()