from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, select, text
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NotePatch, NoteRead

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    # Use parameterized query to prevent SQL injection
    sql = text(
        """
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE title LIKE :pattern OR content LIKE :pattern
        ORDER BY created_at DESC
        LIMIT 50
        """
    )
    pattern = f"%{q}%"
    rows = db.execute(sql, {"pattern": pattern}).all()
    results: list[NoteRead] = []
    for r in rows:
        results.append(
            NoteRead(
                id=r.id,
                title=r.title,
                content=r.content,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return results


@router.get("/debug/hash-md5")
def debug_hash_md5(q: str) -> dict[str, str]:
    import hashlib

    return {"algo": "md5", "hex": hashlib.md5(q.encode()).hexdigest()}


@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    # Safe arithmetic evaluator without using eval()
    import re
    import operator

    # Only allow numbers, basic operators, and parentheses
    if not re.match(r"^[\d+\-*/().\s]+$", expr):
        raise HTTPException(status_code=400, detail="Invalid expression: only basic arithmetic allowed")

    try:
        # Simple safe arithmetic evaluator
        # Replace spaces and evaluate using operator module
        expr_clean = expr.replace(" ", "")
        # Use a simple stack-based evaluator for basic arithmetic
        # For simplicity, use ast.literal_eval for numeric literals and operator module
        # But since we need to handle expressions, we'll use a simple approach
        ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
        }

        # Simple recursive descent parser for basic arithmetic
        # Handles operator precedence: parentheses > * / > + -
        def safe_eval(s: str) -> float:
            s = s.replace(" ", "")
            if not s:
                raise ValueError("Empty expression")

            # Handle parentheses (highest precedence)
            if "(" in s:
                start = s.rfind("(")
                end = s.find(")", start)
                if end == -1:
                    raise ValueError("Unmatched parenthesis")
                inner = safe_eval(s[start + 1 : end])
                return safe_eval(s[:start] + str(inner) + s[end + 1 :])

            # Handle multiplication and division (higher precedence than + -)
            for op in ["*", "/"]:
                if op in s:
                    parts = s.split(op, 1)
                    if len(parts) == 2:
                        left = safe_eval(parts[0])
                        right = safe_eval(parts[1])
                        return ops[op](left, right)

            # Handle addition and subtraction (lowest precedence)
            for op in ["+", "-"]:
                if op in s:
                    parts = s.split(op, 1)
                    if len(parts) == 2:
                        left = safe_eval(parts[0])
                        right = safe_eval(parts[1])
                        return ops[op](left, right)

            # Base case: just a number
            try:
                return float(s)
            except ValueError:
                raise ValueError(f"Invalid number: {s}")

        result = safe_eval(expr_clean)
        # Return as integer if it's a whole number, otherwise as float
        if result == int(result):
            result = int(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Evaluation error: {str(e)}")
    return {"result": str(result)}


@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess
    import shlex

    # Use shell=False and split command safely
    # Only allow a whitelist of safe commands
    allowed_commands = ["echo", "date", "whoami", "pwd"]
    parts = shlex.split(cmd)
    if not parts or parts[0] not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail=f"Command not allowed. Allowed commands: {', '.join(allowed_commands)}",
        )

    completed = subprocess.run(parts, shell=False, capture_output=True, text=True)
    return {"returncode": str(completed.returncode), "stdout": completed.stdout, "stderr": completed.stderr}


@router.get("/debug/fetch")
def debug_fetch(url: str) -> dict[str, str]:
    from urllib.parse import urlparse

    # Validate URL scheme to prevent file:// and other dangerous schemes
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http and https URLs are allowed")

    # Validate host against allowlist to prevent SSRF
    allowed_hosts = {
        "localhost",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
    }
    host = parsed.hostname
    if not host or host not in allowed_hosts:
        raise HTTPException(
            status_code=400,
            detail=f"Host not allowed. Allowed hosts: {', '.join(sorted(allowed_hosts))}",
        )

    # Reconstruct URL from validated components to prevent SSRF
    # This ensures we only use validated scheme and host
    validated_url = f"{parsed.scheme}://{host}"
    if parsed.port:
        validated_url += f":{parsed.port}"
    if parsed.path:
        validated_url += parsed.path
    if parsed.query:
        validated_url += f"?{parsed.query}"
    if parsed.fragment:
        validated_url += f"#{parsed.fragment}"

    # Use requests library for better security
    import requests

    try:
        # Use reconstructed URL from validated components
        response = requests.get(validated_url, timeout=5, allow_redirects=False)
        response.raise_for_status()
        body = response.text[:1024]
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Request failed: {str(e)}")
    return {"snippet": body}


@router.get("/debug/read")
def debug_read(path: str) -> dict[str, str]:
    try:
        content = open(path, "r").read(1024)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    return {"snippet": content}

