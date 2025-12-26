def extract_action_items(text: str) -> list[str]:
    """Extract potential action items from a block of text.

    Heuristics:
    - Lines starting with ``todo:`` or ``action:`` (case-insensitive)
    - Lines containing the words "todo" or "action item" anywhere
    - Lines ending with an exclamation mark, which often indicates emphasis
    """

    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[str] = []
    for line in lines:
        normalized = line.lower()

        # Explicit markers at the beginning of the line
        if normalized.startswith("todo:") or normalized.startswith("action:"):
            results.append(line)

        # Action-style wording appearing anywhere in the line
        elif "todo" in normalized or "action item" in normalized:
            results.append(line)

        # Emphatic lines often represent action items (e.g. "Ship this by Friday!")
        elif line.endswith("!"):
            results.append(line)

    return results
