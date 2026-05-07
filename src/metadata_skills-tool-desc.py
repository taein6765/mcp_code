# Skills tool description length distribution analysis (MCP vs Skills experiments)

import json
import re
import matplotlib.pyplot as plt


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main():
    with open("skills_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    token_lengths = []
    for tool in data:
        desc = tool.get("description", "")
        cleaned_desc = clean_text(desc)
        if cleaned_desc:
            token_lengths.append(len(cleaned_desc.split()))

    plt.figure(figsize=(10, 6))
    plt.hist(token_lengths, bins=50, color="skyblue", edgecolor="black")
    plt.xlabel("Token Length", fontsize=20)
    plt.ylabel("Frequency", fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.grid(axis="y", alpha=0.75, linestyle="--")

    plt.tight_layout()
    plt.savefig("metadata_skills-tool-desc.pdf", dpi=300)


if __name__ == "__main__":
    main()