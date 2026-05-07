# Tool taxonomy classification pipeline for MCP/Skills dataset analysis using LLMs

import json
import random
import os
import re
import time
from typing import List, Literal
from pydantic import BaseModel
import litellm


TaxonomyCategory = Literal[
    "data retrieval",
    "API interaction",
    "file manipulation",
    "database access",
    "code execution",
    "communication",
    "system operations",
    "developer tooling",
    "other",
]


class ToolClassification(BaseModel):
    categories: List[TaxonomyCategory]
    reasoning: str


SYSTEM_PROMPT = """
You are a tool classification engine.

Assign one or more categories from the taxonomy:

- data retrieval
- API interaction
- file manipulation
- database access
- code execution
- communication
- system operations
- developer tooling
- other

Return strict JSON:
{
  "categories": [...],
  "reasoning": "..."
}
"""


def classify_tool(name: str, desc: str, args: list) -> dict:
    user_content = f"Name: {name}\nDescription: {desc}\nArgs: {json.dumps(args)}"

    response = litellm.completion(
        model="openai/Llama 4 Scout",
        api_base="https://litellm.oit.duke.edu/v1",
        api_key=os.environ["LITELLM_TOKEN"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    parsed = ToolClassification(**json.loads(content))
    return parsed.model_dump()


def main():
    with open("skills_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_tools = [
        {**t, "_server": t.get("id", "unknown")}
        for t in data
        if t.get("description", "").strip()
    ]

    results = []
    processed = set()

    if os.path.exists("metadata_functionality-skills.json"):
        with open("metadata_functionality-skills.json", "r") as f:
            results = json.load(f)

        processed = {
            (t["server"], t["name"])
            for t in results
            if "server" in t and "name" in t
        }

    for tool in all_tools:
        key = (tool["_server"], tool["name"])
        if key in processed:
            continue

        for _ in range(5):
            try:
                res = classify_tool(
                    tool["name"],
                    tool["description"],
                    tool.get("args", []),
                )

                results.append({
                    "server": tool["_server"],
                    "name": tool["name"],
                    "categories": res["categories"],
                    "reasoning": res["reasoning"],
                })

                processed.add(key)
                time.sleep(0.5)
                break

            except Exception:
                time.sleep(10)
        else:
            results.append({
                "server": tool["_server"],
                "name": tool["name"],
                "categories": ["other"],
                "reasoning": "failed",
            })
            processed.add(key)

    with open("metadata_functionality-skills.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()