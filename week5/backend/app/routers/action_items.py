from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..api_utils import success_envelope
from ..db import get_db
from ..models import ActionItem
from ..schemas import ActionItemCreate, ActionItemRead

router = APIRouter(prefix="/action-items", tags=["action_items"])

MAX_PAGE_SIZE = 100


@router.get("/")
def list_items(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> dict:
    effective_page_size = min(page_size, MAX_PAGE_SIZE)
    total = db.scalar(select(func.count()).select_from(ActionItem)) or 0
    rows = (
        db.execute(
            select(ActionItem)
            .order_by(ActionItem.id)
            .offset((page - 1) * effective_page_size)
            .limit(effective_page_size)
        )
        .scalars()
        .all()
    )
    items = [ActionItemRead.model_validate(row) for row in rows]
    return success_envelope(
        {
            "items": items,
            "total": total,
            "page": page,
            "page_size": effective_page_size,
        }
    )


@router.post("/", status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> dict:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return success_envelope(ActionItemRead.model_validate(item))


@router.put("/{item_id}/complete")
def complete_item(item_id: int, db: Session = Depends(get_db)) -> dict:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return success_envelope(ActionItemRead.model_validate(item))
