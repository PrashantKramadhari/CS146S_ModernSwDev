from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..api_utils import success_envelope
from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])

MAX_PAGE_SIZE = 100


@router.get("/")
def list_notes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> dict:
    effective_page_size = min(page_size, MAX_PAGE_SIZE)
    total = db.scalar(select(func.count()).select_from(Note)) or 0
    rows = (
        db.execute(
            select(Note)
            .order_by(Note.id)
            .offset((page - 1) * effective_page_size)
            .limit(effective_page_size)
        )
        .scalars()
        .all()
    )
    items = [NoteRead.model_validate(row) for row in rows]
    return success_envelope(
        {
            "items": items,
            "total": total,
            "page": page,
            "page_size": effective_page_size,
        }
    )


@router.post("/", status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> dict:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return success_envelope(NoteRead.model_validate(note))


@router.get("/search/")
def search_notes(q: Optional[str] = None, db: Session = Depends(get_db)) -> dict:
    if not q:
        rows = db.execute(select(Note)).scalars().all()
    else:
        ilike_pattern = f"%{q}%"
        rows = (
            db.execute(
                select(Note).where(
                    Note.title.ilike(ilike_pattern) | Note.content.ilike(ilike_pattern)
                )
            )
            .scalars()
            .all()
        )
    items = [NoteRead.model_validate(row) for row in rows]
    return success_envelope(items)


@router.get("/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)) -> dict:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return success_envelope(NoteRead.model_validate(note))
