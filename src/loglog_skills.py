# Author-level skill contribution distribution analysis for Skills dataset

import json
from collections import Counter
import matplotlib.pyplot as plt

with open("skills_data.json") as f:
    data = json.load(f)

def normalize_author(a):
    return a.strip().lower()

author_counts = Counter(
    normalize_author(o["author"])
    for o in data
    if o.get("author")
)

freq_counts = Counter(author_counts.values())

x = sorted(freq_counts)
y = [freq_counts[i] for i in x]

plt.figure(figsize=(8, 6))
plt.loglog(x, y, marker="o", linestyle="none", markersize=5, alpha=0.8)

plt.xlabel("Number of Skills per Author")
plt.ylabel("Number of Authors")
plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

plt.tight_layout()
plt.savefig("skills_author_frequency_distribution.png", dpi=300)