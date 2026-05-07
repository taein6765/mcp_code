# Scrape SkillsMP API (alphabetical queries with pagination + dedup)

import requests
import json
import os
import string

if os.path.exists("skills_data.json"):
    with open("skills_data.json", "r") as f:
        all_skills = json.load(f)
else:
    all_skills = []

seen = {
    s.get("githubUrl")
    for s in all_skills
    if isinstance(s, dict) and s.get("githubUrl")
}

for q in string.ascii_lowercase:  # a → z
    page = 1
    print(f"\n=== query: {q} ===")

    while True:
        response = requests.get(
            "https://skillsmp.com/api/v1/skills/search",
            params={"q": q, "page": page, "limit": 100},
            headers={"Authorization": "Bearer sk_live_skillsmp_z2I7D8U7dmq37u9rizOAvZ4iGhgeoOf0IKhbVARkzT4"}
        )
        data = response.json()

        added = 0
        for s in data["data"]["skills"]:
            url = s.get("githubUrl")
            if url and url not in seen:
                seen.add(url)
                all_skills.append(s)
                added += 1

        with open("skills_data.json", "w") as f:
            json.dump(all_skills, f, indent=2)

        print(f"query {q} | page {page}: +{added} (total {len(all_skills)})")

        if not data["data"]["pagination"]["hasNext"]:
            break

        page += 1

