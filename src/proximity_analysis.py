# Analyze and visualize Jaccard + SSDeep similarity distributions across repo pairs

import json
import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

#with open("similarity_scores.json") as f:
#with open("similarity_scores_skills.json") as f:
with open("proximity_scores_cross.json") as f:
    data = json.load(f)

proximities1 = [item["jaccard"] for item in data if "jaccard" in item]
proximities2 = [item["ssdeep"] for item in data if "ssdeep" in item]

if not proximities1 or not proximities2:
    print("No proximity values found.")
    exit()

proximities1 = np.array(proximities1)
proximities2 = np.array(proximities2)

print("=== Summary Stats (Jaccard) ===")
print("count:", len(proximities1))
print("mean:", np.mean(proximities1))
print("median:", np.median(proximities1))
print("std:", np.std(proximities1))
print("min:", np.min(proximities1))
print("max:", np.max(proximities1))

print("\n=== Summary Stats (SSDeep) ===")
print("count:", len(proximities2))
print("mean:", np.mean(proximities2))
print("median:", np.median(proximities2))
print("std:", np.std(proximities2))
print("min:", np.min(proximities2))
print("max:", np.max(proximities2))

print("\n=== Bucketed Distribution (Jaccard) ===")
bins = [0, 1, 2, 3, 5, 10, float("inf")]
counts1 = [0] * (len(bins) - 1)

for p in proximities1:
    for i in range(len(bins) - 1):
        if bins[i] <= p < bins[i+1]:
            counts1[i] += 1
            break

for i in range(len(counts1)):
    print(f"{bins[i]}-{bins[i+1]}: {counts1[i]}")

print("\n=== Bucketed Distribution (SSDeep) ===")
counts2 = [0] * (len(bins) - 1)

for p in proximities2:
    for i in range(len(bins) - 1):
        if bins[i] <= p < bins[i+1]:
            counts2[i] += 1
            break

for i in range(len(counts2)):
    print(f"{bins[i]}-{bins[i+1]}: {counts2[i]}")

print("\n=== Top 10 Highest Proximity Pairs (Jaccard) ===")
top1 = sorted(data, key=lambda x: x.get("jaccard", 0), reverse=True)[:10]
for item in top1:
    print(item["repo1"], "<->", item["repo2"], ":", item["jaccard"])

print("\n=== Top 10 Highest Proximity Pairs (SSDeep) ===")
top2 = sorted(data, key=lambda x: x.get("ssdeep", 0), reverse=True)[:10]
for item in top2:
    print(item["repo1"], "<->", item["repo2"], ":", item["ssdeep"])

plt.figure(figsize=(6,4))
plt.hist(proximities1, bins=30, edgecolor='black')
plt.yscale("log")  # log scale on frequency
plt.xlabel("Jaccard Similarity", fontsize=12)
plt.ylabel("Frequency (log scale)", fontsize=12)
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()

#plt.savefig("proximity_histogram_skills_jaccard.png", dpi=300)
plt.savefig("proximity_histogram_cross_jaccard.png")

plt.figure(figsize=(6,4))
plt.hist(proximities2, bins=30, edgecolor='black')
plt.yscale("log")  # log scale on frequency
plt.xlabel("SSDeep Similarity", fontsize=12)
plt.ylabel("Frequency (log scale)", fontsize=12)
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()

#plt.savefig("proximity_histogram_skills_ssdeep.png", dpi=300)
plt.savefig("proximity_histogram_cross_ssdeep.png")
