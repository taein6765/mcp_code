# Tool description length analysis for MCP dataset metadata quality assessment

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
    with open("mcp_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    token_lengths = []

    for server in data:
        for tool in server.get("tools", []):
            desc = clean_text(tool.get("desc", ""))

            if desc:
                token_lengths.append(len(desc.split()))

    plt.figure(figsize=(10, 6))
    plt.hist(token_lengths, bins=50, edgecolor="black")

    plt.xlabel("Token Length")
    plt.ylabel("Frequency")

    plt.grid(axis="y", alpha=0.75, linestyle="--")
    plt.tight_layout()

    plt.savefig("metadata_mcp-tool-desc.pdf", dpi=300)

if __name__ == "__main__":
    main()