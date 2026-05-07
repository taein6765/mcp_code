# Skills semantic embedding + t-SNE visualization for MCP vs Skills experiments

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE


def main():
    with open("skills_data.json", "r") as f:
        skills = json.load(f)
    with open("metadata_skills-functionality.json", "r") as f:
        meta_skills = json.load(f)

    skill_meta_dict = {}
    for item in meta_skills:
        if item.get("categories"):
            cats = item["categories"]
            skill_meta_dict[item["server"]] = cats[0] if isinstance(cats, list) else str(cats)

    data = []
    for s in skills:
        desc = s.get("description", "")
        if desc:
            data.append(
                {
                    "id": s["id"],
                    "name": s["name"],
                    "description": desc,
                    "category": skill_meta_dict.get(s["id"], "Unknown"),
                }
            )

    df = pd.DataFrame(data)
    df = df[df["category"] != "Unknown"].copy()
    df["category"] = df["category"].astype(str)

    vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
    tfidf = vectorizer.fit_transform(df["description"])

    n_components = min(50, tfidf.shape[1] - 1)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    embeddings = svd.fit_transform(tfidf)

    perplexity = min(30, len(df) // 3)
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
    tsne_emb = tsne.fit_transform(embeddings)

    df["x"] = tsne_emb[:, 0]
    df["y"] = tsne_emb[:, 1]

    plt.figure(figsize=(14, 10))
    sns.scatterplot(
        x="x",
        y="y",
        hue="category",
        palette="tab10",
        data=df,
        alpha=0.7,
        s=50,
    )

    plt.xlabel("t-SNE Dimension 1", fontsize=20)
    plt.ylabel("t-SNE Dimension 2", fontsize=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", title="Category", fontsize=16)
    plt.tight_layout()

    plt.savefig("metadata_skills-tsne.pdf", dpi=300, bbox_inches="tight")


if __name__ == "__main__":
    main()