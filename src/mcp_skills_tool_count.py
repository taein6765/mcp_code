# MCP/Skills dataset summary table visualization (tools, repos, averages)

import json
import matplotlib.pyplot as plt

def generate_filtered_jpg_table(mcp_file, skills_file):

    with open(mcp_file, "r", encoding="utf-8") as f:
        mcp_data = json.load(f)

    valid_mcp_servers = [s for s in mcp_data if s.get("tool_count", 0) > 0]
    total_mcp_servers = len(valid_mcp_servers)
    total_mcp_tools = sum(s.get("tool_count", 0) for s in valid_mcp_servers)

    avg_tools_per_server = (
        total_mcp_tools / total_mcp_servers if total_mcp_servers else 0
    )

    with open(skills_file, "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    unique_repos = set()

    for skill in skills_data:
        url = skill.get("githubUrl", "")
        if "github.com" in url:
            parts = url.split("/")
            if len(parts) >= 5:
                unique_repos.add("/".join(parts[:5]))

    total_skills_repos = len(unique_repos)
    total_skills = len(skills_data)

    avg_skills_per_repo = (
        total_skills / total_skills_repos if total_skills_repos else 0
    )

    columns = (
        "Dataset",
        "Total Servers / Repos",
        "Tools / Skills",
        "Average per Repo",
    )

    cell_text = [
        [
            "MCP Server",
            f"{total_mcp_servers:,}",
            f"{total_mcp_tools:,}",
            f"{avg_tools_per_server:.2f}",
        ],
        [
            "Skills Repo",
            f"{total_skills_repos:,}",
            f"{total_skills:,}",
            f"{avg_skills_per_repo:.2f}",
        ],
    ]

    fig, ax = plt.subplots(figsize=(9, 2.5))
    ax.axis("off")

    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        loc="center",
        cellLoc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2.0)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#EAEAF2")

    plt.savefig("mcp_skills_dataset.jpg", dpi=300, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    generate_filtered_jpg_table("mcp_data.json", "skills_data.json")