"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Note Schemas
class NoteBase(BaseModel):
    """Base schema for note data."""
    content: str = Field(..., min_length=1, description="The note content")


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass


class NoteResponse(NoteBase):
    """Schema for note response."""
    id: int = Field(..., description="Unique note identifier")
    created_at: str = Field(..., description="ISO timestamp when note was created")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "content": "Meeting notes from today",
                "created_at": "2024-01-15T10:30:00"
            }
        }


# Action Item Schemas
class ActionItemBase(BaseModel):
    """Base schema for action item data."""
    text: str = Field(..., min_length=1, description="The action item text")


class ActionItemResponse(BaseModel):
    """Schema for action item response."""
    id: int = Field(..., description="Unique action item identifier")
    note_id: Optional[int] = Field(None, description="Associated note ID if applicable")
    text: str = Field(..., description="The action item text")
    done: bool = Field(..., description="Whether the action item is completed")
    created_at: str = Field(..., description="ISO timestamp when action item was created")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "note_id": 1,
                "text": "Set up database",
                "done": False,
                "created_at": "2024-01-15T10:30:00"
            }
        }


class ActionItemUpdate(BaseModel):
    """Schema for updating an action item."""
    done: bool = Field(..., description="Whether the action item is completed")


# Extraction Schemas
class ExtractRequest(BaseModel):
    """Schema for action item extraction request."""
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(False, description="Whether to save the input text as a note")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "- [ ] Set up database\n* implement API endpoint",
                "save_note": True
            }
        }


class ExtractResponse(BaseModel):
    """Schema for action item extraction response."""
    note_id: Optional[int] = Field(None, description="ID of created note if save_note was True")
    items: List[ActionItemResponse] = Field(..., description="List of extracted action items")

    class Config:
        json_schema_extra = {
            "example": {
                "note_id": 1,
                "items": [
                    {"id": 1, "note_id": 1, "text": "Set up database", "done": False, "created_at": "2024-01-15T10:30:00"},
                    {"id": 2, "note_id": 1, "text": "implement API endpoint", "done": False, "created_at": "2024-01-15T10:30:00"}
                ]
            }
        }

