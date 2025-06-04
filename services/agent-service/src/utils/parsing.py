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
    

def extract_json_with_brace_counting(text: str) -> dict:
    """Extract JSON by finding balanced braces - works well for nested JSON"""
    start_idx = text.find('{')
    if start_idx == -1:
        raise ValueError("No JSON object found")
    
    brace_count = 0
    end_idx = start_idx
    
    for i, char in enumerate(text[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            
        if brace_count == 0:
            end_idx = i
            break
    
    if brace_count != 0:
        raise ValueError("Unbalanced braces in JSON")
    
    json_str = text[start_idx:end_idx + 1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")