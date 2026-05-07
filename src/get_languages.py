# Counts primary languages across MCP/Skills repositories for dataset analysis

import json
from collections import Counter


def get_unique_languages(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        language_counts = Counter()

        for item in data:
            lang = item.get("primary_language")
            if lang:
                language_counts[lang] += 1

        print("Unique Primary Languages:")
        print("-" * 35)
        print(f"{'Language':<20} {'Repos':>6}")
        print("-" * 35)
        for language in sorted(language_counts.keys()):
            print(f"{language:<20} {language_counts[language]:>6}")
        print("-" * 35)
        print(f"{'Total':<20} {sum(language_counts.values()):>6}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{file_path}'.")


if __name__ == "__main__":
    get_unique_languages("mcp_data.json")