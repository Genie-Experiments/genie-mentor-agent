import json
import re
import json
import re

def _extract_json_with_regex(text: str) -> dict:
    match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if not match:
        match = re.search(r'(\{.*?\})', text, re.DOTALL)

    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}\nRaw text:\n{json_str}")
    else:
        raise ValueError("No JSON object found")
