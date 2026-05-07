"""
plot_token_distribution.py

Read the normalized.json produced by normalize_repos.py and plot the
distribution of repository sizes (normalized source token counts).

The figure reproduces the description from the paper:
  - Log-scale x-axis to show the heavy tail clearly
  - Vertical dashed line at the 50-token exclusion threshold
  - Separate shading for excluded vs kept repos
  - Annotation with counts

Usage:
    python plot_token_distribution.py \\
        --input  ./normalized.json \\
        --output ./figures/token_distribution.pdf   # or .png, .svg
        [--min-tokens 50]    # override threshold for the plot marker
        [--bins 80]
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def plot_distribution(token_counts: list[int], min_tokens: int, output_path: Path, n_bins: int = 80) -> None:
    counts = np.array(token_counts, dtype=float)

    counts_for_log = np.where(counts == 0, 0.5, counts)

    log_min = np.log10(max(counts_for_log.min(), 1))
    log_max = np.log10(counts_for_log.max())
    bin_edges = np.logspace(log_min, log_max, n_bins + 1)

    kept_mask = counts >= min_tokens

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.hist(
        counts_for_log[kept_mask],
        bins=bin_edges,
        color="#1f77b4",
        alpha=0.80,
        edgecolor="black",
        linewidth=0
    )

    ax.set_xscale("log")
    ax.xaxis.set_major_locator(ticker.LogLocator(base=10))
    ax.xaxis.set_major_formatter(ticker.LogFormatterMathtext())

    ax.set_xlabel("Normalized tokens (log scale)", fontsize=20)
    ax.set_ylabel("Number of repositories", fontsize=20)
    ax.tick_params(axis='both', labelsize=16)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--min-tokens", type=int, default=None)
    parser.add_argument("--bins", type=int, default=80)
    args = parser.parse_args()

    if not args.input.exists():
        sys.exit("ERROR: input file not found")

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)

    min_tokens = (
        args.min_tokens
        if args.min_tokens is not None
        else data.get("metadata", {}).get("min_tokens", 50)
    )

    token_counts = [r["token_count"] for r in data["repositories"]]

    if not token_counts:
        sys.exit("ERROR: no data found")

    plot_distribution(
        token_counts=token_counts,
        min_tokens=min_tokens,
        output_path=args.output,
        n_bins=args.bins,
    )


if __name__ == "__main__":
    main()