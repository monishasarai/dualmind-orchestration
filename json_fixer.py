"""
JSON Fixer Module
Repairs common JSON formatting issues from LLM responses.
"""

import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def fix_json_string(json_str: str) -> str:
    """
    Attempt to fix common JSON formatting issues.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Fixed JSON string
    """
    if not json_str:
        raise ValueError("Empty JSON string")
    
    # Strip whitespace
    json_str = json_str.strip()
    
    # Remove common LLM prefixes/suffixes
    json_str = re.sub(r'^(Here is|Here\'s|Sure|Certainly|Of course)[^\{]*', '', json_str, flags=re.IGNORECASE)
    json_str = re.sub(r'(Let me know|Hope this helps|Please|Thank you)[^\}]*$', '', json_str, flags=re.IGNORECASE)
    json_str = json_str.strip()
    
    # Remove markdown code blocks
    json_str = re.sub(r'^```(?:json)?\s*\n?', '', json_str)
    json_str = re.sub(r'\n?```\s*$', '', json_str)
    json_str = json_str.strip()
    
    # Fix common issues
    
    # 1. Fix trailing commas in objects/arrays
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # 2. Fix missing commas between array/object elements
    json_str = re.sub(r'(\}|\])\s*(\{|\[)', r'\1,\2', json_str)
    json_str = re.sub(r'("\w+"\s*:\s*"[^"]*")\s+(")', r'\1,\2', json_str)
    
    # 3. Fix single quotes to double quotes (for keys and string values)
    # Be careful not to replace quotes inside strings
    json_str = re.sub(r"(?<!\\)'([^']*)'(?=\s*:)", r'"\1"', json_str)  # Keys
    json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)  # Values
    
    # 4. Fix unquoted keys
    json_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
    
    # 5. Fix boolean values (ensure lowercase)
    json_str = re.sub(r'\bTrue\b', 'true', json_str)
    json_str = re.sub(r'\bFalse\b', 'false', json_str)
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    
    # 6. Fix escaped quotes that shouldn't be escaped
    json_str = json_str.replace('\\"', '"')
    
    # 7. Ensure string values are properly quoted
    # This is tricky and might need refinement
    
    return json_str


def extract_and_fix_json(response: str) -> str:
    """
    Extract JSON from LLM response and fix common issues.
    
    Args:
        response: LLM response text
        
    Returns:
        Fixed JSON string
        
    Raises:
        ValueError: If no valid JSON can be extracted
    """
    if not response:
        raise ValueError("Empty response")
    
    # First, try to fix the entire response
    try:
        fixed = fix_json_string(response)
        json.loads(fixed)  # Validate
        return fixed
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Try to find JSON between curly braces
    first_brace = response.find('{')
    last_brace = response.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        potential_json = response[first_brace:last_brace + 1]
        try:
            fixed = fix_json_string(potential_json)
            json.loads(fixed)  # Validate
            return fixed
        except (json.JSONDecodeError, ValueError):
            pass
    
    # Try to extract balanced braces
    if '{' in response:
        brace_count = 0
        start_idx = response.find('{')
        end_idx = start_idx
        
        for i in range(start_idx, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx > start_idx:
            potential_json = response[start_idx:end_idx]
            try:
                fixed = fix_json_string(potential_json)
                json.loads(fixed)  # Validate
                return fixed
            except (json.JSONDecodeError, ValueError):
                pass
    
    # If all else fails, raise error with sample
    sample = response[:200] if len(response) > 200 else response
    raise ValueError(f"Could not extract valid JSON. Sample: {sample}...")


def parse_llm_json(response: str, expected_keys: list = None) -> Dict[str, Any]:
    """
    Parse JSON from LLM response with validation and fixing.
    
    Args:
        response: LLM response text
        expected_keys: Optional list of keys that must be present
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON cannot be parsed or validated
    """
    # Extract and fix JSON
    json_str = extract_and_fix_json(response)
    
    # Parse
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON even after fixes: {e}")
        logger.debug(f"JSON string was: {json_str[:500]}")
        raise ValueError(f"Invalid JSON after fixes: {e}")
    
    # Validate expected keys
    if expected_keys:
        missing_keys = [key for key in expected_keys if key not in data]
        if missing_keys:
            logger.warning(f"Missing expected keys: {missing_keys}")
            # Add default values for missing keys
            defaults = {
                "query": "",
                "reasoning": "No reasoning provided",
                "pipeline": [],
                "final_output": "No output specified",
                "overall_approval": False,
                "score": 50,
                "issues": [],
                "suggestions": [],
                "improvements": []
            }
            for key in missing_keys:
                if key in defaults:
                    data[key] = defaults[key]
                    logger.info(f"Added default value for missing key: {key}")
    
    return data


def validate_plan_json(data: Dict[str, Any]) -> bool:
    """
    Validate that a plan JSON has the correct structure.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["query", "reasoning", "pipeline", "final_output"]
    
    # Check required keys
    if not all(key in data for key in required_keys):
        return False
    
    # Validate pipeline structure
    pipeline = data.get("pipeline", [])
    if not isinstance(pipeline, list):
        return False
    
    for step in pipeline:
        if not isinstance(step, dict):
            return False
        if not all(key in step for key in ["tool", "purpose", "input"]):
            return False
    
    return True


def validate_verification_json(data: Dict[str, Any]) -> bool:
    """
    Validate that a verification JSON has the correct structure.
    
    Args:
        data: Parsed JSON data
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["overall_approval", "score", "issues", "suggestions", "improvements"]
    
    # Check required keys
    if not all(key in data for key in required_keys):
        return False
    
    # Validate types
    if not isinstance(data["overall_approval"], bool):
        return False
    
    if not isinstance(data["score"], (int, float)):
        return False
    
    if not all(isinstance(data[key], list) for key in ["issues", "suggestions", "improvements"]):
        return False
    
    return True
