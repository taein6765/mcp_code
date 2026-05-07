# Author concentration analysis in MCP metadata for contribution inequality

import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

def main():
    with open("mcp_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    dev_repos = defaultdict(int)
    dev_tools = defaultdict(int)

    for item in data:
        dev = item.get("developer_name", "Unknown")
        dev_repos[dev] += 1
        dev_tools[dev] += item.get("tool_count", 0)

    total_devs = len(dev_repos)
    total_repos = sum(dev_repos.values())
    total_tools = sum(dev_tools.values())

    sorted_devs = sorted(
        dev_repos.keys(),
        key=lambda d: (dev_tools[d], dev_repos[d]),
        reverse=True
    )

    top_1_pct_count = max(1, int(total_devs * 0.01))
    top_1_devs = sorted_devs[:top_1_pct_count]

    top_1_tools_count = sum(dev_tools[d] for d in top_1_devs)
    top_1_repos_count = sum(dev_repos[d] for d in top_1_devs)

    single_repo_devs = sum(1 for d, c in dev_repos.items() if c == 1)

    k_values = [10, 20, 50]
    table_data = []

    for k in k_values:
        top_k = sorted_devs[:k]

        t_tools = sum(dev_tools[d] for d in top_k)
        t_repos = sum(dev_repos[d] for d in top_k)

        table_data.append({
            "Top-K": k,
            "Tools Authored": t_tools,
            "Tool Share (%)": (t_tools / total_tools) * 100 if total_tools else 0,
            "Repos Owned": t_repos,
            "Repo Share (%)": (t_repos / total_repos) * 100 if total_repos else 0
        })

    df_table = pd.DataFrame(table_data)
    print(df_table.to_string(index=False))

    tool_counts = [dev_tools[d] for d in sorted_devs if dev_tools[d] > 0]
    repo_counts = sorted(dev_repos.values(), reverse=True)

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(tool_counts) + 1), tool_counts, marker=".", linestyle="none")
    plt.plot(range(1, len(repo_counts) + 1), repo_counts, marker=".", linestyle="none")

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Developer Rank (Log Scale)")
    plt.ylabel("Count (Log Scale)")

    plt.legend(["Tools", "Repositories"])
    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("metadata_mcp-authors.pdf", dpi=300)

if __name__ == "__main__":
    main()