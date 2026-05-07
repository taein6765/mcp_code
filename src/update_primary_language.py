# Assign primary programming language per repository (filtered language map)

import json

IGNORE_LIST = {
    "HTML", "CSS", "SCSS", "Markdown", "JSON", "YAML", "MDX",
    "Rich Text Format", "TeX", "API Blueprint", "Protocol Buffers",
    "PostScript", "XSLT",

    "Jinja", "EJS", "Nunjucks", "Smarty", "Go Template", "Handlebars",
    "Astro", "Vue", "QML",

    "Dockerfile", "HCL", "Bicep", "Makefile", "Nix", "CMake", "LLVM",
    "Just", "Open Policy Agent",

    "Shell", "Batchfile", "PowerShell", "VBScript",

    "Stylus", "Less", "PLpgSQL", "Jupyter Notebook",
}

def pick_primary_language(languages_map, ignore_list=IGNORE_LIST):
    """
    Returns the top language by byte count, excluding languages in the ignore list.
    Returns None if the map is empty or every language is in the ignore list.
    """
    if not languages_map:
        return None

    filtered = {
        lang: bytes_count
        for lang, bytes_count in languages_map.items()
        if lang not in ignore_list
    }

    if not filtered:
        return None

    return max(filtered.items(), key=lambda x: x[1])[0]

def process_servers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        no_language_count = 0

        for item in data:
            languages_map = item.get('languages', {})
            item['primary_language'] = pick_primary_language(languages_map)
            if item['primary_language'] is None:
                no_language_count += 1

        with open('servers_updated.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print("Successfully updated primary languages!")
        print(f"  {len(data) - no_language_count} servers with a primary language")
        print(f"  {no_language_count} servers with no meaningful language (set to null)")

    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_servers('servers_clean.json')
