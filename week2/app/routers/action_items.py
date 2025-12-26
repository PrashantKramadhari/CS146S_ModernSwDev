"""Action items router with proper schemas and error handling."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..exceptions import DatabaseError, NotFoundError
from ..schemas import ActionItemResponse, ActionItemUpdate, ExtractRequest, ExtractResponse
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse, status_code=200)
def extract(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using heuristic-based extraction.
    
    Args:
        request: Extraction request with text and optional save_note flag.
        
    Returns:
        ExtractResponse with extracted action items.
        
    Raises:
        HTTPException: If extraction or database operation fails.
    """
    try:
        note_id: Optional[int] = None
        if request.save_note:
            note = db.note_repository.create(request.text)
            note_id = note.id

        items = extract_action_items(request.text)
        action_items = db.action_item_repository.create_many(items, note_id=note_id)
        
        return ExtractResponse(
            note_id=note_id,
            items=[
                ActionItemResponse(
                    id=item.id,
                    note_id=item.note_id,
                    text=item.text,
                    done=item.done,
                    created_at=item.created_at
                )
                for item in action_items
            ]
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract action items: {str(e)}")


@router.post("/extract-llm", response_model=ExtractResponse, status_code=200)
def extract_llm(request: ExtractRequest) -> ExtractResponse:
    """Extract action items from text using LLM-powered extraction.
    
    Args:
        request: Extraction request with text and optional save_note flag.
        
    Returns:
        ExtractResponse with extracted action items.
        
    Raises:
        HTTPException: If extraction or database operation fails.
    """
    try:
        note_id: Optional[int] = None
        if request.save_note:
            note = db.note_repository.create(request.text)
            note_id = note.id

        items = extract_action_items_llm(request.text)
        action_items = db.action_item_repository.create_many(items, note_id=note_id)
        
        return ExtractResponse(
            note_id=note_id,
            items=[
                ActionItemResponse(
                    id=item.id,
                    note_id=item.note_id,
                    text=item.text,
                    done=item.done,
                    created_at=item.created_at
                )
                for item in action_items
            ]
        )
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract action items with LLM: {str(e)}")


@router.get("", response_model=List[ActionItemResponse])
def list_all(note_id: Optional[int] = Query(None, description="Filter by note ID")) -> List[ActionItemResponse]:
    """List all action items, optionally filtered by note_id.
    
    Args:
        note_id: Optional note ID to filter by.
        
    Returns:
        List of action items.
        
    Raises:
        HTTPException: If database query fails.
    """
    try:
        items = db.action_item_repository.list_all(note_id=note_id)
        return [
            ActionItemResponse(
                id=item.id,
                note_id=item.note_id,
                text=item.text,
                done=item.done,
                created_at=item.created_at
            )
            for item in items
        ]
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{action_item_id}/done", response_model=ActionItemResponse)
def mark_done(action_item_id: int, update: ActionItemUpdate) -> ActionItemResponse:
    """Update the done status of an action item.
    
    Args:
        action_item_id: Action item identifier.
        update: Update request with done status.
        
    Returns:
        Updated action item.
        
    Raises:
        HTTPException: If action item not found or update fails.
    """
    try:
        item = db.action_item_repository.update_done_status(action_item_id, update.done)
        return ActionItemResponse(
            id=item.id,
            note_id=item.note_id,
            text=item.text,
            done=item.done,
            created_at=item.created_at
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


