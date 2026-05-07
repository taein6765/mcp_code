# Plot skills per author (top frequency distribution)

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
    if "author" in o and o["author"]
)

top_authors = author_counts.most_common(40)
authors, counts = zip(*top_authors)

plt.figure(figsize=(10, 5))
plt.bar(authors, counts, edgecolor='black')
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.ylabel("Number of Skills", fontsize=12)
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.savefig("skills_per_author.png", dpi=300)
# plt.show()
