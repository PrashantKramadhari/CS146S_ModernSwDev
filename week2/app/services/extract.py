from __future__ import annotations

import json
import logging
import re
from typing import List

try:
    from ollama import chat
    from ollama._types import ResponseError
except ImportError:
    # Fallback if ollama is not installed
    ResponseError = Exception
    chat = None

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def extract_action_items_llm(text: str) -> List[str]:
    """
    Extract action items from text using an LLM via Ollama.
    
    This function uses Ollama's structured output feature to extract action items
    from free-form text. It identifies tasks, todos, and actionable items using
    a large language model.
    
    Args:
        text: The input text from which to extract action items.
        
    Returns:
        A list of extracted action items as strings. Returns empty list if
        extraction fails or if no action items are found.
    """
    if not text or not text.strip():
        return []
    
    # Get the model name from settings
    model_name = settings.ollama_model
    
    # Define the JSON schema for structured output
    json_schema = {
        "type": "object",
        "properties": {
            "action_items": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of extracted action items"
            }
        },
        "required": ["action_items"]
    }
    
    # Create the prompt for action item extraction
    prompt = f"""Extract all action items, tasks, and todos from the following text.
An action item is any task that needs to be completed, such as:
- Items prefixed with "todo:", "action:", "next:"
- Bullet points with tasks
- Checkbox items like "[ ] task"
- Imperative sentences that describe something to do
- Any explicit task or assignment mentioned

Return only the action items, cleaned of prefixes and markers (like "-", "*", "[ ]", etc.).
Do not include narrative text or non-actionable content.

Text to analyze:
{text}

Extract and return all action items as a JSON array of strings."""
    
    try:
        # Call Ollama with structured output
        response = chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format=json_schema
        )
        
        # Extract the content from the response
        content = response.get("message", {}).get("content", "")
        
        if not content:
            # Fallback to heuristic-based extraction if LLM returns empty
            return extract_action_items(text)
        
        # Parse the JSON response
        parsed = json.loads(content)
        action_items = parsed.get("action_items", [])
        
        # Validate and clean the results
        cleaned_items: List[str] = []
        for item in action_items:
            if isinstance(item, str) and item.strip():
                cleaned_items.append(item.strip())
        
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: List[str] = []
        for item in cleaned_items:
            lowered = item.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(item)
        
        return unique
        
    except ResponseError as e:
        # Handle Ollama-specific errors (e.g., model not found)
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg:
            logger.error(
                f"Ollama model '{model_name}' not found. "
                f"Please ensure the model is installed by running: ollama pull {model_name}"
            )
        else:
            logger.error(f"Ollama error: {e}")
        # Fallback to heuristic-based extraction
        return extract_action_items(text)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        # Fallback to heuristic-based extraction if JSON parsing fails
        logger.warning(f"Failed to parse LLM response as JSON: {e}")
        return extract_action_items(text)
    except Exception as e:
        # Fallback to heuristic-based extraction if LLM call fails
        logger.error(f"LLM extraction failed: {e}", exc_info=True)
        return extract_action_items(text)
