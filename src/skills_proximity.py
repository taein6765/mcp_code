# Compute pairwise similarity between skills repositories (ssdeep + Jaccard)

import os
import re
import json
import hashlib
import pyssdeep as ssdeep
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, "../skills_repo")
BASE_DIR = os.path.abspath(BASE_DIR)
OUTPUT_FILE = "similarity_scores_skills.json"

EXCLUDE_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__",
    ".next", ".cache", "out", "coverage", "venv", ".venv"
}

EXCLUDE_EXTS = {
    ".lock", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".tar", ".gz",
    ".pdf", ".mp4", ".mp3", ".woff", ".woff2", ".ttf", ".ico",
    ".exe", ".dll", ".so", ".dylib", ".bin", ".class",
    ".md", ".json"
}

EXCLUDE_FILENAMES = {
    "license", "license.txt", "license.md",
    "readme", "readme.md", "readme.txt",
    "copying", "copying.txt",
    "changelog", "changelog.md",
    ".gitignore", ".gitignore.txt", ".gitignore.md"
}


def get_author(folder):
    return folder.split("_")[0]


def get_repo_name(folder):
    parts = folder.split("_", 1)
    return parts[1] if len(parts) > 1 else folder


def get_github_link(folder):
    author = get_author(folder)
    repo = get_repo_name(folder)
    return f"https://github.com/{author}/{repo}"


def should_skip_file(filename):
    name = filename.lower()

    if name in EXCLUDE_FILENAMES:
        return True

    if any(name.endswith(ext) for ext in EXCLUDE_EXTS):
        return True

    if name.endswith(".min.js") or name.endswith(".min.css"):
        return True

    return False


def normalize(text):
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"#.*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def tokenize(text):
    return set(re.findall(r"\b\w+\b", text))


def jaccard(set1, set2):
    if not set1 or not set2:
        return 0
    return int(100 * len(set1 & set2) / len(set1 | set2))


def sha256_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def read_repo(path):
    contents = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for f in files:
            if should_skip_file(f):
                continue

            file_path = os.path.join(root, f)
            try:
                with open(file_path, "r", errors="ignore") as file:
                    contents.append(file.read())
            except Exception:
                continue

    raw = "\n".join(contents)
    norm = normalize(raw)
    tokens = tokenize(norm)
    return norm, tokens


repos = []

for folder in tqdm(os.listdir(BASE_DIR), desc="Indexing repos"):
    path = os.path.join(BASE_DIR, folder)
    if not os.path.isdir(path):
        continue

    author = get_author(folder)

    try:
        norm_text, tokens = read_repo(path)

        if len(norm_text) < 50:
            tqdm.write(f"Skipping {folder}, too short")
            continue

        try:
            buffer = norm_text.encode('utf-8')
            fuzzy_hash = ssdeep.fuzzy_hash_buf(buffer, len(buffer))
        except Exception as e:
            tqdm.write(f"ssdeep failed for {folder}: {e}")
            continue

        repos.append({
            "name": folder,
            "author": author,
            "github": get_github_link(folder),
            "sha256": sha256_hash(norm_text),
            "fuzzy": fuzzy_hash,
            "tokens": tokens
        })

    except Exception as e:
        tqdm.write(f"Error processing {folder}: {str(e)}")
        continue

tqdm.write(f"Loaded {len(repos)} repos")

results = []
n = len(repos)

for i in tqdm(range(n), desc="Pairwise comparisons"):
    r1 = repos[i]
    for j in range(i + 1, n):
        r2 = repos[j]

        if r1["author"] == r2["author"]:
            continue

        if r1["sha256"] == r2["sha256"]:
            ss_score = 100
            jac_score = 100
        else:
            ss_score = ssdeep.fuzzy_compare(r1["fuzzy"], r2["fuzzy"])
            jac_score = jaccard(r1["tokens"], r2["tokens"])

        results.append({
            "repo1": r1["name"],
            "repo2": r2["name"],
            "author1": r1["author"],
            "author2": r2["author"],
            "github1": r1["github"],
            "github2": r2["github"],
            "ssdeep": ss_score,
            "jaccard": jac_score
        })

results.sort(key=lambda x: -(x["ssdeep"] + x["jaccard"]))

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

tqdm.write(f"Saved {len(results)} pairs to {OUTPUT_FILE}")