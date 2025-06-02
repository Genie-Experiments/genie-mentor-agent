import json
import re

def _extract_json_with_regex(text: str) -> dict:
    match = re.search(r'\{(?:[^{}]|(?R))*\}', text)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
    else:
        raise ValueError("No JSON object found")