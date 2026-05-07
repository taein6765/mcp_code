# Top-author tool concentration analysis for MCP/Skills datasets

import json
from collections import Counter
import matplotlib.pyplot as plt

with open("cleaning/servers_final.json") as f:
    data = json.load(f)

def normalize_author(a):
    return a.strip().lower()

author_counts = Counter()

for o in data:
    if o.get("developer_name"):
        author = normalize_author(o["developer_name"])
        author_counts[author] += o.get("tool_count", 0)

top_authors = author_counts.most_common(40)
authors, counts = zip(*top_authors)

plt.figure(figsize=(10, 5))
plt.bar(authors, counts, edgecolor="black")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.ylabel("Number of Tools")
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.savefig("tools_per_author.png", dpi=300)