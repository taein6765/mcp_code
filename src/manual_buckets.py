# Bucketed sampling of similarity scores for MCP/Skills clone validation analysis

import json
import random

INPUT_FILE = "similarity_scores.json"
N = 20

BUCKETS = [
    (0, 20),
    (20, 40),
    (40, 60),
    (60, 80),
    (80, 101)
]

def load_data(path):
    with open(path, "r") as f:
        return json.load(f)

def bucketize(data):
    buckets = {b: [] for b in BUCKETS}

    for entry in data:
        value = entry.get("ssdeep")
        if value is None:
            continue

        for b in BUCKETS:
            low, high = b
            if low <= value < high:
                buckets[b].append(entry)
                break

    return buckets

def sample_buckets(buckets, n):
    sampled = {}

    for b, items in buckets.items():
        sampled[b] = items if len(items) <= n else random.sample(items, n)

    return sampled

def main():
    data = load_data(INPUT_FILE)
    buckets = bucketize(data)
    sample_buckets(buckets, N)

if __name__ == "__main__":
    main()