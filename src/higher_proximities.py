# High-threshold graph analysis of MCP/Skills similarity networks for strong cloning structure

import json
from collections import defaultdict, deque

input_files = [
    "similarity_scores.json",
    "similarity_scores_skills.json",
    "proximity_scores_cross.json"
]

JACCARD_THRESHOLD = 80
SSDEEP_THRESHOLD = 80

def build_graph(data, metric, threshold):
    graph = defaultdict(set)

    for item in data:
        if item.get(metric, 0) >= threshold:
            a = item["repo1"]
            b = item["repo2"]
            graph[a].add(b)
            graph[b].add(a)

    return graph

def largest_component_size(graph):
    visited = set()
    best = 0

    for node in graph:
        if node in visited:
            continue

        q = deque([node])
        visited.add(node)
        size = 0

        while q:
            cur = q.popleft()
            size += 1
            for nei in graph[cur]:
                if nei not in visited:
                    visited.add(nei)
                    q.append(nei)

        best = max(best, size)

    return best

def compute_metrics(data, metric, threshold):
    graph = build_graph(data, metric, threshold)
    return len(graph), largest_component_size(graph)

for file in input_files:
    with open(file) as f:
        data = json.load(f)

    for metric in ["jaccard", "ssdeep"]:
        threshold = JACCARD_THRESHOLD if metric == "jaccard" else SSDEEP_THRESHOLD
        repos, cluster = compute_metrics(data, metric, threshold)