# Clone GitHub skills repos and group by author

import json
import os
import subprocess

json_file = "skills_data.json"
base_dir = "skills_repo"
os.makedirs(base_dir, exist_ok=True)

with open(json_file, "r") as f:
    skills = json.load(f)

repo_db = {}
cloned_count = 0

for i, skill in enumerate(skills, start=1):
    github_url = skill.get("githubUrl") or skill.get("github_url")
    if not github_url:
        continue

    parts = github_url.split("/")
    if "github.com" not in github_url or len(parts) < 5:
        continue

    author = parts[3]
    repo_name = parts[4]
    repo_key = f"{author}_{repo_name}"

    skill_subdir = ""
    if "tree" in parts:
        tree_index = parts.index("tree")
        skill_subdir = "/".join(parts[tree_index + 2:])

    clone_url = f"https://github.com/{author}/{repo_name}.git"

    if repo_key not in repo_db:
        repo_db[repo_key] = {
            "github_url": clone_url,
            "author": author,
            "skills": []
        }

    if skill_subdir and skill_subdir not in repo_db[repo_key]["skills"]:
        repo_db[repo_key]["skills"].append(skill_subdir)

with open("skills_data_by_author.json", "w") as f:
    json.dump({"repos": repo_db}, f, indent=2)

for i, (repo_key, repo_info) in enumerate(repo_db.items(), start=1):
    dest_path = os.path.join(base_dir, repo_key)
    if os.path.exists(dest_path):
        continue

    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_info["github_url"], dest_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    )

    if result.returncode != 0:
        print(f"[ERROR] Failed to clone {repo_key}: {result.stderr.strip()}")

    cloned_count += 1
    if cloned_count % 100 == 0:
        print(f"[MARKER] {cloned_count} repos saved")