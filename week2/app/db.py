"""Database layer with proper error handling and abstraction."""

from __future__ import annotations

import sqlite3
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional

from .config import get_settings
from .exceptions import DatabaseError, NotFoundError
from .models import ActionItem, Note

logger = logging.getLogger(__name__)


class Database:
    """Database connection and operation manager."""
    
    def __init__(self, db_path: Path):
        """Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_data_directory_exists()
    
    def _ensure_data_directory_exists(self) -> None:
        """Ensure the data directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with proper error handling.
        
        Yields:
            sqlite3.Connection: Database connection
            
        Raises:
            DatabaseError: If connection fails.
        """
        try:
            connection = sqlite3.connect(str(self.db_path))
            connection.row_factory = sqlite3.Row
            try:
                yield connection
                connection.commit()
            except Exception as e:
                connection.rollback()
                logger.error(f"Database operation failed: {e}", exc_info=True)
                raise DatabaseError(f"Database operation failed: {e}") from e
            finally:
                connection.close()
        except sqlite3.Error as e:
            logger.error(f"Database connection failed: {e}", exc_info=True)
            raise DatabaseError(f"Failed to connect to database: {e}") from e
    
    def init_db(self) -> None:
        """Initialize database schema."""
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        created_at TEXT DEFAULT (datetime('now'))
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS action_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        note_id INTEGER,
                        text TEXT NOT NULL,
                        done INTEGER DEFAULT 0,
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (note_id) REFERENCES notes(id)
                    );
                    """
                )
                connection.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise DatabaseError(f"Failed to initialize database: {e}") from e


class NoteRepository:
    """Repository for note operations."""
    
    def __init__(self, db: Database):
        """Initialize note repository.
        
        Args:
            db: Database instance.
        """
        self.db = db
    
    def create(self, content: str) -> Note:
        """Create a new note.
        
        Args:
            content: Note content.
            
        Returns:
            Created Note object.
            
        Raises:
            DatabaseError: If creation fails.
        """
        if not content or not content.strip():
            raise ValueError("Note content cannot be empty")
        
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO notes (content) VALUES (?)",
                    (content.strip(),)
                )
                note_id = int(cursor.lastrowid)
                connection.commit()
                
                # Fetch the created note
                return self.get_by_id(note_id)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to create note: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create note: {e}") from e
    
    def get_by_id(self, note_id: int) -> Note:
        """Get a note by ID.
        
        Args:
            note_id: Note identifier.
            
        Returns:
            Note object.
            
        Raises:
            NotFoundError: If note doesn't exist.
            DatabaseError: If query fails.
        """
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id, content, created_at FROM notes WHERE id = ?",
                    (note_id,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    raise NotFoundError(f"Note with id {note_id} not found")
                
                return Note.from_row(row)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get note {note_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to get note: {e}") from e
    
    def list_all(self) -> List[Note]:
        """List all notes.
        
        Returns:
            List of Note objects.
            
        Raises:
            DatabaseError: If query fails.
        """
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id, content, created_at FROM notes ORDER BY id DESC"
                )
                rows = cursor.fetchall()
                return [Note.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list notes: {e}", exc_info=True)
            raise DatabaseError(f"Failed to list notes: {e}") from e


class ActionItemRepository:
    """Repository for action item operations."""
    
    def __init__(self, db: Database):
        """Initialize action item repository.
        
        Args:
            db: Database instance.
        """
        self.db = db
    
    def create_many(self, items: List[str], note_id: Optional[int] = None) -> List[ActionItem]:
        """Create multiple action items.
        
        Args:
            items: List of action item texts.
            note_id: Optional note ID to associate with items.
            
        Returns:
            List of created ActionItem objects.
            
        Raises:
            DatabaseError: If creation fails.
        """
        if not items:
            return []
        
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                created_items = []
                
                for item in items:
                    if not item or not item.strip():
                        continue
                    cursor.execute(
                        "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                        (note_id, item.strip())
                    )
                    item_id = int(cursor.lastrowid)
                    created_items.append(item_id)
                
                connection.commit()
                
                # Fetch all created items
                return [self.get_by_id(item_id) for item_id in created_items]
        except Exception as e:
            logger.error(f"Failed to create action items: {e}", exc_info=True)
            raise DatabaseError(f"Failed to create action items: {e}") from e
    
    def get_by_id(self, action_item_id: int) -> ActionItem:
        """Get an action item by ID.
        
        Args:
            action_item_id: Action item identifier.
            
        Returns:
            ActionItem object.
            
        Raises:
            NotFoundError: If action item doesn't exist.
            DatabaseError: If query fails.
        """
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                    (action_item_id,)
                )
                row = cursor.fetchone()
                
                if row is None:
                    raise NotFoundError(f"Action item with id {action_item_id} not found")
                
                return ActionItem.from_row(row)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get action item {action_item_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to get action item: {e}") from e
    
    def list_all(self, note_id: Optional[int] = None) -> List[ActionItem]:
        """List all action items, optionally filtered by note_id.
        
        Args:
            note_id: Optional note ID to filter by.
            
        Returns:
            List of ActionItem objects.
            
        Raises:
            DatabaseError: If query fails.
        """
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                if note_id is None:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                    )
                else:
                    cursor.execute(
                        "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                        (note_id,)
                    )
                rows = cursor.fetchall()
                return [ActionItem.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list action items: {e}", exc_info=True)
            raise DatabaseError(f"Failed to list action items: {e}") from e
    
    def update_done_status(self, action_item_id: int, done: bool) -> ActionItem:
        """Update the done status of an action item.
        
        Args:
            action_item_id: Action item identifier.
            done: Whether the item is done.
            
        Returns:
            Updated ActionItem object.
            
        Raises:
            NotFoundError: If action item doesn't exist.
            DatabaseError: If update fails.
        """
        try:
            # Verify item exists
            self.get_by_id(action_item_id)
            
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE action_items SET done = ? WHERE id = ?",
                    (1 if done else 0, action_item_id)
                )
                connection.commit()
                
                return self.get_by_id(action_item_id)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update action item {action_item_id}: {e}", exc_info=True)
            raise DatabaseError(f"Failed to update action item: {e}") from e


# Global database instance
_settings = get_settings()
_database = Database(_settings.database_path)
note_repository = NoteRepository(_database)
action_item_repository = ActionItemRepository(_database)


def init_db() -> None:
    """Initialize the database schema."""
    _database.init_db()


# Backward compatibility functions (deprecated, use repositories directly)
def insert_note(content: str) -> int:
    """Insert a note (backward compatibility).
    
    Deprecated: Use note_repository.create() instead.
    """
    note = note_repository.create(content)
    return note.id


def get_note(note_id: int):
    """Get a note (backward compatibility).
    
    Deprecated: Use note_repository.get_by_id() instead.
    """
    note = note_repository.get_by_id(note_id)
    return {
        "id": note.id,
        "content": note.content,
        "created_at": note.created_at
    }


def list_notes():
    """List all notes (backward compatibility).
    
    Deprecated: Use note_repository.list_all() instead.
    """
    notes = note_repository.list_all()
    return [
        {
            "id": note.id,
            "content": note.content,
            "created_at": note.created_at
        }
        for note in notes
    ]


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    """Insert action items (backward compatibility).
    
    Deprecated: Use action_item_repository.create_many() instead.
    """
    action_items = action_item_repository.create_many(items, note_id)
    return [item.id for item in action_items]


def list_action_items(note_id: Optional[int] = None):
    """List action items (backward compatibility).
    
    Deprecated: Use action_item_repository.list_all() instead.
    """
    items = action_item_repository.list_all(note_id)
    return [
        {
            "id": item.id,
            "note_id": item.note_id,
            "text": item.text,
            "done": item.done,
            "created_at": item.created_at
        }
        for item in items
    ]


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """Mark action item as done (backward compatibility).
    
    Deprecated: Use action_item_repository.update_done_status() instead.
    """
    action_item_repository.update_done_status(action_item_id, done)


