# Compare MCP tool authors vs skills authors (overlap analysis)

import json
from collections import Counter

def load_authors_mcp(filename):
    with open(filename) as f:
        data = json.load(f)
    return [
        (o["developer_name"].strip().lower(), o.get("tool_count", 0))
        for o in data
        if "developer_name" in o and o["developer_name"]
    ]

def load_authors_skills(filename):
    with open(filename) as f:
        data = json.load(f)
    return [
        (o["author"].strip().lower(), 1)
        for o in data
        if "author" in o and o["author"]
    ]

mcp_data = load_authors_mcp("cleaning/servers_final.json")
skills_data = load_authors_skills("skills_data.json")

# Count contributions
mcp_count = Counter()
for author, tools in mcp_data:
    mcp_count[author] += tools

skills_count = Counter()
for author, cnt in skills_data:
    skills_count[author] += cnt

overlap = set(mcp_count.keys()) & set(skills_count.keys())

print(f"{'Author':<25} {'#MCP Tools':>10} {'#Skills':>10}")
print("-" * 50)
for author in sorted(overlap):
    print(f"{author:<25} {mcp_count[author]:>10} {skills_count[author]:>10}")