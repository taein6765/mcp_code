# MCP tool semantic embedding + visualization pipeline for functional clustering analysis

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE


def main():
    with open("mcp_data.json") as f:
        mcps = json.load(f)

    with open("metadata_mcp-functionality.json") as f:
        meta_mcps = json.load(f)

    mcp_meta_dict = {}

    for item in meta_mcps:
        if item.get("categories"):
            cats = item["categories"]
            cat = cats[0] if isinstance(cats, list) else str(cats)
            mcp_meta_dict[(item["server"], item["name"])] = cat

    data = []

    for m in mcps:
        server = m.get("server_name")

        for t in m.get("tools", []):
            desc = t.get("desc", "")

            if desc:
                data.append({
                    "id": f"{server}::{t.get('name')}",
                    "description": desc,
                    "category": mcp_meta_dict.get((server, t.get("name")), "Unknown"),
                })

    df = pd.DataFrame(data)
    df = df[df["category"] != "Unknown"]

    tfidf = TfidfVectorizer(stop_words="english", max_features=2000)
    X = tfidf.fit_transform(df["description"])

    svd = TruncatedSVD(n_components=min(50, X.shape[1] - 1))
    X_lsa = svd.fit_transform(X)

    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(df) // 3))
    X_2d = tsne.fit_transform(X_lsa)

    df["x"] = X_2d[:, 0]
    df["y"] = X_2d[:, 1]

    plt.figure(figsize=(14, 10))
    sns.scatterplot(
        x="x",
        y="y",
        hue="category",
        data=df,
        alpha=0.7,
        s=50,
    )

    plt.tight_layout()
    plt.savefig("metadata_mcp-tsne.pdf", dpi=300)


if __name__ == "__main__":
    main()