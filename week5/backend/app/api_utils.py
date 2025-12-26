from typing import Any


def success_envelope(data: Any) -> dict[str, Any]:
    """Standard success response envelope.

    Shape: {"ok": True, "data": ...}
    """

    return {"ok": True, "data": data}
