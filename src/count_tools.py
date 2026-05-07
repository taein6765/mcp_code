# Tool extraction pipeline for MCP/Skills repositories to compute tool counts across languages.

import ast
import json
import re
from pathlib import Path
from tree_sitter import Language, Parser, Query

def _load(module: str, func: str = "language"):
    try:
        mod = __import__(module, fromlist=[func])
        return Language(getattr(mod, func)())
    except Exception:
        return None

LANGUAGE_LOADERS = {
    "TypeScript": ("tree_sitter_typescript", "language_typescript"),
    "JavaScript": ("tree_sitter_javascript", "language"),
    "Go": ("tree_sitter_go", "language"),
    "Rust": ("tree_sitter_rust", "language"),
    "Java": ("tree_sitter_java", "language"),
    "Kotlin": ("tree_sitter_kotlin", "language"),
    "C#": ("tree_sitter_c_sharp", "language"),
    "Ruby": ("tree_sitter_ruby", "language"),
    "PHP": ("tree_sitter_php", "language_php"),
    "Swift": ("tree_sitter_swift", "language"),
    "Elixir": ("tree_sitter_elixir", "language"),
    "Scala": ("tree_sitter_scala", "language"),
    "Haskell": ("tree_sitter_haskell", "language"),
    "Lua": ("tree_sitter_lua", "language"),
    "C++": ("tree_sitter_cpp", "language"),
    "C": ("tree_sitter_c", "language"),
}

_lang_cache = {}

def get_language(lang: str):
    if lang not in _lang_cache:
        loader = LANGUAGE_LOADERS.get(lang)
        _lang_cache[lang] = _load(*loader) if loader else None
    return _lang_cache[lang]

LANGUAGE_QUERIES = {
    "TypeScript": [
        '(call_expression function: (member_expression property: (property_identifier) @p (#eq? @p "tool"))) @call',
        '(call_expression function: (identifier) @f (#match? @f "^(defineTool|define.+Tool|createTool|registerTool)$")) @call',
        '(object (pair key: [(property_identifier)(string)] @n (#match? @n "^[\'\"]?name[\'\"]?$")) (pair key: [(property_identifier)(string)] @d (#match? @d "^[\'\"]?(description|inputSchema)[\'\"]?$"))) @tool'
    ],
    "JavaScript": [
        '(call_expression function: (member_expression property: (property_identifier) @p (#eq? @p "tool"))) @call',
        '(call_expression function: (identifier) @f (#match? @f "^(defineTool|define.+Tool|createTool|registerTool)$")) @call',
        '(object (pair key: [(property_identifier)(string)] @n (#match? @n "^[\'\"]?name[\'\"]?$")) (pair key: [(property_identifier)(string)] @d (#match? @d "^[\'\"]?(description|inputSchema)[\'\"]?$"))) @tool'
    ],
    "Go": [
        '(call_expression function: (selector_expression field: (field_identifier) @f (#match? @f "^(AddTool|NewTool)$"))) @call',
        '(composite_literal type: (selector_expression field: (field_identifier) @f (#eq? @f "Tool"))) @tool',
        '(composite_literal type: (type_identifier) @t (#eq? @t "Tool")) @tool',
    ],
    "Rust": ['(attribute_item (attribute (identifier) @a (#match? @a "tool"))) @attr'],
    "Java": ['(annotation name: (identifier) @a (#match? @a "Tool")) @ann'],
    "Kotlin": ['(annotation (user_type (type_identifier) @a (#match? @a "Tool"))) @ann'],
    "C#": ['(attribute name: (identifier) @a (#match? @a "Mcp.*Tool")) @attr'],
    "Ruby": ['(call method: (identifier) @m (#match? @m "^(define_tool|tool)$")) @call'],
    "PHP": ['(attribute_list (attribute (name_qualified_name (name) @a (#match? @a "Tool")))) @attr'],
    "Swift": ['(attribute (identifier) @a (#match? @a "MCPTool")) @attr'],
}

REGEX_PATTERNS = {
    "TypeScript": re.compile(r'(?:\.tool\s*\(\s*[\'"])|(?:(?:["\']?name["\']?\s*:\s*[\'"][^\'"]+[\'"]\s*,)\s*["\']?(?:description|inputSchema)["\']?\s*:)'),
    "JavaScript": re.compile(r'(?:\.tool\s*\(\s*[\'"])|(?:(?:["\']?name["\']?\s*:\s*[\'"][^\'"]+[\'"]\s*,)\s*["\']?(?:description|inputSchema)["\']?\s*:)'),
    "Go": re.compile(r'(?:mcp\.NewTool\s*\()|(?:mcp\.Tool\s*\{)|(?:\.AddTool\s*\()'),
    "C#": re.compile(r'\[Mcp(?:Server)?Tool\b'),
    "Java": re.compile(r'@(?:Mcp)?Tool\b'),
    "Kotlin": re.compile(r'@(?:Mcp)?Tool\b'),
    "Rust": re.compile(r'#\[(?:mcp_)?tool\]'),
    "Ruby": re.compile(r'(?:define_tool|tool)\s+[:\'"]'),
    "Swift": re.compile(r'@MCPTool\b'),
}

FILE_EXTENSIONS = {
    "Python": [".py"],
    "TypeScript": [".ts"],
    "JavaScript": [".js", ".mjs", ".cjs"],
    "Go": [".go"],
    "Java": [".java"],
    "Kotlin": [".kt"],
    "Rust": [".rs"],
    "C#": [".cs"],
    "Ruby": [".rb"],
    "Swift": [".swift"],
    "PHP": [".php"],
    "Elixir": [".ex", ".exs"],
    "Scala": [".scala"],
    "Haskell": [".hs"],
    "Lua": [".lua"],
    "C++": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "C": [".c", ".h"],
}

SERVERS_JSON = "servers_final.json"

def is_mcp_tool_decorator(dec, aliases, has_from_import_tool):
    if isinstance(dec, ast.Name):
        return has_from_import_tool and dec.id == "tool"
    target = dec.func if isinstance(dec, ast.Call) else dec
    return isinstance(target, ast.Attribute) and target.attr == "tool"

def count_python_tools(fp: Path) -> int:
    try:
        tree = ast.parse(fp.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return 0

    has_from_import_tool = any(
        isinstance(n, ast.ImportFrom) and n.module == "mcp"
        for n in ast.walk(tree)
    )

    count = 0
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(is_mcp_tool_decorator(d, [], has_from_import_tool) for d in n.decorator_list):
                count += 1
    return count

def count_tools_hybrid(fp: Path, lang: str) -> int:
    try:
        if fp.stat().st_size > 1_000_000:
            return 0
        text = fp.read_text(encoding="utf-8", errors="ignore")
        raw = text.encode()
    except Exception:
        return 0

    ts_count = 0
    language = get_language(lang)

    if language:
        queries = LANGUAGE_QUERIES.get(lang, [])
        parser = Parser(language)
        tree = parser.parse(raw)

        for q in queries:
            try:
                query = Query(language, q)
                ts_count += len(query.captures(tree.root_node))
            except Exception:
                continue

    regex = REGEX_PATTERNS.get(lang)
    regex_count = len(regex.findall(text)) if regex else 0

    return max(ts_count, regex_count)

def get_repo_languages(item):
    langs = item.get("languages")
    if isinstance(langs, dict):
        langs = list(langs.keys())
    elif not isinstance(langs, list):
        langs = []
    if not langs and item.get("primary_language"):
        langs = [item["primary_language"]]
    return [l for l in langs if l in FILE_EXTENSIONS]

def count_tools_in_repo(root: Path, languages):
    total = 0
    for lang in languages:
        seen = set()
        for ext in FILE_EXTENSIONS.get(lang, []):
            for fp in root.rglob(f"*{ext}"):
                if any(x in fp.parts for x in [".git", "node_modules", "dist", "build"]):
                    continue
                r = fp.resolve()
                if r in seen:
                    continue
                seen.add(r)
                total += count_python_tools(fp) if lang == "Python" else count_tools_hybrid(fp, lang)
    return total

def main():
    data = json.load(open(SERVERS_JSON, encoding="utf-8"))

    for item in data:
        root = Path(item.get("local_repo_path", ""))
        if root.exists():
            langs = get_repo_languages(item)
            item["tool_count"] = count_tools_in_repo(root, langs)

    json.dump(data, open(SERVERS_JSON, "w", encoding="utf-8"), indent=2)

if __name__ == "__main__":
    main()