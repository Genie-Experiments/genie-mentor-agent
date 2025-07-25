import json
import re
from typing import Any, Dict, List, Optional, Tuple


def strip_markdown_code_fence(text: str) -> str:
    """Remove leading/trailing triple backticks and optional 'json' label from a string."""
    # Remove leading/trailing code fences and optional 'json' after opening
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)


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


def extract_github_metadata(text: str) -> Dict[str, Any]:
    """
    Extract GitHub repository information from text content.
    Returns metadata including repository links and repository names.
    """
    repo_links = []
    repo_names = []
    
    # Extract GitHub URLs
    github_urls = re.findall(r'https?://github\.com/[^\s"\'\)]+', text)
    
    for url in github_urls:
        # Clean the URL in case it has trailing punctuation
        url = re.sub(r'[.,;:"\']$', '', url)
        repo_links.append(url)
        
        # Extract repo name from URL
        match = re.search(r'github\.com/[^/]+/([^/\s"\'\)]+)', url)
        if match:
            repo_names.append(match.group(1))
    
    return {
        "repo_links": repo_links,
        "repo_names": repo_names
    }


def parse_source_response(text: str) -> Dict[str, Any]:
    """
    Process response text to extract meaningful content and metadata.
    Handles detection of GitHub content.
    Returns parsed data with source-specific metadata.
    """
    try:
        # First try to parse as normal JSON
        parsed_json = json.loads(text)
        
        # Check if the answer field itself contains nested JSON
        if isinstance(parsed_json, dict) and "answer" in parsed_json:
            answer_text = parsed_json["answer"]
            if isinstance(answer_text, str) and (answer_text.strip().startswith('{') or answer_text.strip().startswith('[')):
                try:
                    # Try to parse the inner JSON
                    inner_json = json.loads(answer_text)
                    if isinstance(inner_json, dict):
                        # If inner JSON has answer field, extract it directly
                        if "answer" in inner_json:
                            parsed_json["answer"] = inner_json["answer"]
                            # Merge metadata if present
                            if "metadata" in inner_json and isinstance(parsed_json.get("metadata"), list):
                                parsed_json["metadata"].extend(inner_json["metadata"])
                except json.JSONDecodeError:
                    # If inner parsing fails, keep original answer text
                    pass
        
        # Ensure 'answer' and 'metadata' keys always exist
        if not isinstance(parsed_json, dict):
            parsed_json = {"answer": str(parsed_json), "metadata": []}
        if 'answer' not in parsed_json:
            parsed_json['answer'] = 'Error parsing agent response'
        if 'metadata' not in parsed_json:
            parsed_json['metadata'] = []
        
        # Sanitize strings to remove unescaped control characters
        for key, value in parsed_json.items():
            if isinstance(value, str):
                parsed_json[key] = ''.join(c for c in value if c.isprintable())
        
        return parsed_json
    except json.JSONDecodeError:
        # Next try the brace counting method
        try:
            parsed_json = extract_json_with_brace_counting(text)
            
            # Apply the same nested JSON check as above
            if isinstance(parsed_json, dict) and "answer" in parsed_json:
                answer_text = parsed_json["answer"]
                if isinstance(answer_text, str) and (answer_text.strip().startswith('{') or answer_text.strip().startswith('[')):
                    try:
                        inner_json = json.loads(answer_text)
                        if isinstance(inner_json, dict):
                            if "answer" in inner_json:
                                parsed_json["answer"] = inner_json["answer"]
                                if "metadata" in inner_json and isinstance(parsed_json.get("metadata"), list):
                                    parsed_json["metadata"].extend(inner_json["metadata"])
                    except json.JSONDecodeError:
                        pass
                        
            # Ensure 'answer' and 'metadata' keys always exist
            if not isinstance(parsed_json, dict):
                parsed_json = {"answer": str(parsed_json), "metadata": []}
            if 'answer' not in parsed_json:
                parsed_json['answer'] = ''
            if 'metadata' not in parsed_json:
                parsed_json['metadata'] = []
            
            # Sanitize strings to remove unescaped control characters
            for key, value in parsed_json.items():
                if isinstance(value, str):
                    parsed_json[key] = ''.join(c for c in value if c.isprintable())
            
            return parsed_json
            
        except ValueError:
            # Check if it contains GitHub links
            has_github = "github.com" in text
            
            result = {"answer": text, "metadata": [], "error": ""}
            
            # Extract and add GitHub metadata if present
            if has_github:
                result["metadata"].extend(extract_github_metadata(text))
                
            # Sanitize strings to remove unescaped control characters
            for key, value in result.items():
                if isinstance(value, str):
                    result[key] = ''.join(c for c in value if c.isprintable())
            
            return result


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


def escape_unescaped_newlines_in_json_strings(text: str) -> str:
    """Escape unescaped newlines inside double-quoted JSON string values with \\n."""
    def replacer(match):
        s = match.group(1)
        # Escape newlines
        s = s.replace('\n', '\\n').replace('\x0a', '\\n')
        # List of unwanted chars to remove
        unwanted = ['\r', '\u2028', '\u2029', '\x0b', '\x0c', '\x1c', '\x1d', '\x1e', '\x85', '\x0d']
        for ch in unwanted:
            s = s.replace(ch, '')
        return '"' + s + '"'
    # Only operate inside double quotes
    return re.sub(r'"(.*?)"', replacer, text, flags=re.DOTALL)
