"""Notes router with proper schemas and error handling."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..exceptions import DatabaseError, NotFoundError
from ..schemas import NoteCreate, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(note: NoteCreate) -> NoteResponse:
    """Create a new note.
    
    Args:
        note: Note creation request.
        
    Returns:
        Created note.
        
    Raises:
        HTTPException: If creation fails.
    """
    try:
        created_note = db.note_repository.create(note.content)
        return NoteResponse(
            id=created_note.id,
            content=created_note.content,
            created_at=created_note.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Get a single note by ID.
    
    Args:
        note_id: Note identifier.
        
    Returns:
        Note object.
        
    Raises:
        HTTPException: If note not found or query fails.
    """
    try:
        note = db.note_repository.get_by_id(note_id)
        return NoteResponse(
            id=note.id,
            content=note.content,
            created_at=note.created_at
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[NoteResponse])
def list_all_notes() -> List[NoteResponse]:
    """List all notes.
    
    Returns:
        List of all notes.
        
    Raises:
        HTTPException: If query fails.
    """
    try:
        notes = db.note_repository.list_all()
        return [
            NoteResponse(
                id=note.id,
                content=note.content,
                created_at=note.created_at
            )
            for note in notes
        ]
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


