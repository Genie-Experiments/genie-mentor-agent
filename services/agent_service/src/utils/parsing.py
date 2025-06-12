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
    # Try to find a JSON object that starts with '{"' to avoid false positives
    # in code snippets with unrelated braces
    json_starts1 = [i for i, char in enumerate(text) if i < len(text)-1 and text[i:i+2] == '{\''] 
    json_starts2 = [i for i, char in enumerate(text) if i < len(text)-1 and text[i:i+2] == '{"']
    potential_starts = json_starts1 + json_starts2
    
    if not potential_starts:
        # Fallback to just looking for opening braces
        start_idx = text.find("{")
        if start_idx == -1:
            raise ValueError("No JSON object found")
        potential_starts = [start_idx]
    
    # Try each potential starting point
    for start_idx in potential_starts:
        try:
            brace_count = 0
            end_idx = start_idx
            in_string = False
            escape_next = False
            
            for i, char in enumerate(text[start_idx:], start_idx):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string:  # Only count braces outside of strings
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                
                if brace_count == 0 and i > start_idx:  # Found a complete object
                    end_idx = i
                    break
            
            if brace_count != 0:
                continue  # Try next potential start if this one had unbalanced braces
                
            json_str = text[start_idx : end_idx + 1]
            # Try to parse and return if successful
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            continue  # Try next potential start
    
    # If we get here, no valid JSON was found
    try:
        # One last attempt with regex to find the most promising JSON-like structure
        return extract_json_with_regex(text)
    except:
        # If all else fails, try a more lenient approach with regex cleanup
        # Find the largest {...} block and clean it up
        matches = re.findall(r'\{[^{}]*((\{[^{}]*\})[^{}]*)*\}', text, re.DOTALL)
        if matches:
            largest_match = max(matches, key=lambda x: len(x[0]) if isinstance(x, tuple) else len(x))
            json_candidate = largest_match[0] if isinstance(largest_match, tuple) else largest_match
            try:
                return json.loads(json_candidate)
            except:
                pass
        
        raise ValueError("Could not extract valid JSON - unbalanced braces or invalid format")


def safe_json_parse(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try the more robust extraction methods before giving up
        try:
            return extract_json_with_brace_counting(content)
        except Exception:
            try:
                return extract_json_with_regex(content)
            except Exception:
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
