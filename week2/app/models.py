"""Database models and data classes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Note:
    """Note model."""
    id: int
    content: str
    created_at: str

    @classmethod
    def from_row(cls, row) -> Note:
        """Create Note from database row."""
        return cls(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"]
        )


@dataclass
class ActionItem:
    """Action item model."""
    id: int
    text: str
    note_id: Optional[int]
    done: bool
    created_at: str

    @classmethod
    def from_row(cls, row) -> ActionItem:
        """Create ActionItem from database row."""
        return cls(
            id=row["id"],
            text=row["text"],
            note_id=row["note_id"],
            done=bool(row["done"]),
            created_at=row["created_at"]
        )

