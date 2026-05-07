# Author-level skill distribution analysis for Skills dataset

import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict


def main():
    with open("skills_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    author_skills = defaultdict(int)

    for item in data:
        author = item.get("author", "Unknown")
        author_skills[author] += 1

    total_authors = len(author_skills)
    total_skills = sum(author_skills.values())

    sorted_authors = sorted(
        author_skills.keys(),
        key=lambda a: author_skills[a],
        reverse=True
    )

    k_values = [10, 20, 50]
    table_data = []

    for k in k_values:
        top_k = sorted_authors[:k]
        t_skills = sum(author_skills[a] for a in top_k)

        table_data.append({
            "Top-K Authors": k,
            "Skills Authored": t_skills,
            "Skill Share (%)": (t_skills / total_skills) * 100 if total_skills else 0,
        })

    df_table = pd.DataFrame(table_data)
    print(df_table.to_string(index=False))

    skill_counts = [
        author_skills[a]
        for a in sorted_authors
        if author_skills[a] > 0
    ]

    plt.figure(figsize=(10, 6))
    plt.plot(
        range(1, len(skill_counts) + 1),
        skill_counts,
        marker=".",
        linestyle="none",
    )

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Developer Rank (Log Scale)")
    plt.ylabel("Skills Count (Log Scale)")

    plt.grid(True, which="both", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("metadata_skills-authors.pdf", dpi=300)


if __name__ == "__main__":
    main()