# src/ Pipeline Overview

This directory contains scripts for building and analyzing two related datasets: MCP servers/tools and Skills repositories. The pipeline moves from raw data collection → cleaning/normalization → metadata enrichment → similarity analysis → statistical and semantic visualization. Each script has a comment above describing its use and how it fits into the data analysis pipeline. 

---

## 1. Data Collection
Scripts that gather raw data from external sources.

- **Skills API scraper**
  - Collects skill entries from SkillsMP
  - Handles pagination + deduplication
  - Produces `skills_data.json`

- **GitHub language enrichment**
  - Queries GitHub API for repository languages
  - Produces `servers_clean.json`

---

## 2. Repository Processing & Normalization
Scripts that transform raw code into structured representations.

- **Repo cloning script**
  - Groups skills by GitHub repository
  - Clones repositories locally
  - Outputs `skills_repo/` + metadata mappings

- **Code normalizer**
  - Traverses repositories
  - Removes comments / boilerplate
  - Tokenizes and filters content
  - Produces `normalized.json`

---

## 3. Metadata & Labeling
Scripts that enrich datasets with structured attributes.

- **Primary language selector**
  - Filters noisy languages (HTML, JSON, configs)
  - Assigns primary language per repo

- **Tool/functionality classifier (LLM-based)**
  - Classifies tools into functional taxonomy
  - Categories include:
    - data retrieval
    - API interaction
    - file manipulation
    - code execution
    - system operations
    - developer tooling
    - etc.

---

## 4. Similarity & Deduplication Analysis
Scripts that measure overlap between repositories.

- **Pairwise similarity engine**
  - Computes Jaccard similarity (token overlap)
  - Computes SSDeep fuzzy similarity
  - Outputs ranked similarity pairs

- **Cross-dataset comparison**
  - Analyzes similarity distributions
  - Produces histograms and summary stats

---

## 5. Author-Level Analysis
Scripts that study contribution concentration.

- MCP author aggregation
  - Tools per developer
  - Top-K contribution concentration
  - Rank-frequency distributions

- Skills author aggregation
  - Skills per contributor
  - Inequality / concentration plots

---

## 6. Statistical & Structural Analysis
Scripts focused on dataset properties.

- Token length analysis
  - Measures description length distributions
  - Histograms for MCP and Skills datasets

- Dataset summary tables
  - MCP vs Skills comparisons:
    - total entities
    - total tools/skills
    - averages per entity

---

## 7. Semantic Visualization
Scripts that embed and visualize content structure.

- MCP t-SNE visualization
  - TF-IDF → SVD → t-SNE pipeline
  - Category-colored scatter plot

- Skills t-SNE visualization
  - Same embedding pipeline applied to skills dataset

---

## 8. Similarity Distribution Visualization
Scripts for interpreting similarity results.

- Histogram generation for:
  - Jaccard similarity
  - SSDeep similarity
- Log-scale frequency plots

---
