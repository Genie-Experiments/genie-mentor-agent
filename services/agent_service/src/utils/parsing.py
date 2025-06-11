import json
import re
from typing import Any, Dict, List


def extract_json_with_regex(text: str) -> dict:
    match = re.search(r"""```json\s*(\{.*?\})\s*```""", text, re.DOTALL)
    if not match:
        match = re.search(r"""(\{.*?\})""", text, re.DOTALL)

    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nRaw text:\n{json_str}")
    else:
        raise ValueError("No JSON object found")


def extract_json_with_brace_counting(text: str) -> dict:
    """Extract JSON by finding balanced braces - works well for nested JSON"""
    start_idx = text.find("{")
    if start_idx == -1:
        raise ValueError("No JSON object found")

    brace_count = 0
    end_idx = start_idx

    for i, char in enumerate(text[start_idx:], start_idx):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1

        if brace_count == 0:
            end_idx = i
            break

    if brace_count != 0:
        raise ValueError("Unbalanced braces in JSON")

    json_str = text[start_idx : end_idx + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def safe_json_parse(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw_content": content}


def extract_all_sources_from_plan(plan_data: Any) -> List[str]:
    """
    Recursively extracts all 'source' values from a nested plan data structure.
    """
    all_sources = []

    if isinstance(plan_data, dict):
        # Check for 'source' or 'sources' directly in the current dict
        if "source" in plan_data:
            all_sources.append(str(plan_data["source"]))
        if "sources" in plan_data:
            if isinstance(plan_data["sources"], list):
                all_sources.extend([str(s) for s in plan_data["sources"]])
            else:
                all_sources.append(str(plan_data["sources"]))

        # Recursively search in values of the dictionary
        for value in plan_data.values():
            all_sources.extend(extract_all_sources_from_plan(value))

    elif isinstance(plan_data, list):
        # Recursively search in items of the list
        for item in plan_data:
            all_sources.extend(extract_all_sources_from_plan(item))

    return all_sources
