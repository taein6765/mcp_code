# GitHub repository cloning pipeline for MCP dataset construction

import json
import os
import subprocess

json_file = "all_servers_clean.json"
base_dir = "mcp_repo"
os.makedirs(base_dir, exist_ok=True)

with open(json_file, "r") as f:
    skills = json.load(f)

repo_db = {}
cloned_count = 0

for skill in skills:
    github_url = skill.get("githubUrl") or skill.get("github_url")
    if not github_url:
        continue

    github_url = github_url.rstrip("/").replace(".git", "")
    parts = github_url.split("/")

    if "github.com" not in github_url or len(parts) < 5:
        continue

    author = parts[3]
    repo_name = parts[4]
    repo_key = f"{author}_{repo_name}"

    if repo_key not in repo_db:
        repo_db[repo_key] = {
            "github_url": f"https://github.com/{author}/{repo_name}.git"
        }

for repo_key, repo_info in repo_db.items():
    dest_path = os.path.join(base_dir, repo_key)

    if os.path.exists(dest_path):
        continue

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_info["github_url"], dest_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    )

    cloned_count += 1