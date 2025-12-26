import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """
    Extract hashtags from text and return them as a deduplicated list.

    Args:
        text: The input text to extract tags from

    Returns:
        A list of unique tags without the '#' prefix
    """
    # Pattern: # followed by a letter, then any combination of letters, numbers, hyphens, or underscores
    pattern = r"#([a-zA-Z][a-zA-Z0-9_-]*)"
    matches = re.findall(pattern, text)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for tag in matches:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result
