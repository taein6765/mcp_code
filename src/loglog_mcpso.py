# Author-level tool contribution distribution analysis for MCP/Skills datasets

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

freq_counts = Counter(author_counts.values())

x = sorted(freq_counts)
y = [freq_counts[i] for i in x]

plt.figure(figsize=(8, 6))
plt.loglog(x, y, marker="o", linestyle="none", markersize=5, alpha=0.8)

plt.xlabel("Number of Tools per Author")
plt.ylabel("Number of Authors")
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

plt.tight_layout()
plt.savefig("mcp_author_frequency_distribution.png", dpi=300)