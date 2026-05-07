# Fetch GitHub repo languages and assign primary language per repository

import json
import os
import time
from urllib.parse import urlparse

import requests

JSON_FILE = "servers.json"
IGNORE_LIST = {
    "HTML", "CSS", "SCSS", "Markdown", "JSON",
    "YAML", "Dockerfile"
}
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

session = requests.Session()
if GITHUB_TOKEN:
    session.headers.update({"Authorization": f"Bearer {GITHUB_TOKEN}"})

session.headers.update(
    {
        "Accept": "application/vnd.github+json",
        "User-Agent": "repo-language-checker",
    }
)


def normalize_url(url):
    return url.lower().rstrip("/")


def github_home(url):
    p = urlparse(normalize_url(url))
    parts = p.path.strip("/").split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def pick_primary_language(languages_map, ignore_list=IGNORE_LIST):
    if not languages_map:
        return None

    filtered = {
        lang: byte_count
        for lang, byte_count in languages_map.items()
        if lang not in ignore_list
    }

    if filtered:
        return max(filtered.items(), key=lambda x: x[1])[0]

    return max(languages_map.items(), key=lambda x: x[1])[0]


def get_repo_languages(owner_repo, cache):
    if owner_repo in cache:
        return cache[owner_repo]

    url = f"https://api.github.com/repos/{owner_repo}/languages"

    while True:
        try:
            r = session.get(url, timeout=20)

            if r.status_code == 404:
                cache[owner_repo] = ("missing", None)
                return cache[owner_repo]

            if r.status_code == 403:
                remaining = r.headers.get("X-RateLimit-Remaining")
                reset = r.headers.get("X-RateLimit-Reset")

                if remaining == "0" and reset:
                    wait_time = max(int(reset) - int(time.time()) + 5, 1)
                    time.sleep(wait_time)
                    continue

                cache[owner_repo] = ("failed", None)
                return cache[owner_repo]

            r.raise_for_status()
            data = r.json() or {}
            cache[owner_repo] = ("ok", data)
            return cache[owner_repo]

        except requests.RequestException:
            cache[owner_repo] = ("failed", None)
            return cache[owner_repo]


def main():
    if not GITHUB_TOKEN:
        print("WARNING: GITHUB_TOKEN is not set. You will hit rate limits quickly.")

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        arr = json.load(f)

    cache = {}
    kept = []
    updated = 0
    removed = 0
    failed = 0

    for idx, item in enumerate(arr, start=1):
        github_url = item.get("github_url")
        if not github_url:
            kept.append(item)
            continue

        owner_repo = github_home(github_url)
        if not owner_repo:
            removed += 1
            continue

        status, languages_map = get_repo_languages(owner_repo, cache)

        if status == "missing":
            removed += 1
            continue

        if status == "failed":
            kept.append(item)
            failed += 1
            continue

        item["languages"] = languages_map
        item["primary_language"] = pick_primary_language(languages_map)

        kept.append(item)
        updated += 1

        if idx % 100 == 0:
            pass

        time.sleep(0.05)

    with open("servers_clean.json", "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2, ensure_ascii=False)

    print(f"Done. Kept {len(kept)} items | updated={updated} | removed={removed} | failed={failed}")


if __name__ == "__main__":
    main()