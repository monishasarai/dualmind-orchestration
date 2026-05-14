"""
JSON Fixer Module — DualMind v3
Robust extraction and repair of JSON from LLM responses.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Core extraction ────────────────────────────────────────────────────────────

def extract_json_str(text: str) -> str:
    """
    Extract the first valid JSON object from any LLM response text.
    Handles: leading spaces, markdown fences, prose before/after JSON.
    """
    if not text:
        raise ValueError("Empty response")

    text = text.strip()

    # 1. Direct parse (model returned clean JSON)
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences  ```json ... ``` or ``` ... ```
    fenced = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
    fenced = re.sub(r'\n?```\s*$', '', fenced).strip()
    try:
        json.loads(fenced)
        return fenced
    except json.JSONDecodeError:
        pass

    # 3. Brace-counting extraction (most reliable for embedded JSON)
    start = text.find('{')
    if start != -1:
        depth = 0
        for i in range(start, len(text)):
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        # Try fixing common issues then retry
                        fixed = _repair(candidate)
                        try:
                            json.loads(fixed)
                            return fixed
                        except json.JSONDecodeError:
                            break

    # 4. Greedy regex fallback
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        candidate = m.group(0)
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            fixed = _repair(candidate)
            try:
                json.loads(fixed)
                return fixed
            except json.JSONDecodeError:
                pass

    sample = text[:300]
    raise ValueError(f"Could not extract valid JSON. Sample: {sample}...")


def _repair(s: str) -> str:
    """Apply common JSON repairs."""
    # Trailing commas before } or ]
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    # Python booleans / None
    s = re.sub(r'\bTrue\b',  'true',  s)
    s = re.sub(r'\bFalse\b', 'false', s)
    s = re.sub(r'\bNone\b',  'null',  s)
    # Single-quoted keys/values
    s = re.sub(r"(?<![\\])'([^']*)'(\s*:)", r'"\1"\2', s)
    s = re.sub(r":\s*'([^']*)'", r': "\1"', s)
    # Unquoted keys
    s = re.sub(r'([{,]\s*)([A-Za-z_]\w*)(\s*:)', r'\1"\2"\3', s)
    return s


# ── Public API ─────────────────────────────────────────────────────────────────

def parse_llm_json(response: str, expected_keys: List[str] = None) -> Dict[str, Any]:
    """
    Parse JSON from an LLM response, filling in defaults for missing keys.
    Never raises on missing keys — always returns a usable dict.
    """
    json_str = extract_json_str(response)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error("JSON parse failed after extraction: %s", e)
        raise ValueError(f"Invalid JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object, got {type(data).__name__}")

    # Fill defaults for any missing expected keys
    if expected_keys:
        defaults: Dict[str, Any] = {
            "query":            "",
            "reasoning":        "No reasoning provided",
            "pipeline":         [],
            "final_output":     "No output specified",
            "overall_approval": False,
            "score":            50,
            "issues":           [],
            "suggestions":      [],
            "improvements":     [],
            "reasoning":        "No reasoning provided",
        }
        for key in expected_keys:
            if key not in data:
                data[key] = defaults.get(key, "")
                logger.debug("Added default for missing key: %s", key)

    return data


# ── Validators ─────────────────────────────────────────────────────────────────

def validate_plan_json(data: Dict[str, Any]) -> bool:
    if not all(k in data for k in ("query", "reasoning", "pipeline", "final_output")):
        return False
    if not isinstance(data.get("pipeline"), list):
        return False
    for step in data["pipeline"]:
        if not isinstance(step, dict):
            return False
        if "tool" not in step:
            return False
    return True


def validate_verification_json(data: Dict[str, Any]) -> bool:
    required = ("overall_approval", "score", "issues", "suggestions", "improvements")
    if not all(k in data for k in required):
        return False
    if not isinstance(data.get("overall_approval"), bool):
        return False
    if not isinstance(data.get("score"), (int, float)):
        return False
    return True


# Keep old name for backward compat
def fix_json_string(s: str) -> str:
    return _repair(s)


def extract_and_fix_json(response: str) -> str:
    return extract_json_str(response)
